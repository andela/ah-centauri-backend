import copy
from notifications.signals import notify
from authors.apps.core.notifications import registered_notifications


def send_notifications(request, **kwargs):
    """
    :param request: The HTTP request object for the current request
    :param kwargs:
    :return: None
        Arguments:
            recipients
                An iterable of User objects that we want to notify about
                an event in the app

            notification_type
                The type of notification to send. This value is used to
                decide which notification object to send from the
                registered_notifications dict

            instance
                Object that triggered the event we're responding to with a notification
                i.e if a new article is created, then "instance" will be an instance
                of Articles model
    """
    notification_type = kwargs.get('notification_type', None)

    if notification_type is None:
        raise Exception("Notification type must be provided")

    if notification_type not in registered_notifications:
        raise Exception("Invalid notification type found")

    for recipient in kwargs['recipients']:
        current_kwargs = copy.deepcopy(kwargs)
        current_kwargs['recipient'] = recipient
        args = registered_notifications[notification_type](request, **current_kwargs)

        notify.send(
            sender='ah-centauri',
            **args
        )
