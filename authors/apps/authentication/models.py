from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.db import models


class UserManager(BaseUserManager):
    """
    Django requires that custom users define their own Manager class. By
    inheriting from `BaseUserManager`, we get a lot of the same code used by
    Django to create a `User` for free. 

    All we have to do is override the `create_user` function which we will use
    to create `User` objects.
    """

    def create_user(self, username, email, password=None):
        """Create and return a `User` with an email, username and password."""
        if username is None:
            raise TypeError('Users must have a username.')

        if email is None:
            raise TypeError('Users must have an email address.')

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password):
        """
        Create and return a `User` with superuser powers.

        Superuser powers means that this use is an admin that can do anything
        they want.
        """
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    # Each `User` needs a human-readable unique identifier that we can use to
    # represent the `User` in the UI. We want to index this column in the
    # database to improve lookup performance.
    username = models.CharField(db_index=True, max_length=255, unique=True)

    # We also need a way to contact the user and a way for the user to identify
    # themselves when logging in. Since we need an email address for contacting
    # the user anyways, we will also use the email for logging in because it is
    # the most common form of login credential at the time of writing.
    email = models.EmailField(db_index=True, unique=True)

    # When a user no longer wishes to use our platform, they may try to delete
    # there account. That's a problem for us because the data we collect is
    # valuable to us and we don't want to delete it. To solve this problem, we
    # will simply offer users a way to deactivate their account instead of
    # letting them delete it. That way they won't show up on the site anymore,
    # but we can still analyze the data.
    is_active = models.BooleanField(default=True)

    # The `is_staff` flag is expected by Django to determine who can and cannot
    # log into the Django admin site. For most users, this flag will always be
    # falsed.
    is_staff = models.BooleanField(default=False)

    is_verified = models.BooleanField(default=False)

    # A unique identifier representing what method of authentication used
    # If user logs in using social accounts their id is saved in this object.
    social_id = models.CharField(db_index=True, null=True, max_length=255)

    # A timestamp representing when this object was created.
    created_at = models.DateTimeField(auto_now_add=True)

    # A timestamp representing when this object was last updated.
    updated_at = models.DateTimeField(auto_now=True)

    # More fields required by Django when specifying a custom user model.
    # email_confirmed = models.BooleanField(default=False)
    # The `USERNAME_FIELD` property tells us which field we will use to log in.
    # In this case, we want that to be the email field.
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    # Tells Django that the UserManager class defined above should manage
    # objects of this type.
    objects = UserManager()

    def __str__(self):
        """
        Returns a string representation of this `User`.

        This string is used when a `User` is printed in the console.
        """
        return self.email

    @property
    def token(self):
        """
        Allows us to get a user's token by calling `user.token` instead of
        `user.generate_jwt_token().

        The `@property` decorator above makes this possible.
        """
        return self._generate_jwt_token()

    @property
    def get_full_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically, this would be the user's first and last name. Since we do
        not store the user's real name, we return their username instead.
        """
        return self.username

    def get_short_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically, this would be the user's first name. Since we do not store
        the user's real name, we return their username instead.
        """
        return self.username

    def _generate_jwt_token(self):
        """
        Generates a JSON Web Token that stores this user's ID and has an expiry
        date set to 7 days into the future.
        """
        dt = datetime.now() + timedelta(days=7)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')

    @property
    def email_notifications(self):
        return self.notification_settings.email_notifications

    @property
    def in_app_notifications(self):
        return self.notification_settings.in_app_notifications


class PasswordReset(models.Model):
    """
    Password Reset Model create a Password Reset record
    A password reset record should have a :
    user_id: Int - The primary key from of the user record related to the password reset request 
    token: String - The jwt token generated to allow a user to set their new password.
    used: True - if the token is used or False if the token is not used.
    
    """

    def __str__(self):
        """
        Return a human readable representation of the Password Reset instance.
        """
        return "user_id: {}, token:{}, used:{}, createdOn:{} ".format(
            self.user_id,
            self.token,
            self.used,
            self.createdOn
        )

    user_id = models.ForeignKey(User, db_column="user_id", on_delete=models.CASCADE)
    token = models.CharField(max_length=256, unique=True)
    used = models.BooleanField(default=False)
    createdOn = models.DateTimeField("Created On", auto_now_add=True)


class UserNotification(models.Model):
    """
    User Notification model stores user's preferences for notifications.
    By default all users are "opted in" to notifications
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True,
                                related_name='notification_settings')
    email_notifications = models.BooleanField(default=True)
    in_app_notifications = models.BooleanField(default=True)
