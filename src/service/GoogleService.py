from __future__ import print_function
import os.path
import base64
import pickle
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class GoogleService:
    def __init__(self):
        # Gmail API scope for sending emails
        self._SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    def sendEmail(self, to, subject, body):
        creds = self._get_credentials()
        service = build('gmail', 'v1', credentials=creds)
        message = self._create_message(sender="mohamednorth@gmail.com", to=to, subject=subject, message_text=body)
        self._send_message(service, "me", message)


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



