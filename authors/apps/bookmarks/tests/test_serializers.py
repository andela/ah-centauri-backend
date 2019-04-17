from django.test import TestCase

from authors.apps.articles.models import Articles
from authors.apps.authentication.models import User
from authors.apps.bookmarks.models import Bookmark
from authors.apps.bookmarks.serializers import BookmarkSerializer


class TestBookmarkSerializer(TestCase):
    """
    Test the bookmark serializer class
    """

    def setUp(self):
        """
        Set up dummy data for use in the serializer
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
        self.article = Articles.objects.create(**self.article_data)

        self.bookmark_data = {
            "profile": self.user.profile,
            "article": self.article
        }

        self.bookmark = Bookmark.objects.create(**self.bookmark_data)

    def test_bookmark_serializer_can_validate_valid_bookmark(self):
        """
        Test if the bookmark serializer properly serializes bookmark data
        """
        serializer = BookmarkSerializer(self.bookmark)
        self.assertEqual(
            self.bookmark_data['article'].author.username,
            serializer.data['article']['author']
        )
