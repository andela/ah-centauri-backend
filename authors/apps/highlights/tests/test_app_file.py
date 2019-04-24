from django.apps import apps
from django.test import TestCase

from authors.apps.highlights.apps import HighlightsConfig


class HighlightsConfigTest(TestCase):
    """Test the highlights application in django on file apps.py"""

    def test_apps(self):
        self.assertEqual(HighlightsConfig.name, 'highlights')
        self.assertEqual(apps.get_app_config('highlights').name, 'authors.apps.highlights')
