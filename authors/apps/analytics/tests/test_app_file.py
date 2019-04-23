from django.apps import apps
from django.test import TestCase

from authors.apps.analytics.apps import AnalyticsConfig


class AnalyticsConfigTest(TestCase):
    """Test the comment application in django on file apps.py"""

    def test_apps(self):
        self.assertEqual(AnalyticsConfig.name, 'authors.apps.analytics')
        self.assertEqual(apps.get_app_config('analytics').name, 'authors.apps.analytics')
