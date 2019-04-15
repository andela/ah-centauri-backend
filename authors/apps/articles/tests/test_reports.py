from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from authors.apps.articles.models import Articles, ReportArticles
from authors.apps.authentication.models import User

ARTICLES_URL = reverse('articles:articles')

REPORTS_URL = reverse('articles:reports')

def reports_url(slug):
    """Return reports list URL"""
    return reverse('articles:reports-list', args=[slug])


def report_url(pk):
    """Return report detail URL"""
    return reverse('articles:report-detail', args=[pk])


class RatingsviewsTest(TestCase):
    """ 
    Unit tests for the ratings' views class defined in our views.
    """

    def setUp(self):
        self.user_koko = User.objects.create(
            username='Koko',
            email='Koko@mail.com',
            password='Password123@'
        )
        self.user_koko.is_verified = True
        self.user_koko.save()
        self.user_token = self.user_koko.token

        self.user_Eric = User.objects.create(
            username='Eric',
            email='Eric@mail.com',
            password='password'
        )
        self.user_Eric.is_verified = True
        self.user_Eric.save()
        self.user2_token = self.user_Eric.token

        self.article_two = Articles.objects.create(
            title='the wheels on the bus',
            body='go round and round',
            author=self.user_koko
        )
        self.article_two.save()

        self.article_three = {
            'article': {
                'title': 'alice in wonderland',
                'body': 'life is unfair',
                'description': 'one tree hill'
            }
        }

        self.report = {
            "report" : {
                "report" : "contains vulgar language!",
                "type_of_report" : "Spam"
            }
        }

        self.updated_report = {

            "report": "too erotic for family audience!"
        }

        self.client = APIClient()
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer {self.user_token}'}
        self.headers2 = {'HTTP_AUTHORIZATION': f'Bearer {self.user2_token}'}

    def create_article(self):
        self.article = Articles.objects.create(
            title='the wheels on the bus',
            body='go round and round',
            description='all through the town',
            author=self.user_koko
        )
        self.article.save()
        return self.article

    def create_report(self):
        article = self.create_article()
        self.report = ReportArticles.objects.create(
            report="copied!",
            author=self.user_koko,
            article=article
        )
        self.article_two.save()
        data = [self.report, article.slug, article]
        return data

    def post_article(self):
        response = self.client.post(
            ARTICLES_URL,
            self.article_three,
            **self.headers2,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response

    def test_post_report(self):
        """ test whether a user is able to post a report. """
        article = self.post_article()
        slug = article.data['slug']
        my_url = reports_url(slug)
        response = self.client.post(
            my_url,
            self.report,
            **self.headers,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_edit_report(self):
        """ test whether a user is able to edit a report. """
        report = self.create_report()
        pk = report[0].pk
        my_url = report_url(pk)
        response = self.client.put(
            my_url,
            self.updated_report,
            **self.headers,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_edit_report_no_auth(self):
        """ test whether an unauthenticated user is able to edit a report. """
        report = self.create_report()
        pk = report[0].pk
        my_url = report_url(pk)
        response = self.client.put(
            my_url,
            self.updated_report,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_report(self):
        """ test whether a user is able to delete a report. """
        report = self.create_report()
        pk = report[0].pk
        my_url = report_url(pk)
        response = self.client.delete(
            my_url,
            **self.headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_report_no_auth(self):
        """ test whether an unauthenticated user is able to delete a report. """
        report = self.create_report()
        pk = report[0].pk
        my_url = report_url(pk)
        response = self.client.delete(
            my_url
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_reports(self):
        """ test whether a user is able to get reports of a particular article. """
        self.create_report()
        report = self.create_report()
        slug = report[1]
        my_url = reports_url(slug)
        response = self.client.get(
            my_url,
            **self.headers,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response

    def test_get_reports_of_user(self):
        """ test whether a user is able to get his/her reports. """
        self.create_report()
        report = self.create_report()
        response = self.client.get(
            REPORTS_URL,
            **self.headers,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response

    def test_get_reports_no_rating_found(self):
        """ test whether a user is able to get reports of a particular article if there are no ratings."""
        my_url = reports_url(1)
        response = self.client.get(
            my_url,
            **self.headers,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_reports_no_auth(self):
        """ test whether an unauthenticated user is able to get reports of a particular article. """
        self.create_report()
        report = self.create_report()
        slug = report[1]
        my_url = reports_url(slug)
        response = self.client.get(
            my_url,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)