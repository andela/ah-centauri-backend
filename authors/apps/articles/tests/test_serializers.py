from django.test import TestCase
from rest_framework import serializers
from authors.apps.articles.serializers import ArticleSerializer
from authors.apps.authentication.models import User


class TestArticleSerializer(TestCase):
    """
    TestArticleSerializer Test the article serializer class
    """

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
