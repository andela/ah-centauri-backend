from django.test import TestCase

from authors.apps.authentication.models import User


def create_user(username="user", email="user@mail.com", password="password"):
    return User.objects.create_user(
            username=username,
            email=email,
            password=password
            )


def create_superuser(username="superuser", email="superuser@mail.com", password="password"):
    return User.objects.create_superuser(
            username=username,
            email=email,
            password=password
            )


class UserManagerTest(TestCase):
    """ Unit tests for UserManager class defined in our models. """

    def test_successfull_registraton(self):
        """ Test whether a user can register """
        user = create_user()
        self.assertIsInstance(user, User)

    def test_failed_registration_no_username(self):
        """ Test whether a user can register without a username. """
        with self.assertRaises(TypeError) as e:
            create_user(username=None)
        self.assertEqual(str(e.exception), 'Users must have a username.')

    def test_failed_registration_no_email(self):
        """ Test whether a user can register without an email. """
        with self.assertRaises(TypeError) as e:
            create_user(email=None)
        self.assertEqual(str(e.exception), 'Users must have an email address.')

    def test_successfull_registraton_superuser(self):
        """ Test whether we can create a superuser """
        user = create_superuser()
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_failed_superuser_registration_no_password(self):
        """ Test whether a superuser can register without a password. """
        with self.assertRaises(TypeError) as e:
            create_superuser(password=None)
        self.assertEqual(str(e.exception), 'Superusers must have a password.')


class UserTest(TestCase):
    """ Unit tests for `User` model. """

    def setUp(self):
        self.user = User.objects.create_user(
            username="user",
            email="user@mail.com",
            password="password"
            )

    def test_user_string_representation(self):
        """
        Test whether a proper string representation
        of `User` is returned.
        """
        self.assertEqual(str(self.user), "user@mail.com")

    def test_get_full_name(self):
        """ Test whether username is returned when method is called. """
        self.assertEqual(self.user.get_full_name, "user")

    def test_get_short_name(self):
        """ Test whether username is returned when method is called. """
        self.assertEqual(self.user.get_short_name(), "user")
