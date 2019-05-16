from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from authors.apps.authentication.models import User, PasswordReset
from authors.apps.authentication.response_messages import PASSWORD_RESET_MSGS
from authors.apps.authentication.utils import PasswordResetTokenHandler


class PasswordResetViewTest(TestCase):
    """
    Test the password reset view endpoint for valid responses
    """

    def setUp(self):
        """
        Setup test data for password reset view
        """
        self.user = User.objects.create_user(
            username="test_user",
            email="ah_user@mailinator.com",
            password="p@ssW0rddd"
        )
        self.user.save()
        self.password_reset_data = {
            'user': {
                'email': "ah_user@mailinator.com",
            }
        }
        self.invalid_password_reset_data = {
            'user': {
                'email': "invalid@mailinator.com",
            }
        }
        self.invalid_email_password_reset_data = {
            'user': {
                'email': "mailinator.com",
            }
        }
        self.client = APIClient()

    def test_valid_password_reset_request(self):
        """
        Test if user can make a request to reset their password.
        """
        response = self.client.post(
            reverse('authentication:password_reset'),
            self.password_reset_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(PASSWORD_RESET_MSGS['SENT_RESET_LINK'], response.data['message'])

    def test_invalid_user_password_reset_request(self):
        """
        Test if a non-existent user can make a request to reset their password
        """
        response = self.client.post(
            reverse('authentication:password_reset'),
            self.invalid_password_reset_data,
            format='json'
        )
        msg = PASSWORD_RESET_MSGS['SENT_RESET_LINK']
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(msg, response.data['errors'])

    def test_invalid_user_email_password_reset_request(self):
        """
        Test if an invalid user email can make a request to reset their password
        """
        response = self.client.post(
            reverse('authentication:password_reset'),
            self.invalid_email_password_reset_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SetPasswordAPIViewTest(TestCase):
    """
    Test the change password endpoint
    """

    def setUp(self):
        """
        Setup test data for password reset view
        """
        self.user = User.objects.create_user(
            username="test_user",
            email="ah_user@mailinator.com",
            password="p@ssW0rddd"
        )
        self.user.save()
        self.set_password_data = {
            "password_data": {
                "new_password": "Abcd3fg$",
                "confirm_password": "Abcd3fg$"
            }
        }
        self.unmatched_set_password_data = {
            "password_data": {
                "new_password": "Abcd3fq$",
                "confirm_password": "Abcd3fg$"
            }
        }
        self.password_reset_token = PasswordResetTokenHandler().get_reset_token(
            self.user.email
        )
        self.password_reset_token_record = PasswordReset(
            user_id=self.user,
            token=self.password_reset_token
        )
        self.password_reset_token_record.save()
        self.client = APIClient()

    def test_valid_password_set_request(self):
        """
        Test if user can set their new password successfully.
        """
        response = self.client.patch(
            reverse('authentication:password_change',
                    kwargs={'reset_token': self.password_reset_token}
                    ),
            self.set_password_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(PASSWORD_RESET_MSGS['RESET_SUCCESSFUL'], response.data['message'])

    def test_invalid_password_set_request(self):
        """
        Test if user can set their new password.
        If the new password and confirmed password are not the same.
        """
        response = self.client.patch(
            reverse('authentication:password_change',
                    kwargs={'reset_token': self.password_reset_token}
                    ),
            self.unmatched_set_password_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(PASSWORD_RESET_MSGS['UNMATCHING_PASSWORDS'], response.data['errors'])

    def test_reuse_of_reset_link_for_password_set_request(self):
        """
        Test if user can set their new password using a link that was already set.
        """
        response = self.client.patch(
            reverse('authentication:password_change',
                    kwargs={'reset_token': self.password_reset_token}
                    ),
            self.set_password_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(PASSWORD_RESET_MSGS['RESET_SUCCESSFUL'], response.data['message'])

        response = self.client.patch(
            reverse('authentication:password_change',
                    kwargs={'reset_token': self.password_reset_token}
                    ),
            self.set_password_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(PASSWORD_RESET_MSGS['USED_RESET_LINK'], response.data['errors'])
