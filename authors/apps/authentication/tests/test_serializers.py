from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.serializers import ValidationError

from authors.apps.authentication.error_messages import errors
from authors.apps.authentication.models import User, PasswordReset
from authors.apps.authentication.serializers import (LoginSerializer,
                                                     PasswordResetRequestSerializer,
                                                     PasswordResetSerializer,
                                                     RegistrationSerializer,
                                                     UserSerializer,
                                                     GoogleAuthAPISerializer,
                                                     FacebookAuthAPISerializer,
                                                     )
from authors.apps.authentication.utils import PasswordResetTokenHandler


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
        self.user.update({'password': 'l' * 129})

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


class PasswordResetSerializerTest(TestCase):
    """
    Unit tests for the PasswordResetSerializer
    class defined in our serializers.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_user",
            email="ah_user@mailinator.com",
            password="p@ssW0rddd"
        )
        self.user.save()
        password_reset_token = PasswordResetTokenHandler().get_reset_token(
            self.user.email
        )
        self.password_reset = {
            "user_id": self.user.id,
            "token": password_reset_token
        }

        self.password_reset_invalid_user = {
            "user_id": 10000,
            "token": password_reset_token
        }

    def test_create_valid_password_reset_record(self):
        """ Test whether the create password reset record method works. """
        serializer = PasswordResetSerializer(data=self.password_reset)
        self.assertTrue(serializer.is_valid())
        saved_password_reset = serializer.save()
        self.assertIsInstance(saved_password_reset, PasswordReset)

    def test_create_password_reset_without_valid_user(self):
        """ 
        Test whether the create password reset record 
        without a valid user id works. 
        """
        serializer = PasswordResetSerializer(
            data=self.password_reset_invalid_user
        )
        self.assertFalse(serializer.is_valid())


class PasswordResetRequestSerializerTest(TestCase):
    """
    Unit test for the PasswordResetRequestSerializerTest
    class defined in our serializers.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_user",
            email="ah_user@mailinator.com",
            password="p@ssW0rddd"
        )
        self.user.save()
        password_reset_token = PasswordResetTokenHandler().get_reset_token(
            self.user.email
        )
        self.password_reset_request_payload = {
            "email": self.user.email
        }

        self.password_reset_request_payload_invalid = {
            "email": "gmail.com"
        }

    def test_valid_password_reset_request_payload(self):
        """ Test whether the password reset request record method works. """
        serializer = PasswordResetRequestSerializer(
            data=self.password_reset_request_payload
        )
        self.assertTrue(serializer.is_valid())

    def test_password_reset_invalid_request_payload(self):
        """ 
        Test whether the password reset request record 
        without a valid user id works. 
        """
        serializer = PasswordResetRequestSerializer(
            data=self.password_reset_request_payload_invalid
        )
        self.assertFalse(serializer.is_valid())


GOOGLE_VALIDATION = "authors.apps.authentication.validators.SocialValidation.google_auth_validation"
FACEBOOK_VALIDATION = "authors.apps.authentication.validators.SocialValidation.facebook_auth_validation"
TWITTER_VALIDATION = "authors.apps.authentication.validators.SocialValidation.twitter_auth_validation"


def sample_user():
    return get_user_model().objects.create_user(email='cmeordvda_1554574357@tfbnw.net',
                                                username='cmeordvda',
                                                password='T35tP45w0rd'
                                                )


class GoogleSerializerTest(TestCase):
    """
    Unit test for the GoogleSerializer
    class defined in our serializers.
    """

    def setUp(self):
        self.payload = {
            "access_token": "access_token"
        }

    def test_valid_google_login(self):
        with patch(GOOGLE_VALIDATION) as mg:
            mg.return_value = {
                "name": "alexa",
                "email": "alexa@gmail.com",
                "sub": "102723377587866"
            }
            serializer = GoogleAuthAPISerializer(data=self.payload)
            self.assertTrue(serializer.is_valid())

    def test_in_valid_google_login(self):
        serializer = GoogleAuthAPISerializer(data=self.payload)
        self.assertFalse(serializer.is_valid())

    def test_sub_is_not_found_in_payload(self):
        with patch(GOOGLE_VALIDATION) as mg:
            mg.return_value = {
                "name": "alexa",
                "email": "cmeordvda_1554574357@tfbnw.net"
            }
            serializer = GoogleAuthAPISerializer(data=self.payload)

            self.assertFalse(serializer.is_valid())

    def test_login_user_already_exist(self):
        sample_user()
        with patch(GOOGLE_VALIDATION) as mg:
            mg.return_value = {
                "name": "alexa",
                "email": "alexa@gmail.com",
                "sub": "102723377587866"
            }
            serializer = GoogleAuthAPISerializer(data=self.payload)
            self.assertTrue(serializer.is_valid())
            self.assertIn('access_token', serializer.data)


class FacebookSerializerTest(TestCase):
    """
    Unit test for the FacebookSerializer
    class defined in our serializers.
    """

    def setUp(self):
        self.payload = {
            "access_token": "access_token"
        }

    def test_valid_google_login(self):
        with patch(FACEBOOK_VALIDATION) as mg:
            mg.return_value = {
                "name": "alexa",
                "email": "alexa@gmail.com",
                "id": "102723377587866"
            }
            serializer = FacebookAuthAPISerializer(data=self.payload)
            self.assertTrue(serializer.is_valid())

    def test_in_valid_facebook_login(self):
        serializer = FacebookAuthAPISerializer(data=self.payload)
        self.assertFalse(serializer.is_valid())

    def test_id_is_not_found_in_payload(self):
        with patch(FACEBOOK_VALIDATION) as mg:
            mg.return_value = {
                "name": "alexa",
                "email": "cmeordvda_1554574357@tfbnw.net"
            }
            serializer = FacebookAuthAPISerializer(data=self.payload)

            self.assertFalse(serializer.is_valid())

    def test_login_user_already_exist(self):
        sample_user()
        with patch(FACEBOOK_VALIDATION) as mg:
            mg.return_value = {
                "name": "alexa",
                "email": "alexa@gmail.com",
                "id": "102723377587866"
            }
            serializer = FacebookAuthAPISerializer(data=self.payload)
            self.assertTrue(serializer.is_valid())
            self.assertIn('access_token', serializer.data)
