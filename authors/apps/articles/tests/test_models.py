from django.test import TestCase

from authors.apps.articles.models import Articles
from authors.apps.authentication.models import User


class ArticleTest(TestCase):
    """ Unit tests for `User` model. """

    def setUp(self):
        self.user = User.objects.create_user(
            username="user",
            email="user@mail.com",
            password="Pa@bbgbh"
        )
        self.article = Articles.objects.create(
            author=User.objects.first(),
            title="the 3 musketeers",
            body="is a timeless story",
            description="not written by me"
        )

    def test_article_string_representation(self):
        """
        Test whether a proper string representation
        of `User` is returned.
        """
        self.assertEqual(str(self.article), "the 3 musketeers")
