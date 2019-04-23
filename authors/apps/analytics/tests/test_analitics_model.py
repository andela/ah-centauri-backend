from authors.apps.analytics.models import ReadsReport
from authors.apps.analytics.tests.baseSetup import BaseAnalyticsSetup


class TestAnalyticsModel(BaseAnalyticsSetup):
    """
    Test the Analytics model functions and methods
    """

    def test_analytics_model_can_create_report(self):
        """
        Test if we can create a report using the report model class
        """
        report = ReadsReport.objects.create(user=self.author, article=self.article)

        self.assertEqual(report.article, self.article)

    def test_report_model_string_representation(self):
        """
        Test if the string of the report model returns the expected string
        """
        report = ReadsReport.objects.create(user=self.author, article=self.article)

        rep = f'{report.article.slug} viewed by {report.user.username}: ' \
            f'read entire article == {report.full_read}'

        self.assertIn(str(rep), str(report))
