from django.contrib.auth import get_user_model
from django.test import TestCase

from authors.apps.articles.models import Articles
from authors.apps.comments.models import Comment


class CommentModelTest(TestCase):
    """
    Handles comments model testing
    """

    def setUp(self):
        """
        Setup to create a sample user and articles
        :return:
        """
        self.author = get_user_model().objects.create_user(
            username="user",
            email="user@mail.com",
            password="Pa@bbgbh"
        )
        self.article = Articles.objects.create(
            author_id=self.author.pk,
            title="the 3 musketeers",
            body="is a timeless story",
            description="not written by me"
        )

    def test_comment_str(self):
        """
        Test comment string representation
        :return:
        """
        comment = Comment.objects.create(
            author=self.author,
            article=self.article,
            body="Test comment",
        )
        self.assertEqual(str(comment), "Test comment")
