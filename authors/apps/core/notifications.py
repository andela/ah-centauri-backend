from django.template.loader import render_to_string

"""
Notification Message object dict

source: 
    A ForeignKey to Django's User model (Can be null if it's not a User to User Notification).
source_display_name:
    A User Friendly name for the source of the notification.
recipient:
    The Recipient of the notification. It's a ForeignKey to Django's User model.
category: 
    Arbitrary category that can be used to group messages.
action: 
    Verbal action for the notification E.g Sent, Cancelled, Bought (this can be anything you want)
obj: 
    The id of the object associated with the notification (Can be null).
short_description: 
    The body of the notification.
url: 
    The url of the object associated with the notification (Can be null).
silent:
    If this Value is set, the notification won't be persisted to the database.
extra_data: 
    Arbitrary data as a dictionary.
channels: 
    Delivery channels that should be used to deliver the message. Defaults to an empty
    list and must be provided. Available channels are console, email and websocket
"""


def notification_channels(user):
    """
    :param user: User to use when building up list
        of allowed notification channels
    :return: list of channels
    """
    channels = []

    if user.email_notifications:
        channels.append('email')

    if user.in_app_notifications:
        # uncomment to have real time in app notifications
        # channels.append('websocket')
        pass

    return channels


def article_published(request, **kwargs):
    """
    Build up notification payload to send when a new article gets published
    :param request: The request object for the current HTTP request
    :param kwargs:
    :return: Message object dict
    """

    return {
        'source': request.user,
        'source_display_name': 'AH Publications',
        'recipient': kwargs['recipient'],
        'category': 'Subscriptions',
        'action': 'Published',
        'obj': kwargs['instance'].id,
        'short_description': 'New Article Published',
        'url': '',
        'channels': notification_channels(kwargs['recipient']),
        'extra_data': {
            'email_message': render_to_string('articles/article_published.html', context={
                'article': kwargs['instance']
            }),
            'email_text': render_to_string('articles/article_published.txt', context={
                'article': kwargs['instance']
            }),
            'recipient_email': kwargs['recipient'].email,
        }
    }


def article_rated(request, **kwargs):
    """
    Build up notification payload to send when an article gets a new rating
    :param request: The request object for the current HTTP request
    :param kwargs:
    :return: Message object dict
    """

    return {
        'source': request.user,
        'source_display_name': 'AH Publications',
        'recipient': kwargs['recipient'],
        'category': 'Interactions',
        'action': 'Rated',
        'obj': kwargs['instance'].id,
        'short_description': 'New Article Interactions',
        'url': '',
        'channels': notification_channels(kwargs['recipient']),
        'extra_data': {
            'email_message': render_to_string(
                'articles/article_rated.html', context={
                    'article': kwargs['instance'].article,
                    'user': kwargs['instance'].author
                }),
            'email_text': render_to_string(
                'articles/article_rated.txt', context={
                    'article': kwargs['instance'].article,
                    'user': kwargs['instance'].author
                }),
            'recipient_email': kwargs['recipient'].email,
        }
    }


def user_followed(request, **kwargs):
    """
    Build up notification payload to send when a user gets a new follower
    :param request: The request object for the current HTTP request
    :param kwargs:
    :return: Message object dict
    """

    return {
        'source': request.user,
        'source_display_name': 'Followers Notification',
        'recipient': kwargs['recipient'],
        'category': 'Follows',
        'action': '',
        'obj': kwargs['instance'].id,
        'short_description': 'You have a new follower',
        'url': '',
        'channels': notification_channels(kwargs['recipient']),
        'extra_data': {
            'email_message': render_to_string(
                'users/user_follow.html', context={
                    'user': kwargs['instance']
                }),
            'email_text': render_to_string(
                'users/user_follow.txt', context={
                    'user': kwargs['instance']
                }),
            'recipient_email': kwargs['recipient'].email,
        }
    }


def article_comment(request, **kwargs):
    """
    Build up notification payload to send when an article gets a new comment
    :param request: The request object for the current HTTP request
    :param kwargs:
    :return: Message object dict
    """
    return {
        'source': request.user,
        'source_display_name': 'AH Publications',
        'recipient': kwargs['recipient'],
        'category': 'Interactions',
        'action': 'Comment',
        'obj': kwargs['instance'].id,
        'short_description': 'New Article Interactions',
        'url': '',
        'channels': notification_channels(kwargs['recipient']),
        'extra_data': {
            'email_message': render_to_string(
                'articles/article_comment.html', context={
                    'article': kwargs['instance'].article,
                    'user': kwargs['instance'].author,
                    'comment': kwargs['instance']
                }),
            'email_text': render_to_string(
                'articles/article_comment.txt', context={
                    'article': kwargs['instance'].article,
                    'user': kwargs['instance'].author,
                    'comment': kwargs['instance']
                }),
            'recipient_email': kwargs['recipient'].email,
        }
    }


def resource_liked(request, **kwargs):
    """
    Build up notification payload to send when an article gets liked
    :param request: The request object for the current HTTP request
    :param kwargs:
    :return: Message object dict
    """

    return {
        'source': request.user,
        'source_display_name': 'AH Publications',
        'recipient': kwargs['recipient'],
        'category': 'Interactions',
        'action': '',
        'obj': kwargs['instance'].id,
        'short_description': 'New Article Interactions',
        'url': '',
        'channels': notification_channels(kwargs['recipient']),
        'extra_data': {
            'email_message': render_to_string(
                'articles/article_likes.html', context={
                    'article': kwargs['instance'].article,
                    'user': kwargs['instance'].user
                }),
            'email_text': render_to_string(
                'articles/article_likes.txt', context={
                    'article': kwargs['instance'].article,
                    'user': kwargs['instance'].user
                }),
            'recipient_email': kwargs['recipient'].email,
        }
    }


registered_notifications = {
    'article_published': article_published,
    'article_rated': article_rated,
    'user_followed': user_followed,
    'article_comment': article_comment,
    'resource_liked': resource_liked
}
