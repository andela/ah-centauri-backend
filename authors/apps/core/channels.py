from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from notifications.channels import BaseNotificationChannel
from pusher import Pusher

from authors.apps.authentication.models import User


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

        msg = EmailMultiAlternatives(
            subject, message['plain_text'], sender, [recipient])
        msg.attach_alternative(message['formatted'], "text/html")
        msg.send()


class PusherNotificationChannel(BaseNotificationChannel):
    """Allows realtime notifications to be sent via Pusher"""

    def construct_message(self):
        """Constructs a message from notification arguments."""
        kwargs = self.notification_kwargs

        sender = User.objects.get(pk=kwargs['source'])
        recipient = User.objects.get(pk=kwargs['recipient'])

        message = {
            'source': {
                'id': sender.id,
                'username': sender.username
            },
            'recipient': {
                'id': recipient.id
            },
            'short_description': kwargs['short_description'],
            'actions': kwargs['action'],
            'read': kwargs['is_read']
        }

        return message

    def notify(self, message):
        """Send the notification"""
        pusher = Pusher(
            app_id=settings.PUSHER_APP_ID,
            key=settings.PUSHER_KEY,
            secret=settings.PUSHER_SECRET,
            cluster=settings.PUSHER_CLUSTER,
            ssl=True
        )

        pusher.trigger(
            'user-{}'.format(message['recipient']['id']),
            'notificationReceived',
            message
        )
