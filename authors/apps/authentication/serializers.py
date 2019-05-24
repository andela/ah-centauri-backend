import re
from random import randint

from django.core.validators import (RegexValidator,
                                    ValidationError, )
from authors.apps.profiles.serializers import GetProfileSerializer
from .models import (User,
                     PasswordReset,
                     UserNotification, )
from rest_framework.validators import UniqueValidator
from notifications.models import Notification
from django.contrib.auth import authenticate
from rest_framework import serializers

from authors.apps.authentication.validators import SocialValidation
from authors.apps.profiles.serializers import GetProfileSerializer
from .error_messages import errors
from .models import (User,
                     PasswordReset, )


def email_validate(email):
    regex = "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    if not re.match(regex, email):
        raise ValidationError(errors['email']['invalid'])


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializers registration requests and creates a new user."""
    # Ensure passwords are at least 8 characters long, no longer than 128
    # characters, and can not be read by the client.
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True,
        validators=[RegexValidator(
            regex="^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).+$",
            message=errors['password']['weak_password'])],
        error_messages={
            "max_length": errors['password']['max_length'],
            "min_length": errors['password']['min_length'],
            "blank": errors['password']['blank'],
            "required": errors['password']['required']
        }
    )

    username = serializers.CharField(
        required=True,
        error_messages={
            "required": errors['username']['required'],
            "blank": errors['username']['blank'],
            "invalid": errors['username']['invalid']
        }
    )

    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(
            queryset=User.objects.all(), message=errors['email']['unique']),
            email_validate],
        error_messages={
            "required": errors['email']['required'],
            "blank": errors['email']['blank'],
            "invalid": errors['email']['invalid']
        }
    )

    def validate_username(self, username):

        uname = "^(?=.{4,20}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$"

        if User.objects.filter(username=username.lower()).exists():
            raise ValidationError(errors['username']['unique'])

        if not re.match(uname, username):
            raise ValidationError(errors['username']['invalid'])

        return username.lower()

    class Meta:
        model = User
        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above.
        fields = ['email', 'username', 'password']

    def create(self, validated_data):
        # Use the `create_user` method we wrote earlier to create a new user.
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255, read_only=True)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        # The `validate` method is where we make sure that the current
        # instance of `LoginSerializer` has "valid". In the case of logging a
        # user in, this means validating that they've provided an email
        # and password and that this combination matches one of the users in
        # our database.
        email = data.get('email', None)
        password = data.get('password', None)

        # As mentioned above, an email is required. Raise an exception if an
        # email is not provided.
        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )

        # As mentioned above, a password is required. Raise an exception if a
        # password is not provided.
        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        # The `authenticate` method is provided by Django and handles checking
        # for a user that matches this email/password combination. Notice how
        # we pass `email` as the `username` value. Remember that, in our User
        # model, we set `USERNAME_FIELD` as `email`.
        user = authenticate(username=email, password=password)

        # If no user was found matching this email/password combination then
        # `authenticate` will return `None`. Raise an exception in this case.
        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )

        # Django provides a flag on our `User` model called `is_active`. The
        # purpose of this flag to tell us whether the user has been banned
        # or otherwise deactivated. This will almost never be the case, but
        # it is worth checking for. Raise an exception in this case.
        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        # Django provides a flag on our `User` model called `is_active`. The
        # purpose of this flag to tell us whether the user has been banned
        # or otherwise deactivated. This will almost never be the case, but
        # it is worth checking for. Raise an exception in this case.

        # The `validate` method should return a dictionary of validated data.
        # This is the data that is passed to the `create` and `update` methods
        # that we will see later on.
        return {
            'user': user,
            'email': user.email,
            'username': user.username,
        }


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """Handles serialization and deserialization of User objects."""

    # Passwords must be at least 8 characters, but no more than 128
    # characters. These values are the default provided by Django. We could
    # change them, but that would create extra work while introducing no real
    # benefit, so let's just stick with the defaults.

    articles = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='articles:article',
        read_only=True,
        lookup_field='slug'

    )

    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    profile = GetProfileSerializer()

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'profile', 'articles')
        # The `read_only_fields` option is an alternative for explicitly
        # specifying the field with `read_only=True` like we did for password
        # above. The reason we want to use `read_only_fields` here is because
        # we don't need to specify anything else about the field. For the
        # password field, we needed to specify the `min_length` and
        # `max_length` properties too, but that isn't the case for the token
        # field.

    def update(self, instance, validated_data):
        """Performs an update on a User."""

        # Passwords should not be handled with `setattr`, unlike other fields.
        # This is because Django provides a function that handles hashing and
        # salting passwords, which is important for security. What that means
        # here is that we need to remove the password field from the
        # `validated_data` dictionary before iterating over it.
        password = validated_data.pop('password', None)
        profile_data = validated_data.pop('profile', {})

        for (key, value) in validated_data.items():
            # For the keys remaining in `validated_data`, we will set them on
            # the current `User` instance one at a time.
            setattr(instance, key, value)

        if password is not None:
            # `.set_password()` is the method mentioned above. It handles all
            # of the security stuff that we shouldn't be concerned with.
            instance.set_password(password)

        # Finally, after everything has been updated, we must explicitly save
        # the model. It's worth pointing out that `.set_password()` does not
        # save the model.
        instance.save()

        for (key, value) in profile_data.items():
            setattr(instance.profile, key, value)
            # Save profile
        instance.profile.save()

        return instance


class PasswordResetSerializer(serializers.ModelSerializer):
    """
    Handles serialization and deserialization of PasswordReset model
    """

    class Meta:
        model = PasswordReset
        fields = ('user_id', 'token')
        read_only_fields = ('createdOn',)


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Validate PasswordReset Request from a user
    """
    email = serializers.EmailField()


class SetNewPasswordSerializer(serializers.Serializer):
    """
    Validate the password being created by the password reset endpoint
    """

    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True,
        validators=[RegexValidator(
            regex="^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).+$",
            message="Please ensure password contains at least 1 uppercase, 1 lowercase and 1 special character")],
        error_messages={
            "max_length": "Please ensure your password does not exceed 128 characters",
            "min_length": "Please ensure that your password has at least 8 characters",
            "blank": "A password is required to complete registration",
            "required": "A password is required to complete registration"
        }
    )


class NotificationSerializer(serializers.ModelSerializer):
    source = UserSerializer(read_only=True)
    source_display_name = serializers.CharField(max_length=150)
    action = serializers.CharField(max_length=50)
    category = serializers.CharField(max_length=50)
    url = serializers.URLField()
    short_description = serializers.CharField(max_length=100)
    is_read = serializers.BooleanField(default=False)
    create_date = serializers.DateTimeField(format="%c")
    update_date = serializers.DateTimeField(format="%c")

    class Meta:
        model = Notification

        fields = ['source', 'source_display_name', 'action', 'category', 'url', 'short_description',
                  'is_read', 'create_date', 'update_date']

    def to_representation(self, instance):
        """"""
        notification = super().to_representation(instance)

        notification.update({
            'source': {
                'username': notification['source']['username']
            }
        })

        return notification


class UserNotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    email_notifications = serializers.BooleanField()
    in_app_notifications = serializers.BooleanField()

    class Meta:
        model = UserNotification

        fields = ['user', 'email_notifications', 'in_app_notifications']


class GoogleAuthAPISerializer(serializers.ModelSerializer):
    """Handles serialization and deserialization of User objects."""

    access_token = serializers.CharField()

    class Meta:
        model = User
        fields = ['access_token']

    @staticmethod
    def validate_access_token(access_token):
        """
        Handles validating the request token by decoding and getting user_info associated
        To an account on google.
        Then authenticate the user.
        :param access_token:
        :return: user_token
        """
        id_info = SocialValidation.google_auth_validation(
            access_token=access_token)

        # checks if the data retrieved once token is decoded is empty.
        if id_info is None:
            raise serializers.ValidationError('Token is not valid.')

        # Checks to see if there is a user id associated with the payload after decoding the token
        # this user_id confirms that the user exists on twitter because its a unique identifier.
        if 'sub' not in id_info:
            raise serializers.ValidationError(
                'Token is not valid or has expired. Please get a new one.')

        user_id = id_info['sub']
        # Query database to check if there is an existing user with the save email.
        user = User.objects.filter(email=id_info.get('email'))

        # Returns the user token showing that the user has been registered before and existing in our database.
        if user:
            return user[0].token

        # Creates a new user because email is not associated with any existing account in our app
        payload = {
            'email': id_info.get('email'),
            'username': id_info.get('email'),
            'password': randint(10000000, 20000000)
        }
        new_user = User.objects.create_user(**payload)
        new_user.is_verified = True
        new_user.social_id = user_id
        new_user.save()

        return new_user.token


class FacebookAuthAPISerializer(serializers.ModelSerializer):
    """Handles serialization and deserialization of User objects."""

    access_token = serializers.CharField()

    class Meta:
        model = User
        fields = ['access_token']

    @staticmethod
    def validate_access_token(access_token):
        """
        Handles validating the request token by decoding and getting user_info associated
        To an account on facebook.
        Then authenticate the user.
        :param access_token:
        :return: user_token
        """
        id_info = SocialValidation.facebook_auth_validation(
            access_token=access_token)

        # checks if the data retrieved once token is decoded is empty.
        if id_info is None:
            raise serializers.ValidationError('Token is not valid.')

        # Checks to see if there is a user id associated with the payload after decoding the token
        # this user_id confirms that the user exists on twitter because its a unique identifier.
        if 'id' not in id_info:
            raise serializers.ValidationError(
                'Token is not valid or has expired. Please get a new one.')

        user_id = id_info['id']

        # Query database to check if there is an existing user with the save email.
        user = User.objects.filter(email=id_info.get('email'))

        # Returns the user token showing that the user has been registered before and existing in our database.
        if user:
            return user[0].token

        # Creates a new user because email is not associated with any existing account in our app
        payload = {
            'email': id_info.get('email'),
            'username': id_info.get('email'),
            'password': randint(10000000, 20000000)
        }
        new_user = User.objects.create_user(**payload)
        new_user.is_verified = True
        new_user.social_id = user_id
        new_user.save()

        return new_user.token


class TwitterAuthAPISerializer(serializers.ModelSerializer):
    """Handles serialization and deserialization of User objects."""

    access_token = serializers.CharField()
    access_token_secret = serializers.CharField()

    class Meta:
        model = User
        fields = ['access_token', 'access_token_secret']

    def validate(self, data):
        """
        Handles validating the request token by decoding and getting user_info associated
        To an account on twitter.
        Then authenticate the user.
        :param data:
        :return: user_token
        """
        id_info = SocialValidation.twitter_auth_validation(access_token=data.get('access_token'),
                                                           access_token_secret=data.get('access_token_secret'))
        # Check if there is an error message in the id_info validation body
        if 'errors' in id_info:
            raise serializers.ValidationError(
                id_info.get('errors')[0]['message'])

        # checks if the data retrieved once token is decoded is empty.
        if id_info is None:
            raise serializers.ValidationError('Token is not valid.')

        # Checks to see if there is a user id associated with the payload after decoding the token
        # this user_id confirms that the user exists on twitter because its a unique identifier.
        if 'id_str' not in id_info:
            raise serializers.ValidationError(
                'Token is not valid or has expired. Please get a new one.')

        user_id = id_info['id_str']

        # Query database to check if there is an existing user with the save email.
        user = User.objects.filter(email=id_info.get('email'))

        # Returns the user token showing that the user has been registered before and existing in our database.
        if user:
            return {"token": user[0].token}

        # Creates a new user because email is not associated with any existing account in our app
        payload = {
            'email': id_info.get('email'),
            'username': id_info.get('email'),
            'password': randint(10000000, 20000000)
        }
        try:
            new_user = User.objects.create_user(**payload)
            new_user.is_verified = True
            new_user.social_id = user_id
            new_user.save()
        except:
            raise serializers.ValidationError('Error While creating User.')

        return {"token": new_user.token}
