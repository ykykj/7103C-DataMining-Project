from __future__ import print_function
import os.path
import base64
import pickle
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

    def sendEmail(self, to, subject, body):
        creds = self._get_credentials()
        service = build('gmail', 'v1', credentials=creds)
        message = self._create_message(sender=settings.google_cloud_auth_email, to=to, subject=subject, message_text=body)
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
            'attendees': [{'email': email} for email in attendees_emails] if attendees_emails else [],
        }

        created_event = service.events().insert(calendarId='primary', body=event).execute()
        return f"Event created: {created_event.get('htmlLink')}"

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
        creds = None
        token_path = settings.google_token_path
        
        # Try to load existing token
        if token_path.exists():
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)

        # Validate and refresh if needed
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    console.print(f"[yellow]Token refresh failed: {e}[/yellow]")
                    creds = None
            
            # Need new authentication
            if not creds:
                creds = self._authenticate_device_flow()
            
            # Save the credentials
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
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



