from django.test import TestCase
from rest_framework import serializers
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient

from authors.apps.articles.models import Articles
from authors.apps.articles.serializers import ArticleSerializer
from authors.apps.authentication.models import User


class TestArticleSerializer(TestCase):
    """
    TestArticleSerializer Test the article serializer class
    """

    def setUp(self):
        self.client = APIClient()

        self.article = {
            "article": {
                "title": "MS. Found in a bottle",
                "body": "is a very good story",
                "description": "was not written by me",
                "tags": ["bottler"]
            }
        }

        self.invalid_article = {
            "article": {
                "title": "Berenice",
                "description": "was not written by me"
            }
        }

        user_data = {
            "username": "user",
            "email": "user@mail.com",
            "password": "Pa@55Word!"
        }

        self.user = User.objects.create(**user_data)
        self.article_data = {
            'title': 'the quick brown fox',
            'body': 'this article is nice',
            'description': 'this is a description',
            'author': self.user
        }

    def test_articles_have_sharable_social_links(self):
        # setup
        article = Articles.objects.create(**self.article_data)

        # act
        response = self.client.get(
            reverse('articles:article', kwargs={'slug': article.slug}),
            format='json'
        )

        # assert

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn('share_links', response.data)
        self.assertNotEqual({}, response.data['share_links'])

    def test_article_serializer_without_request_context_returns_empty_share_links(self):
        # setup
        article = Articles.objects.create(**self.article_data)

        # act
        serializer = ArticleSerializer(article)

        # assert
        self.assertEqual({}, serializer.data['share_links'])

    def test_article_serializer_validates_invalid_article(self):
        """
        Test if the serializer validate an article
        """
        serializer = ArticleSerializer(data=self.invalid_article["article"])
        self.assertRaises(
            serializers.ValidationError,
            serializer.is_valid,
            raise_exception=True)

    def test_article_serializer_has_read_time(self):
        """
        Test if the serializer validated data has a read time
        """
        serializer = ArticleSerializer(data=self.article["article"])
        serializer.is_valid()
        self.assertIn('min read', serializer.data['read_time'])

    def test_article_serializer_has_tags(self):
        """Test if the serializer data has tags"""
        serializer = ArticleSerializer(data=self.article["article"])
        serializer.is_valid()
        self.assertIn('bottler', serializer.data['tags'])

