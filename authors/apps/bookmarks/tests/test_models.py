from django.test import TestCase

from authors.apps.articles.models import Articles
from authors.apps.authentication.models import User
from authors.apps.bookmarks.models import Bookmark


# Create Bookmark model tests here.
class TestBookmarkModel(TestCase):
    """
    Test the Bookmark model functions and methods
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
            'body': 'this article is nice',
            'description': 'this is a description',
            'author': self.user
        }
        self.article = Articles.objects.create(**self.article_data)

        self.bookmark_data = {
            "profile": self.user.profile,
            "article": self.article
        }

    def test_bookmark_model_can_create_bookmark(self):
        """
        Test if we can create a bookmark using the bookmark model class
        """

        bookmark = Bookmark.objects.create(**self.bookmark_data)
        self.assertEqual(bookmark.profile, self.user.profile)

    def test_bookmark_model_string_representation(self):
        """
        Test if the string of the bookmark model returns the expected string
        """
        bookmark = Bookmark.objects.create(**self.bookmark_data)
        username = bookmark.profile.user.username
        article_title = bookmark.article.title
        bm_id = bookmark.id
        rep = "Bookmark - id:{} username: {}, title: {}".format(
            bm_id,
            username,
            article_title
        )
        self.assertIn(str(rep), str(bookmark))
