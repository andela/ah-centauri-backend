import os

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

AUTH_URL = reverse('authentication:social')


class SocialAuthTest(APITestCase):
    """
    Base tet class for social authentication
    """

    def setUp(self):
        self.client = APIClient()

    def authenticate(self, provider=os.environ.get('SOCIAL_PROVIDER'),
                     access_token_secret=os.environ.get('ACCESS_TOKEN_SECRET'),
                     access_token=os.environ.get('ACCESS_TOKEN')):
        payload = {
            'access_token': access_token,
            'provider': provider,
            "access_token_secret": access_token_secret
        }
        return self.client.post(AUTH_URL, payload)

    # def test_user_authenticated_successfully(self):
    #     """test user is authenticated successfully with all
    #     correct parameters"""
    #     res = self.authenticate()
    #
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_provider_not_in_payload(self):
        """Test that the OAuth provider is included in request."""
        res = self.authenticate(provider='')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_provider(self):
        """Test given a none existent provider, should only be
            google-oauth2, facebook, twitter
        """
        res = self.authenticate(provider='google')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(res.data, {
            "errors": "Provider not supported, Please use 'google-oauth2','facebook', or 'twitter'."
        })

    def test_invalid_access_token_in_payload(self):
        """Test tha OAuth access token is provided"""
        res = self.authenticate(access_token='dgfhdf',
                                access_token_secret='gfdtetrtr')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(res.data, {
            "errors": "Your credentials aren't allowed"
        })
