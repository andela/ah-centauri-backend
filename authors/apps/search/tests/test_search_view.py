from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from authors.apps.articles.models import Articles


def sample_article(user_id):
    """
    handle Create a sample article
    :param user_id:
    :return: [Article object]
    """
    return Articles.objects.create(
        author_id=user_id,
        title="the 3 musketeers",
        body="is a timeless story",
        description="not written by me",
        tags=['musk', "three", "teers"]
    )


def sample_user(name):
    """
    handle Create a sample user
    :return: [User object]
    """
    user = get_user_model().objects.create_user(
        f'{name}@gmail.com',
        f'user_{name}',
        'T35tP45w0rd'
    )
    user.is_verified = True
    user.save()
    return user


ARTICLE_SEARCH_URL = reverse('articles:search')


class PublicCommentAPiTest(TestCase):
    """
    Test unauthorized api access
    """

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_article_search_by_author(self):
        """Test that can Filter by author"""
        user1 = sample_user("one")
        user2 = sample_user("two")
        sample_article(user_id=user1.pk)
        sample_article(user_id=user2.pk)

        res = self.client.get(f'{ARTICLE_SEARCH_URL}?author={user1.username}')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_article_search_by_title(self):
        """Test that can Filter by title"""
        user1 = sample_user("one")
        user2 = sample_user("two")
        article = sample_article(user_id=user1.pk)
        sample_article(user_id=user2.pk)

        res = self.client.get(f'{ARTICLE_SEARCH_URL}?title={article.title}')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_article_search_by_favorite(self):
        """Test that can Filter by favorited by user"""
        user1 = sample_user("one")
        user2 = sample_user("two")
        sample_article(user_id=user1.pk)
        sample_article(user_id=user2.pk)

        res = self.client.get(f'{ARTICLE_SEARCH_URL}?favorited={user1.username}')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_article_search_by_tags(self):
        """Test that can Filter by favorited by user"""
        user1 = sample_user("one")
        user2 = sample_user("two")
        article = sample_article(user_id=user1.pk)
        sample_article(user_id=user2.pk)

        res = self.client.get(f'{ARTICLE_SEARCH_URL}?tags={article.tags}')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_article_search_by_title_and_author(self):
        """Test that can Filter by title and author"""
        user1 = sample_user("one")
        user2 = sample_user("two")
        article = sample_article(user_id=user1.pk)
        sample_article(user_id=user2.pk)

        res = self.client.get(f'{ARTICLE_SEARCH_URL}?author={user1.username}'
                              f'&title={article.title}')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_article_search_by_title_and_author_favourite(self):
        """Test that can Filter by title and author"""
        user1 = sample_user("one")
        user2 = sample_user("two")
        article = sample_article(user_id=user1.pk)
        sample_article(user_id=user2.pk)

        res = self.client.get(f'{ARTICLE_SEARCH_URL}?author={user1.username}'
                              f'&title={article.title}&favorited={user1.username}')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_article_search_by_title_and_author_favourite_and_tags(self):
        """Test that can Filter by title and author"""
        user1 = sample_user("one")
        user2 = sample_user("two")
        article = sample_article(user_id=user1.pk)
        sample_article(user_id=user2.pk)

        res = self.client.get(f'{ARTICLE_SEARCH_URL}?author={user1.username}'
                              f'&title={article.title}&favorited={user1.username}'
                              f'&tags={article.tags}')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
