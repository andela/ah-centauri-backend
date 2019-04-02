from django.test import TestCase
from rest_framework.serializers import ValidationError

from authors.apps.authentication.models import User
from authors.apps.authentication.serializers import LoginSerializer
from authors.apps.authentication.serializers import RegistrationSerializer
from authors.apps.authentication.serializers import UserSerializer
from authors.apps.authentication.error_messages import errors

class RegistrationSerializerTests(TestCase):
    """
    Unit tests for the RegistrationSerializer
    class defined in our serializers.
    """

    def setUp(self):
        self.user = {
            "username": "user",
            "email": "user@mail.com",
            "password": "invAli3d#"
        }

    def test_register_method(self):
        """ Test whetther the create method works. """
        serializer = RegistrationSerializer(data=self.user)
        self.assertTrue(serializer.is_valid())
        saved_user = serializer.save()
        self.assertIsInstance(saved_user, User)

    def test_validation_fails_with_non_alphanumeric_password(self):
        # setup
        self.user.update({'password': 'password'})

        # act
        serializer = RegistrationSerializer(data=self.user)

        # assert
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors['password'][0],
            errors['password']['weak_password'])

    def test_validation_fails_if_missing_password(self):
        # setup
        self.user.pop('password')

        # act
        serializer = RegistrationSerializer(data=self.user)

        # assert
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors['password'][0], errors['password']['required'])

    def test_password_min_length_validation(self):
        # setup
        self.user.update({'password': 'less'})

        # act
        serializer = RegistrationSerializer(data=self.user)

        # assert
        self.assertFalse(serializer.is_valid())
        self.assertIn(errors['password']['min_length'],
                      serializer.errors['password'])

    def test_password_max_length_validation(self):
        # setup
        self.user.update({'password': 'l'*129})

        # act
        serializer = RegistrationSerializer(data=self.user)

        # assert
        self.assertFalse(serializer.is_valid())
        self.assertIn(
            errors['password']['max_length'],
            serializer.errors['password'])

    def test_validation_fails_if_blank_password(self):
        # setup
        self.user.update({'password': ''})

        # act
        serializer = RegistrationSerializer(data=self.user)

        # assert
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors['password'][0], errors['password']['required'])

    def test_unique_username_validation(self):
        # setup
        # create user
        User.objects.create_user(**self.user)

        # act
        # attempt to create another user with same username
        self.user.update({'email': 'newunusedemail@emails.com'})
        serializer = RegistrationSerializer(data=self.user)

        # assert
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors['username'][0], errors['username']['unique'])

    def test_unique_email_validation(self):
        # setup
        # create user
        User.objects.create_user(**self.user)

        # act
        # attempt to create another user with same email
        self.user.update({'username': 'newusername'})
        serializer = RegistrationSerializer(data=self.user)

        # assert
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors['email'][0], errors['email']['unique'])

    def test_non_alphanumeric_emails_fail_validation(self):
        # setup
        self.user.update({'email': 'v123@e..com'})

        # act
        serializer = RegistrationSerializer(data=self.user)

        # assert
        self.assertFalse(serializer.is_valid())
        self.assertIn(errors['email']['invalid'],
                      serializer.errors['email'])

    def test_invalid_username(self):
        # setup
        self.user.update({'username': 'ze-us'})

        # act
        serializer = RegistrationSerializer(data=self.user)

        # assert
        self.assertFalse(serializer.is_valid())
        self.assertIn(errors['username']['invalid'],
                      serializer.errors['username'])


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

    def test_login_existent_user_validation(self):
        """ Test whether users can log in without an email. """
        # register user
        user = User.objects.create_user(
            username="user",
            email="user@mail.com",
            password="password"
        )
        user.save()
        serializer = LoginSerializer(data=self.login_payload)
        user_data = serializer.validate(self.login_payload)
        self.assertEqual({
            "user": user,
            "username": "user",
            "email": "user@mail.com"
        }, user_data)

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
