from django.core.mail import EmailMultiAlternatives
from notifications.channels import BaseNotificationChannel


class EmailNotificationChannel(BaseNotificationChannel):
    """Allows notifications to be sent via email to users."""

    def construct_message(self):
        """Constructs a message from notification arguments."""
        kwargs = self.notification_kwargs

        message = {
            'formatted': kwargs['extra_data']['email_message'],
            'plain_text': kwargs['extra_data']['email_text']
        }

        return message

    def notify(self, message):
        """Send the notification."""
        subject = self.notification_kwargs['short_description']
        sender = 'noreply@ah-centauri.com'

        recipient = self.notification_kwargs['extra_data']['recipient_email']

        msg = EmailMultiAlternatives(subject, message['plain_text'], sender, [recipient])
        msg.attach_alternative(message['formatted'], "text/html")
        msg.send()
