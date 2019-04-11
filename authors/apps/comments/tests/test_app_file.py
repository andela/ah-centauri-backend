from django.apps import apps
from django.test import TestCase

from authors.apps.comments.apps import CommentsConfig


class CommentConfigTest(TestCase):
    """Test the comment application in django on file apps.py"""

    def test_apps(self):
        self.assertEqual(CommentsConfig.name, 'authors.apps.comments')
        self.assertEqual(apps.get_app_config('comments').name, 'authors.apps.comments')
