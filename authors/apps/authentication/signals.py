from django.db.models.signals import post_save
from django.dispatch import receiver
from authors.apps.authentication.models import User
from authors.apps.authentication.models import UserNotification


@receiver(post_save, sender=User)
def setup_notification_permissions(sender, **kwargs):
    instance = kwargs.get('instance')
    created = kwargs.get('created', False)

    if created:
        data = {
            'user': instance,
            'email_notifications': True,
            'in_app_notifications': True
        }
        UserNotification.objects.create(**data)
