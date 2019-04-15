from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from authors.apps.articles.models import Articles
from authors.apps.authentication.models import User

PROFILES_URL = reverse('articles:author-profile-list')

class AuthorTest(TestCase):
    """ Unit tests for `User` model. """

    def setUp(self):
        self.user_riley = User.objects.create(
            username='Riley',
            email='riley@mail.com',
            password='Password123@'
        )
        self.user_riley.is_verified = True
        self.user_riley.save()
        self.user_token = self.user_riley.token

        self.user_EricK = User.objects.create(
            username='SteveO',
            email=')@mail.com',
            password='password'
        )
        self.user_EricK.save()
        self.user2_token = self.user_EricK.token

        self.client = APIClient()
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer {self.user_token}'}
        self.headers2 = {'HTTP_AUTHORIZATION': f'Bearer {self.user2_token}'}


        self.article = Articles.objects.create(
            author=User.objects.first(),
            title="the 3 musketeers",
            body="is a timeless story",
            description="not written by me"
        )

    def test_get_profiles(self):
        """
        Test whether a user can fetch a list of all authors on the platform
        """
        response = self.client.get(
            PROFILES_URL,
            **self.headers,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data['results']), 1)

    def test_get_profiles_no_auth(self):
        """
        Test whether an unauthenticated user can view authors
        """
        response = self.client.get(
            PROFILES_URL,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_profiles_not_verified(self):
        """
        Test whether an unverified user can view authors
        """
        response = self.client.get(
            PROFILES_URL,
            **self.headers2,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
