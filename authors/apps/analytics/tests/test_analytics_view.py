from django.urls import reverse
from rest_framework import status

from authors.apps.analytics.response_messages import REPORT_MSG
from authors.apps.analytics.tests.baseSetup import BaseAnalyticsSetup


class PublicCommentAPiTest(BaseAnalyticsSetup):
    """
    Test unauthorized api access
    """

    def test_auth_required_to_view_user_stats(self):
        """Test unauthorized user can not view user statistics"""
        res = self.client.get(self.report_views_url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PrivateCommentApiTest(BaseAnalyticsSetup):
    """
    Test authorized api access
    """

    def test_access_analytics_endpoint(self):
        """
        Tests user can view all articles viewed or read
        :return:
        """
        res = self.client.get(self.report_views_url, **self.headers, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_access_analytics_endpoint_if_user_email_is_not_verified(self):
        """
        Tests user can not view all articles viewed or read if not verified
        :return:
        """
        res = self.client.get(self.report_views_url, **self.headers2, format='json')

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


    def test_user_can_view_his_reading_starts(self):
        """
        Test can view article user has viewed
        :return:
        """
        article = self.get_an_article()

        res = self.client.get(self.report_views_url, **self.headers, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['user'], self.author.username)
        self.assertEqual(res.data[0]['article']['slug'], self.article.slug)

    def test_user_can_update_article_stats(self):
        """
        Test can update on reading an article
        :return:
        """
        article = self.get_an_article()

        payload = {
            "full_read": True}

        res = self.client.patch(self.report_url, payload, **self.headers, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['full_read'])

    def test_user_can_not_unread_an_article(self):
        """
        Test can not unread an article
        :return:
        """
        article = self.get_an_article()

        payload = {
            "full_read": False}
        res = self.client.patch(self.report_url, payload, **self.headers, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['errors'], REPORT_MSG['CAN_NOT_UNREAD'])

    def test_can_not_update_report_if_article_is_invalid(self):
        """Test retrieving and article where the article is not found"""
        url = reverse("analytics:update", args=["Not_valid_article"])
        payload = {
            "full_read": True
        }
        res = self.client.patch(url, payload, **self.headers, format='json')

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(res.data, {
            'errors': REPORT_MSG['ARTICLE_DOES_NOT_EXIST']})

    def test_user_can_not_update_article_stats_as_read_if_already_read(self):
        """
        Test can not update an already read article.
        :return:
        """
        article = self.get_an_article()

        payload = {
            "full_read": True
        }

        res = self.client.patch(self.report_url, payload, **self.headers, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['full_read'])

        res1 = self.client.patch(self.report_url, payload, **self.headers, format='json')
        self.assertEqual(res1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(res1.data, {
            "errors": REPORT_MSG['REPORT_UPTO_DATE']})

    def test_user_can_not_update_article_stats_as_read_if_not_viewed(self):
        """
        Test can not update an article if user has not viewed the article.
        :return:
        """
        payload = {
            "full_read": True
        }

        res = self.client.patch(self.report_url, payload, **self.headers, format='json')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(res.data, {
            "errors": REPORT_MSG['READS_REPORT_DOES_NOT_EXIST']})

    def test_get_all_views_of_my_article(self):
        """
        Tests user can not view all articles viewed or read if not verified
        :return:
        """
        res = self.client.get(self.total_report_views_url, **self.headers, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
