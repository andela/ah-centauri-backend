import json

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from authors.apps.articles.models import Articles
from authors.apps.authentication.models import User
from authors.apps.bookmarks.response_messages import (
    BOOKMARK_MSGS)


class TestBookmarkViews(TestCase):
    """
    Test the API views used to interact with bookmarks.
    """

    def setUp(self):
        """
        Add dummy data to test the bookmark views.
        """

        self.user_data = {
            "username": "test_user",
            "email": "test_user@mailinator.com",
            "password": "P@ssW0rd!"
        }

        self.user = User.objects.create_user(**self.user_data)
        self.article_data = {
            'title': 'the quick brown fox',
            'body': 'this article is nice',
            'description': 'this is a description',
            'author': self.user
        }
        self.article_data2 = {
            'title': 'New article data',
            'body': 'this article is new',
            'description': 'this is a new description',
            'author': self.user
        }
        self.article = Articles.objects.create(**self.article_data)
        self.article2 = Articles.objects.create(**self.article_data2)
        self.bookmark_data = {
            "profile": self.user.profile,
            "article": self.article
        }

        self.invalid_bookmark_data = {
            "profile": 'profile',
            "article": self.article
        }

        self.user.is_verified = True
        self.user.save()
        self.test_client = APIClient()

    def login_a_user(self):
        """
        Reusable function to login a user
        """
        login_data = {
            "user": {
                "username": self.user_data["username"],
                "email": self.user_data["email"],
                "password": self.user_data["password"]
            }
        }
        response = self.test_client.post(
            "/api/users/login/",
            data=json.dumps(login_data),
            content_type='application/json')
        token = response.json()['user']['token']
        return token

    def create_bookmarks(self):
        """
        Create bookmarks for testing
        """
        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        response = self.test_client.post(
            reverse('bookmarks:create-bookmark',
                    kwargs={"slug": self.article.slug}),
            **headers,
            content_type='application/json',
            data={}
        )
        response = self.test_client.post(
            reverse('bookmarks:create-bookmark',
                    kwargs={"slug": self.article2.slug}),
            **headers,
            content_type='application/json',
            data={}
        )
        return response

    def test_user_can_create_bookmark_view(self):
        """
        Test if a user can bookmark an article
        """

        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        response = self.test_client.post(
            reverse('bookmarks:create-bookmark',
                    kwargs={"slug": self.article.slug}),
            **headers,
            content_type='application/json',
            data={}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            BOOKMARK_MSGS['BOOKMARK_SUCCESSFUL'],
            response.data['message'])

    def test_user_cannot_create_bookmark_with_nonexistent_article(self):
        """
        Test if a user cannot create a bookmark with a nonexistent article
        """

        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        response = self.test_client.post(
            reverse('bookmarks:create-bookmark',
                    kwargs={"slug": 'fake-slug'}),
            **headers,
            content_type='application/json',
            data={}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            BOOKMARK_MSGS['ARTICLE_NOT_FOUND'],
            response.data['errors'])

    def test_user_cannot_create_bookmark_for_an_article_twice(self):
        """
        Test if a user cannot bookmark an article twice
        """

        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        response = self.create_bookmarks()
        response = self.test_client.post(
            reverse('bookmarks:create-bookmark',
                    kwargs={"slug": self.article.slug}),
            **headers,
            content_type='application/json',
            data={}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            BOOKMARK_MSGS['ARTICLE_ALREADY_BOOKMARKED'],
            response.data['errors'])

    def test_user_can_get_all_their_bookmarks(self):
        """
        Test if a user can get all their bookmarked article
        """

        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        response = self.create_bookmarks()
        response = self.test_client.get(
            reverse('bookmarks:list-bookmarks'),
            **headers,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            BOOKMARK_MSGS['BOOKMARKS_FOUND'],
            response.data['message'])

    def test_user_gets_empty_bookmarks_list_if_no_bookmarks_exist(self):
        """
        Test if a user can gets an empty list if no bookmarks exist
        """

        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        response = self.test_client.get(
            reverse('bookmarks:list-bookmarks'),
            **headers,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            BOOKMARK_MSGS['NO_BOOKMARKS'],
            response.data['message'])

    def test_user_can_delete_a_bookmark(self):
        """
        Test if a user can delete bookmarked article
        """

        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        response = self.create_bookmarks()
        article_slug = response.data['bookmark']['article']['slug']
        response = self.test_client.delete(
            reverse('bookmarks:delete-bookmark',
                    kwargs={"pk": response.data['bookmark']['id']}),
            **headers,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            BOOKMARK_MSGS['BOOKMARK_REMOVED'],
            response.data['message'])

    def test_user_cannot_delete_nonexistent_bookmark(self):
        """
        Test if a user cannot delete non-existent bookmark
        """

        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        response = self.create_bookmarks()
        response_deleted = response
        response = self.test_client.delete(
            reverse('bookmarks:delete-bookmark',
                    kwargs={"pk": response.data['bookmark']['id']}),
            **headers,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            BOOKMARK_MSGS['BOOKMARK_REMOVED'],
            response.data['message'])
        response = self.test_client.delete(
            reverse('bookmarks:delete-bookmark',
                    kwargs={"pk": response_deleted.data['bookmark']['id']}),
            **headers,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            BOOKMARK_MSGS['BOOKMARK_NOT_FOUND'],
            response.data['errors'])
