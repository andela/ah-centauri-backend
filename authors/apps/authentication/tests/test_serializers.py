from django.test import TestCase
from rest_framework.serializers import ValidationError

from authors.apps.authentication.models import User
from authors.apps.authentication.serializers import LoginSerializer
from authors.apps.authentication.serializers import RegistrationSerializer
from authors.apps.authentication.serializers import UserSerializer


class RegistrationSerializerTests(TestCase):
    """
    Unit tests for the RegistrationSerializer
    class defined in our serializers.
    """

    def setUp(self):
        self.user = {
            "username": "user",
            "email": "user@mail.com",
            "password": "password"
        }

    def test_register_method(self):
        """ Test whetther the create method works. """
        serializer = RegistrationSerializer(data=self.user)
        self.assertTrue(serializer.is_valid())
        saved_user = serializer.save()
        self.assertIsInstance(saved_user, User)


class LoginSerializerTests(TestCase):
    """
    Unit tests for the LoginSerializer class
    defined in our serializers.
    """
    def setUp(self):
        self.login_payload = {
            "email": "user@mail.com",
            "password": "password"
        }

    def test_login_no_password_validation(self):
        """ Test whether users can log in without a password. """
        payload = {
            "email": "user@mail.com"
        }
        serializer = LoginSerializer(data=payload)
        with self.assertRaises(ValidationError) as e:
            serializer.validate(payload)
        self.assertEqual(
            e.exception.detail[0],
            'A password is required to log in.'
            )

    def test_login_no_email_validation(self):
        """ Test whether users can log in without an email. """
        payload = {
            "password": "password"
        }
        serializer = LoginSerializer(data=payload)
        with self.assertRaises(ValidationError) as e:
            serializer.validate(payload)
        self.assertEqual(
            e.exception.detail[0],
            'An email address is required to log in.'
            )

    def test_login_non_existent_user_validation(self):
        """ Test whether users can log in without an email. """  
        serializer = LoginSerializer(data=self.login_payload)
        with self.assertRaises(ValidationError) as e:
            serializer.validate(self.login_payload)
        self.assertEqual(
            e.exception.detail[0],
            'A user with this email and password was not found.'
            )

    class UserSerializerTests(TestCase):
        """
        Unit tests for the UserSerializer class
        defined in our serializers.
        """

        def setUp(self):
            self.user = User.objects.create_user(
                username="user",
                email="user@mail.com",
                password="password"
            )
            self.user.save()
            self.serializer = UserSerializer()
            self.user1 = {
                "username": "user1",
                "email": "user1@mail.com",
                "password": "password1"
            }
            self.user2 = {
                "username": "user2",
                "email": "user2@mail.com",
            }

        def test_update_info_with_password(self):
            """ Test whether a user can update their information. """
            current_password = self.user.password
            updated_user = self.serializer.update(self.user, self.user1)
            self.assertEqual(updated_user.username, "user1")
            self.assertEqual(updated_user.email, "user1@mail.com")
            self.assertNotEqual(updated_user.password, current_password)

        def test_update_info_without_password(self):
            """
            Test whether a user can update their info
            without changing their password.
            """
            current_password = self.user.password
            updated_user = self.serializer.update(self.user, self.user2)
            self.assertEqual(updated_user.username, "user2")
            self.assertEqual(updated_user.email, "user2@mail.com")
            self.assertEqual(updated_user.password, current_password)
