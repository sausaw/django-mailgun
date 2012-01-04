import requests
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import sanitize_address

class MailgunBackend(BaseEmailBackend):
    """A Django Email backend that uses mailgun.
    """

    def __init__(self, fail_silently=False, *args, **kwargs):
        super(MailgunBackend, self).__init__(
                        fail_silently=fail_silently, 
                        *args, **kwargs)

        self._access_key = getattr(settings, 'MAILGUN_ACCESS_KEY', None)
        self._server_name = getattr(settings, 'MAILGUN_SERVER_NAME', '')
        self._api_url = "https://api.mailgun.net/v2/%s/" % self._server_name
        Mailgun.init(self._access_key)

    def open(self):
        """Stub for open connection, all sends are done over HTTP POSTs
        """
        pass

    def close(self):
        """Close any open HTTP connections to the API server.
        """
        pass

    def _send(self, email_message):
        """A helper method that does the actual sending."""
        if not email_message.recipients():
            return False
        from_email = sanitize_address(email_message.from_email, email_message.encoding)
        recipients = [sanitize_address(addr, email_message.encoding)
                      for addr in email_message.recipients()]

        try:
            r = requests.\
                post(self._api_url + "messages.mime",
                     auth=("api", self._access_key),
                     data={
                            "to": from_email,
                            "from": recipients,
                         },
                     files={
                            "message": email_message.message().as_string(),
                         }
                     )
        except:
            if not self.fail_silently:
                raise
            return False
        return True

    def send_messages(self, email_messages):
        """Sends one or more EmailMessage objects and returns the number of
        email messages sent.
        """
        if not email_messages:
            return

        num_sent = 0
        for message in email_messages:
            if self._send(message):
                num_sent += 1

        return num_sent
