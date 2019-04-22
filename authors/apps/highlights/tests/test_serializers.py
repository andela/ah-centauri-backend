from django.test import TestCase
from rest_framework import serializers

from authors.apps.articles.serializers import ArticleSerializer
from authors.apps.authentication.models import User
from ..serializers import HighlightSerializer


class TestHighlightsSerializer(TestCase):
    """
    Test the Highlights model functions and methods
    """

    def setUp(self):
        """
        Set up dummy data for use in the model
        """

        self.user_data = {
            "username": "test_user",
            "email": "test_user@mailinator.com",
            "password": "P@ssW0rd!"
        }

        self.user = User.objects.create_user(**self.user_data)
        self.article_data = {
            'title': 'the quick brown fox',
            'body': """
                this article is nice. It needs more paragraphs and text.
                this article is nice. It needs more paragraphs and text.
                this article is nice. It needs more paragraphs and text.
                this article is nice. It needs more paragraphs and text.
            """,
            'description': 'this is a description',
            'author': self.user,
            'tags': []
        }
        self.article = ArticleSerializer(data=self.article_data)
        self.article.is_valid()
        self.article = self.article.save(author=self.user)
        self.highlight_data = {
            "profile": self.user.profile,
            "article": self.article,
            "start_index": 0,
            "end_index": 20
        }
        self.invalid_highlight_data = {
            "profile": self.user.profile,
            "article": self.article,
            "start_index": 12,
            "end_index": 1000
        }

    def test_highlight_serializer_can_validate_highlight(self):
        """
        Test if we can validate a highlight object using the highlight serializer class
        """
        highlight = HighlightSerializer(data=self.highlight_data)
        highlight.is_valid()
        self.assertTrue(highlight.is_valid())

    def test_highlight_serializer_with_invalid_highlight(self):
        """
        Test if we can invalidate a highlight
        if the indexes are out of range of the article body length
        """

        highlight = HighlightSerializer(data=self.invalid_highlight_data)
        self.assertRaises(
            serializers.ValidationError,
            highlight.is_valid,
            raise_exception=True)
