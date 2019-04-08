from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from authors.apps.authentication.models import User
from authors.apps.articles.models import Articles


class ArticlesBaseTest(APITestCase):
    """Sets up tests for features related to articles"""

    def setUp(self):
        client = APIClient()
        self.user1 = User.objects.create(
            username='Kamar', email="dante@gmail.com", password='password')
        self.user1_token = self.user1.token
        self.user1.is_verified = True
        self.user1.save()
        self.user2 = User.objects.create(
            username='Dan', email='dankamar@gmail.com', password='password')
        self.user2_token = self.user2.token
        self.user2.is_verified = True
        self.user2.save()
        self.header_user1 = {
            'HTTP_AUTHORIZATION': f'Bearer {self.user1_token}'
        }
        self.header_user2 = {
            'HTTP_AUTHORIZATION': f'Bearer {self.user2_token}'
        }
        
        self.article1 = Articles.objects.create(
            title='the wheels on the bus',
            body='go round and round',
            author=self.user1
        )
        self.article1.save()

        #Publish article
        retrieved_article = Articles.objects.filter(slug=self.article1.slug).first()
        retrieved_article.published = True
        retrieved_article.save()
        self.favorite_article_url = '/api/articles/{}/favorite/'.format(self.article1.slug)
        self.get_favorites_url = reverse('articles:get_favorites')