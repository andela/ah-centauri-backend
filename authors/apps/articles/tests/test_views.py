from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from authors.apps.authentication.models import User

ARTICLES_URL = reverse('articles:articles')


def article_url(slug):
    """Return article detail URL"""
    return reverse('articles:article', args=[slug])


def like_url(slug):
    """Return like url"""
    return reverse('articles:article_like', args=[slug])


def dislike_url(slug):
    """Return like url"""
    return reverse('articles:article_dislike', args=[slug])


class ViewTest(TestCase):
    """ Unit tests for the create/list view class defined in our views. """

    # any authenticated user should be able to create an article
    # any visitor to the site should be able to view all articles

    def setUp(self):
        self.article = {
            "article": {
                "title": "MS. Found in a bottle",
                "body": "is a very good story",
                "description": "was not written by me"
            }
        }

        self.invalid_article = {
            "article": {
                "title": "Berenice",
                "description": "was not written by me"
            }
        }

        self.user = User.objects.create(
            username='user',
            email='user@mail.com',
            password='password'
        )
        self.user_token = self.user.token
        self.user.is_verified = True
        self.user.save()

        self.user2 = User.objects.create(
            username='user2',
            email='user2@mail.com',
            password='password'
        )
        self.user2_token = self.user2.token
        self.user2.is_verified = True
        self.user2.save()
        self.client = APIClient()
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer {self.user_token}'}
        self.headers1 = {'HTTP_AUTHORIZATION': f'Bearer {self.user2_token}'}

    def test_create_article_method(self):
        response = self.client.post(
            ARTICLES_URL,
            self.article,
            **self.headers,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response

    def test_create_article_no_auth(self):
        response = self.client.post(
            ARTICLES_URL,
            self.article,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_article_invalid_data(self):
        response = self.client.post(
            ARTICLES_URL,
            self.invalid_article,
            **self.headers,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_articles_method(self):
        response = self.client.get(
            ARTICLES_URL
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_an_article(self):
        response = self.test_create_article_method()
        slug = response.data['slug']
        my_url = article_url(slug)
        respo1 = self.client.get(
            my_url,
            **self.headers,
            format='json'
        )
        self.assertEqual(respo1.status_code, status.HTTP_200_OK)

    def test_get_an_article_does_not_exist(self):
        slug = "article-does-not-exist"
        my_url = article_url(slug)
        respo1 = self.client.get(
            my_url,
            **self.headers,
            format='json'
        )
        self.assertEqual(respo1.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_an_article(self):
        response = self.test_create_article_method()
        slug = response.data['slug']
        my_url = article_url(slug)
        response1 = self.client.put(
            my_url,
            self.invalid_article,
            **self.headers,
            format='json'
        )
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

    def test_update_an_article_not_yours(self):
        response = self.client.post(
            ARTICLES_URL,
            self.article,
            **self.headers1,
            format='json'
        )
        slug = response.data['slug']
        my_url = article_url(slug)
        response1 = self.client.put(
            my_url,
            self.invalid_article,
            **self.headers,
            format='json'
        )
        self.assertEqual(response1.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_an_article_not_yours(self):
        response = self.client.post(
            ARTICLES_URL,
            self.article,
            **self.headers1,
            format='json'
        )
        slug = response.data['slug']
        my_url = article_url(slug)
        response1 = self.client.delete(
            my_url,
            self.invalid_article,
            **self.headers,
            format='json'
        )
        self.assertEqual(response1.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_an_article_no_auth(self):
        response = self.test_create_article_method()
        slug = response.data['slug']
        my_url = article_url(slug)
        response1 = self.client.put(
            my_url,
            self.invalid_article,
            format='json'
        )
        self.assertEqual(response1.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_article_does_not_exist(self):
        slug = "article-does-not-exist"
        my_url = article_url(slug)
        response = self.client.put(
            my_url,
            self.invalid_article,
            **self.headers,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_an_article(self):
        response = self.test_create_article_method()
        slug = response.data['slug']
        my_url = article_url(slug)
        response1 = self.client.delete(
            my_url,
            self.invalid_article,
            **self.headers,
            format='json'
        )
        self.assertEqual(response1.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_an_article_no_auth(self):
        response = self.test_create_article_method()
        slug = response.data['slug']
        my_url = article_url(slug)
        response1 = self.client.delete(
            my_url,
            self.invalid_article,
            format='json'
        )
        self.assertEqual(response1.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_article_does_not_exist(self):
        slug = "article-does-not-exist"
        my_url = article_url(slug)
        response = self.client.delete(
            my_url,
            self.invalid_article,
            **self.headers,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LikeViewTest(ViewTest):
    """Tests for like and dislike"""

    def test_like_an_article(self):
        """Test that an article can be liked"""
        self.client.post(
            ARTICLES_URL,
            self.article,
            **self.headers,
            format='json'
        )
        res = self.client.post(
            like_url('ms-found-in-a-bottle'),
            **self.headers,
            format='json'
        )
        self.assertEqual(res.data['like_count'], 1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_dislike_an_article(self):
        """Test that an article can be disliked"""
        self.client.post(
            ARTICLES_URL,
            self.article,
            **self.headers,
            format='json'
        )
        res = self.client.post(
            dislike_url('ms-found-in-a-bottle'),
            **self.headers,
            format='json'
        )
        self.assertEqual(res.data['dislike_count'], 1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_second_user_likes(self):
        """Tests that a second user can like"""
        self.client.post(
            ARTICLES_URL,
            self.article,
            **self.headers,
            format='json'
        )
        self.client.post(
            like_url('ms-found-in-a-bottle'),
            **self.headers,
            format='json'
        )
        res = self.client.post(
            like_url('ms-found-in-a-bottle'),
            **self.headers1,
            format='json'
        )
        self.assertEqual(res.data['like_count'], 2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_second_user_dislikes(self):
        """Tests that another user can dislike and the dislikes accumulates"""
        self.client.post(
            ARTICLES_URL,
            self.article,
            **self.headers,
            format='json'
        )
        self.client.post(
            dislike_url('ms-found-in-a-bottle'),
            **self.headers,
            format='json'
        )
        res = self.client.post(
            dislike_url('ms-found-in-a-bottle'),
            **self.headers1,
            format='json'
        )
        self.assertEqual(res.data['dislike_count'], 2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
