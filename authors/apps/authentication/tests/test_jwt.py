from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory

from authors.apps.authentication.models import User
from authors.apps.authentication.backends import JWTAuthentication


class JWTAuthenticationTest(TestCase):
    """ Test the JWT Authentication implementation """

    def setUp(self):
        self.user_data = {
            'user': {
                'email': 'user1@mail.com',
                'username': 'user1',
                'password': 'sTr0ng%weR'
            }
        }
        self.user = User.objects.create(
            username='user',
            email='user@mail.com',
            password='password'
        )
        self.user_token = self.user.token
        self.user.save()
        self.client = APIClient()

    def sign_up_user(self):
        res = self.client.post(
            reverse('authentication:register'),
            self.user_data,
            format='json'
        )
        return res

    def test_user_gets_a_token_when_they_sign_up(self):
        """ Users should get a token when they successfully sign up """
        response = self.sign_up_user()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)

    def test_user_gets_a_token_when_they_log_in(self):
        """ Users should get a token when they successfully log in """
        self.sign_up_user()
        response = self.client.post(
            reverse('authentication:login'),
            self.user_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_if_user_passes_valid_token_to_access_secured_endpoint(self):
        """
        Test if a user can access a secured endpoint
        after providing a valid token
        """
        headers = {'HTTP_AUTHORIZATION': f'Bearer {self.user_token}'}
        response = self.client.get(reverse('authentication:get'), **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_failure_if_user_passes_no_token(self):
        """
        Test if a user can access a secured
        endpoint without providing a token
        """
        response = self.client.get(
            reverse('authentication:get')
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data['detail'],
            'Authentication credentials were not provided.'
        )

    def test_failure_if_user_provides_invalid_token(self):
        """ Test if an invalid token can be decoded """
        fake_token = self.user_token + 'invalid'
        headers = {'HTTP_AUTHORIZATION': f'Bearer {fake_token}'}
        response = self.client.get(reverse('authentication:get'), **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data['detail'],
            'Invalid authentication. Could not decode token.'
        )

    def test_failure_if_user_does_not_exist(self):
        """
        We register a user to get the token,
        then delete the user from the database.
        When a user tries to pass the token to access the endpoint,
        they should be forbidden from proceeding.
        """
        test_user = User.objects.create(
            username='test_user',
            email='test_user@mail.com',
            password='password'
        )
        test_token = test_user.token
        test_user.delete()
        client = APIClient()
        headers = {'HTTP_AUTHORIZATION': f'Bearer {test_token}'}
        response = client.get(reverse('authentication:get'), **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data['detail'],
            'No user matching this token was found.'
        )

    def test_failure_because_user_is_inactive(self):
        """ Test if an inactive user can be authenticated """
        inactive_user = User.objects.create(
            username='inactive_one',
            email='inactive@mail.com',
            password='password'
        )
        inactive_user.is_active = False
        inactive_user.save()
        headers = {'HTTP_AUTHORIZATION': f'Bearer {inactive_user.token}'}
        response = self.client.get(reverse('authentication:get'), **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data['detail'],
            'This user has been deactivated.'
        )

    def test_authentication_failure_because_header_is_None(self):
        """ Test if authentication fails when a request has authorization
        headers with a length of 0 """
        jwt_auth = JWTAuthentication()
        factory = APIRequestFactory()
        request = factory.get(reverse('authentication:get'))
        request.META['HTTP_AUTHORIZATION'] = ''
        response = jwt_auth.authenticate(request)
        self.assertEqual(response, None)

    def test_authentication_failure_because_header_length_is_1(self):
        """ Test if authentication fails when a request has authorization
        headers with a length of 1 """
        jwt_auth = JWTAuthentication()
        factory = APIRequestFactory()
        request = factory.get(reverse('authentication:get'))
        request.META['HTTP_AUTHORIZATION'] = 'length'
        response = jwt_auth.authenticate(request)
        self.assertEqual(response, None)

    def test_authentication_failure_if_header_length_is_greater_than_2(self):
        """ Test if authentication fails when a request has authorization
        headers with a length greater than 2 """
        jwt_auth = JWTAuthentication()
        factory = APIRequestFactory()
        request = factory.get(reverse('authentication:get'))
        request.META['HTTP_AUTHORIZATION'] = b'length is greater than 2'
        response = jwt_auth.authenticate(request)
        self.assertEqual(response, None)

    def test_authentication_failure_if_prefixes_mismatch(self):
        """ We unit test our authentication method to see if the method
        returns `None` when the prefixes mismatch """
        jwt_auth = JWTAuthentication()
        factory = APIRequestFactory()
        request = factory.get(reverse('authentication:get'))
        request.META['HTTP_AUTHORIZATION'] = 'Token, {}'.format(
            self.user_token)
        response = jwt_auth.authenticate(request)
        self.assertEqual(response, None)
