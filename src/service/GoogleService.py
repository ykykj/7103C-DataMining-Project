from __future__ import print_function
import os.path
import base64
import pickle
import json
from datetime import datetime
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from rich.console import Console
from rich.panel import Panel

from src.config import settings

console = Console()


class GoogleService:
    def __init__(self):
        # Gmail API scope for sending emails, events, calendar, drive
        self._SCOPES = settings.get_google_scopes()
        self._user_info = None  # 缓存用户信息
        self._creds = None  # 缓存认证凭证

    def sendEmail(self, to, subject, body):
        creds = self._get_credentials()
        service = build('gmail', 'v1', credentials=creds)
        user_info = self.get_user_info()
        message = self._create_message(sender=user_info['email'], to=to, subject=subject, message_text=body)
        self._send_message(service, "me", message)

    def searchEmail(self, query):
        creds = self._get_credentials()
        service = build('gmail', 'v1', credentials=creds)

        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])

        if not messages:
            print("No messages found.")
            return []

        emails = []

        for msg in messages:
            msg_id = msg['id']
            msg_data = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
            headers = msg_data['payload']['headers']

            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), '')

            # Decode body
            body = ""
            if 'parts' in msg_data['payload']:
                for part in msg_data['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        body = base64.urlsafe_b64decode(part['body'].get('data', '')).decode('utf-8')
            else:
                body = base64.urlsafe_b64decode(msg_data['payload']['body'].get('data', '')).decode('utf-8')

            # Get email date
            internal_timestamp = int(msg_data['internalDate'])  # milliseconds since epoch
            email_date = datetime.fromtimestamp(internal_timestamp / 1000)  # convert to datetime

            emails.append({
                'id': msg_id,
                'subject': subject,
                'sender': sender,
                'body': body,
                'date': email_date.strftime('%Y-%m-%d %H:%M:%S')  # readable format
            })

        return emails

    def createBookingEvent(self, summary : str, description : str, start_time : datetime, end_time : datetime, attendees_emails=None):
        """
        Creates a Google Calendar event.

        Parameters:
        - summary: str -> Event title
        - description: str -> Event details
        - start_time: datetime -> Event start
        - end_time: datetime -> Event end
        - attendees_emails: list -> List of attendee emails
        """
        creds = self._get_credentials()
        service = build('calendar', 'v3', credentials=creds)

        # Validate and filter attendee emails
        valid_attendees = []
        invalid_emails = []
        
        if attendees_emails:
            from email_validator import validate_email, EmailNotValidError
            
            for email in attendees_emails:
                if not isinstance(email, str):
                    invalid_emails.append(f"{email} (not a string)")
                    continue
                
                try:
                    # Validate email using email-validator library
                    validated = validate_email(email.strip(), check_deliverability=False)
                    valid_attendees.append({'email': validated.normalized})
                except EmailNotValidError as e:
                    invalid_emails.append(f"{email} ({str(e)})")

        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': settings.google_calendar_timezone,
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': settings.google_calendar_timezone,
            },
            'attendees': valid_attendees,
        }

        created_event = service.events().insert(calendarId='primary', body=event).execute()
        
        # Build result message with detailed information
        result = f"Event created successfully: {created_event.get('htmlLink')}\n"
        result += f"Title: {summary}\n"
        result += f"Time: {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')}"
        
        if valid_attendees:
            result += f"\n\nValid attendees ({len(valid_attendees)}):\n"
            result += "\n".join([f"  - {a['email']}" for a in valid_attendees])
        
        if invalid_emails:
            result += f"\n\nInvalid emails ({len(invalid_emails)}) - NOT added to event:\n"
            result += "\n".join([f"  - {email}" for email in invalid_emails])
            result += "\n\nPlease provide valid email addresses for these attendees."
        
        return result

    def getCalendarEvents(self, time_min: datetime, time_max: datetime, max_results: int = 10):
        """
        Retrieves calendar events within a specified time range.

        Parameters:
        - time_min: datetime -> Start of time range
        - time_max: datetime -> End of time range
        - max_results: int -> Maximum number of events to return (default: 10)

        Returns:
        - list: List of calendar events with details
        """
        import pytz
        creds = self._get_credentials()
        service = build('calendar', 'v3', credentials=creds)

        # Ensure datetime objects have timezone info
        tz = pytz.timezone(settings.google_calendar_timezone)
        if time_min.tzinfo is None:
            time_min = tz.localize(time_min)
        if time_max.tzinfo is None:
            time_max = tz.localize(time_max)

        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min.isoformat(),
            timeMax=time_max.isoformat(),
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        if not events:
            return []

        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            formatted_events.append({
                'id': event['id'],
                'summary': event.get('summary', 'No Title'),
                'description': event.get('description', ''),
                'start': start,
                'end': end,
                'location': event.get('location', ''),
                'attendees': [attendee.get('email') for attendee in event.get('attendees', [])],
                'htmlLink': event.get('htmlLink', '')
            })

        return formatted_events

    def createDocumentInDrive(self, title="New Document", content="Hello, this is a test document created by Python!"):
        """
        Creates a Google Docs document in Drive and adds initial text.

        Parameters:
        - title: str -> Document title
        - content: str -> Initial content to insert
        """
        creds = self._get_credentials()
        docs_service = build('docs', 'v1', credentials=creds)

        # Step 1: Create the document
        doc = docs_service.documents().create(body={'title': title}).execute()
        doc_id = doc['documentId']

        # Step 2: Insert initial content
        requests = [
            {
                'insertText': {
                    'location': {'index': 1},
                    'text': content
                }
            }
        ]
        docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()

        # Optional: return the Google Docs URL
        return f"Document created: https://docs.google.com/document/d/{doc_id}/edit"

    def _get_credentials(self):
        """Handles authentication and saves a token for reuse."""
        # ========================================
        # 1. 返回缓存的凭证 (避免重复验证)
        # ========================================
        if self._creds and self._creds.valid:
            return self._creds

        creds = None
        token_path = settings.google_token_path

        # ========================================
        # 2. 尝试从 token.pickle 加载
        # ========================================
        if token_path.exists():
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)

        # ========================================
        # 3. 验证并刷新 token
        # ========================================
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    console.print(f"[yellow]Token refresh failed: {e}[/yellow]")
                    creds = None

            # ========================================
            # 4. 需要重新认证
            # ========================================
            if not creds:
                creds = self._authenticate_device_flow()

            # ========================================
            # 5. 保存新 token
            # ========================================
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        # ========================================
        # 6. 缓存凭证到内存
        # ========================================
        self._creds = creds
        return creds
    
    def _authenticate_device_flow(self):
        """Authenticate using OAuth 2.0 for Desktop Apps with local server callback."""
        client_id = settings.google_oauth_client_id
        client_secret = settings.google_oauth_client_secret
        
        # Create flow with proper desktop app configuration
        # Note: redirect_uris will be automatically set by run_local_server()
        flow = InstalledAppFlow.from_client_config(
            {
                "installed": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "redirect_uris": ["http://localhost"]
                }
            },
            scopes=self._SCOPES
        )
        
        # Display authentication instructions
        console.print("\n[bold cyan]🔐 Google Authentication Required[/bold cyan]")
        console.print(Panel(
            "[yellow]Please follow these steps:[/yellow]\n"
            "1. A browser window will open automatically\n"
            "2. Sign in with your Google account\n"
            "3. Grant the requested permissions\n"
            "4. The browser will redirect to localhost (this is normal)\n"
            "5. Return to this terminal after authorization",
            title="[bold magenta]Authentication Steps[/bold magenta]",
            border_style="cyan"
        ))
        
        # Run local server for OAuth callback
        # port=0 means use a random available port
        # This is the recommended approach for desktop apps
        creds = flow.run_local_server(
            port=0,
            authorization_prompt_message="",
            success_message="✅ Authentication successful! You can close this window and return to the terminal.",
            open_browser=True
        )
        
        console.print("[bold green]✅ Authentication completed successfully![/bold green]\n")
        return creds

    def get_user_info(self) -> dict:
        """
        从 Google OAuth 获取用户信息 (email, name)
        使用缓存机制避免重复请求

        Returns:
            dict: {'email': str, 'name': str}
        """
        # ========================================
        # 1. 检查内存缓存
        # ========================================
        if self._user_info:
            return self._user_info

        # ========================================
        # 2. 检查持久化缓存 (user_info.json)
        # ========================================
        user_info_path = settings.google_token_path.parent / "user_info.json"
        if user_info_path.exists():
            try:
                with open(user_info_path, 'r', encoding='utf-8') as f:
                    self._user_info = json.load(f)
                    console.print(f"[green]✓ User loaded from cache: {self._user_info['name']} ({self._user_info['email']})[/green]")
                    return self._user_info
            except Exception as e:
                console.print(f"[yellow]Failed to load cached user info: {e}[/yellow]")

        # ========================================
        # 3. 从 Gmail API 获取用户邮箱 (不触发 openid scope)
        # ========================================
        try:
            creds = self._get_credentials()
            gmail_service = build('gmail', 'v1', credentials=creds)
            profile = gmail_service.users().getProfile(userId='me').execute()

            self._user_info = {
                'email': profile.get('emailAddress', 'unknown@example.com'),
                'name': profile.get('emailAddress', 'User').split('@')[0].title()  # 从邮箱提取用户名
            }

            # ========================================
            # 4. 持久化缓存到本地
            # ========================================
            try:
                with open(user_info_path, 'w', encoding='utf-8') as f:
                    json.dump(self._user_info, f, indent=2)
            except Exception as e:
                console.print(f"[yellow]Failed to cache user info: {e}[/yellow]")

            console.print(f"[green]✓ User authenticated: {self._user_info['name']} ({self._user_info['email']})[/green]")
            return self._user_info

        except Exception as e:
            console.print(f"[red]Failed to fetch user info: {e}[/red]")
            # 返回默认值避免崩溃
            return {'email': 'unknown@example.com', 'name': 'User'}


    def _create_message(self, sender, to, subject, message_text):
        """Creates a base64 encoded email message."""
        message = MIMEText(message_text)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return {'raw': raw_message}


    def _send_message(self, service, user_id, message):
        """Sends the email via Gmail API."""
        sent = service.users().messages().send(userId=user_id, body=message).execute()
        return "Email sent! Message ID: {sent['id']}"



