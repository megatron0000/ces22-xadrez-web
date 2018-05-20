from email.mime.text import MIMEText

from django.core.mail.backends.base import BaseEmailBackend
from gmailbox.models import UserToken
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import base64


class GmailBackend(BaseEmailBackend):

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently)
        try:
            cred = UserToken.objects.get()
            self.credentials = Credentials.from_authorized_user_info({
                'token': cred.token,
                'refresh_token': cred.refresh_token,
                'token_uri': cred.token_uri,
                'client_id': cred.client_id,
                'client_secret': cred.client_secret,
                'scopes': cred.scopes
            })
            self.service = build('gmail', 'v1', credentials=self.credentials)
        except UserToken.DoesNotExist:
            self.credentials = None

    def send_messages(self, email_messages):
        # 0 successes
        if self.credentials is None:
            return 0
        successes = 0
        for mail in email_messages:
            message = MIMEText(mail.body)
            message['to'] = ', '.join(mail.to)  # comma-separated list of emails
            message['from'] = self.service.users() \
                .getProfile(userId='me').execute()['emailAddress']
            message['subject'] = mail.subject or ''
            successes += 1
            try:
                self.service.users().messages().send(userId='me', body={
                    'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()
                }).execute()
            except Exception as e:
                print(e)
                successes -= 1
