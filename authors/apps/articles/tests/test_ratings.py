from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from authors.apps.articles.models import Articles, Ratings
from authors.apps.authentication.models import User

ARTICLES_URL = reverse('articles:articles')


def ratings_url(slug):
    """Return ratings detail URL"""
    return reverse('articles:ratings-list', args=[slug])


def rating_url(pk):
    """Return rating detail URL"""
    return reverse('articles:rating-detail', args=[pk])


class RatingsviewsTest(TestCase):
    """ 
    Unit tests for the ratings' views class defined in our views.
    """

    def setUp(self):
        self.user = User.objects.create(
            username='user',
            email='user@mail.com',
            password='password'
        )
        self.user.is_verified = True
        self.user.save()
        self.user_token = self.user.token

        self.user2 = User.objects.create(
            username='user5',
            email='user5@mail.com',
            password='password'
        )
        self.user2.is_verified = True
        self.user2.save()
        self.user2_token = self.user2.token

        self.article2 = Articles.objects.create(
            title='the wheels on the bus',
            body='go round and round',
            author=self.user
        )
        self.article2.save()

        self.article3 = {
            'article': {
                'title': 'alice in wonderland',
                'body': 'life is unfair',
                'description': 'one tree hill'
            }
        }

        self.rating = {
            "rating": {
                "value": "1",
                "review": "good children's song"
            }
        }

        self.second_rating = {
            "rating": {
                "value": "2",
                "review": "good children's song"
            }
        }

        self.updated_rating = {
            "value": "2",
            "review": "might as well give it a better rating"
        }

        self.client = APIClient()
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer {self.user_token}'}
        self.headers2 = {'HTTP_AUTHORIZATION': f'Bearer {self.user2_token}'}

    def create_article(self):
        self.article = Articles.objects.create(
            title='the wheels on the bus',
            body='go round and round',
            description='all through the town',
            author=self.user
        )
        self.article.save()
        return self.article

    def create_rating(self):
        article = self.create_article()
        self.rating = Ratings.objects.create(
            value='1',
            review='this is a review',
            author=self.user,
            article=article
        )
        self.article2.save()
        data = [self.rating, article.slug, article]
        return data

    def post_article(self):
        response = self.client.post(
            ARTICLES_URL,
            self.article3,
            **self.headers2,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response

    def test_post_rating(self):
        """ test whether a user is able to post a rating. """
        article = self.post_article()
        slug = article.data['slug']
        my_url = ratings_url(slug)
        response = self.client.post(
            my_url,
            self.rating,
            **self.headers,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response

    def test_post_rating_no_auth(self):
        """ test whether an unauthenticated user is able to post a rating. """
        article = self.post_article()
        slug = article.data['slug']
        my_url = ratings_url(slug)
        response = self.client.post(
            my_url,
            self.rating,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        return response

    def test_edit_rating(self):
        """ test whether a user is able to edit a rating. """
        rating = self.create_rating()
        pk = rating[0].pk
        my_url = rating_url(pk)
        response = self.client.put(
            my_url,
            self.updated_rating,
            **self.headers,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response

    def test_edit_rating_no_auth(self):
        """ test whether an unauthenticated user is able to edit a rating. """
        rating = self.create_rating()
        pk = rating[0].pk
        my_url = rating_url(pk)
        response = self.client.put(
            my_url,
            self.updated_rating,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        return response

    def test_delete_rating(self):
        """ test whether a user is able to delete a rating. """
        rating = self.create_rating()
        pk = rating[0].pk
        my_url = rating_url(pk)
        response = self.client.delete(
            my_url,
            **self.headers
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        return response

    def test_delete_rating_no_auth(self):
        """ test whether an unauthenticated user is able to delete a rating. """
        rating = self.create_rating()
        pk = rating[0].pk
        my_url = rating_url(pk)
        response = self.client.delete(
            my_url
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        return response

    def test_get_ratings(self):
        """ test whether a user is able to get ratings of a particular article. """
        self.create_rating()
        rating = self.create_rating()
        slug = rating[1]
        my_url = ratings_url(slug)
        response = self.client.get(
            my_url,
            **self.headers,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response

    def test_get_ratings_not_rating_found(self):
        """ test whether a user is able to get ratings of a particular article if there are no ratings."""
        my_url = ratings_url(1)
        response = self.client.get(
            my_url,
            **self.headers,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        return response

    def test_get_ratings_no_auth(self):
        """ test whether an unauthenticated user is able to get ratings of a particular article. """
        self.create_rating()
        rating = self.create_rating()
        slug = rating[1]
        my_url = ratings_url(slug)
        response = self.client.get(
            my_url,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response

    def test_get_average_rating(self):
        """ test whether average ratings are calculated and returned. """
        self.create_rating()
        rating1 = self.create_rating()
        article = rating1[2]
        avg = article.get_average_rating()
        self.assertEqual(avg, 1)
