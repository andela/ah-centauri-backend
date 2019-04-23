from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from authors.apps.articles.models import Articles


class BaseAnalyticsSetup(TestCase):
    """
    Test the Analytics model functions and methods
    """

    def setUp(self):
        """
        Set up dummy data for use in the model
        """
        self.author = get_user_model().objects.create_user(
            username="user",
            email="user@mail.com",
            password="Pa@bbgbh"
        )
        self.author.is_verified = True
        self.author.save()
        self.author2 = get_user_model().objects.create_user(
            username="user2",
            email="user2@mail.com",
            password="Pa@bbgbh"
        )
        self.author2.save()

        self.client = APIClient()

        self.headers = {
            'HTTP_AUTHORIZATION': f'Bearer {self.author.token}'}
        self.headers2 = {
            'HTTP_AUTHORIZATION': f'Bearer {self.author2.token}'}

        self.article = Articles.objects.create(
            author_id=self.author.pk,
            title="the 3 musketeers",
            body="is a timeless story",
            description="not written by me",
            tags=[],
        )
        self.report_views_url = reverse("analytics:my_views")
        self.total_report_views_url = reverse("analytics:total_reads")
        self.report_url = reverse("analytics:update", args=[self.article.slug])
        self.article_url = reverse('articles:article', args=[self.article.slug])

    def get_an_article(self):
        """
        Handles retrieving a specific article.
        :return:
        """
        return self.client.get(self.article_url, **self.headers, format='json')
