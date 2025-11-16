from __future__ import print_function
import os
import os.path
import base64
import pickle
from datetime import datetime
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class GoogleService:
    def __init__(self):
        # Gmail API scope for sending emails, events, calendar, drive
        self._SCOPES = ['https://www.googleapis.com/auth/gmail.send',
                        'https://www.googleapis.com/auth/gmail.readonly',
                        'https://www.googleapis.com/auth/calendar.events',
                        'https://www.googleapis.com/auth/drive.file',
                        'https://www.googleapis.com/auth/documents']

    def sendEmail(self, to, subject, body):
        creds = self._get_credentials()
        service = build('gmail', 'v1', credentials=creds)
        message = self._create_message(sender=os.getenv("GOOGLE_CLOUD_AUTH_EMAIL"), to=to, subject=subject, message_text=body)
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
                'timeZone': 'America/Los_Angeles',  # Change as needed
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'America/Los_Angeles',
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
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('creds/credentials.json', self._SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
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



