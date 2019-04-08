from rest_framework import status
from .favorites_base_test import ArticlesBaseTest
from authors.apps.articles.views import *


class FavoriteArticleTestCase(ArticlesBaseTest):
    """Test favoriting an article functionality"""

    def test_favorite_article(self):
        """Test favorite article"""
        response = self.client.post(
            self.favorite_article_url, **self.header_user1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Test already favorited article
        response1 = self.client.post(self.favorite_article_url,
                                    **self.header_user1)
        detail = "Article already in favorites."
        self.assertEqual(response1.data.get('errors'), detail)
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        # Test invalid slug
        response2 = self.client.post(self.invalid_favorite_url,
                                    **self.header_user1, format='json')
        self.assertEqual(response2.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_favorite(self):
        """Test get favorite"""
        response = self.client.get(self.favorite_article_url,
                                   **self.header_user1)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.client.post(self.favorite_article_url,
                         **self.header_user1, format='json')
        response1 = self.client.get(
            self.favorite_article_url, **self.header_user1)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        # Test invalid slug
        response2 = self.client.get(self.invalid_favorite_url,
                                   **self.header_user1)
        detail = "This article has not been found."
        self.assertEqual(response2.data.get('errors'), detail)
        self.assertEqual(response2.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_favorites(self):
        """Test get favorites endpoint"""
        self.client.post(self.favorite_article_url, **self.header_user1)
        response = self.client.get(self.get_favorites_url,
                                   **self.header_user1)
        self.assertEqual(len(response.data.get('favorites')), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_favorite(self):
        """Test delete favorite"""
        # test delete favorite that does not exist
        response = self.client.delete(
            self.favorite_article_url, **self.header_user1)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.client.post(self.favorite_article_url,
                         **self.header_user1)

        response1 = self.client.get(
            self.favorite_article_url, **self.header_user1)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        response2 = self.client.delete(
            self.favorite_article_url, **self.header_user1)
        self.assertEqual(response2.status_code, status.HTTP_204_NO_CONTENT)
        # Test with non existent slug
        response3 = self.client.delete(self.invalid_favorite_url,
                                   **self.header_user1)
        detail = "This article has not been found."
        self.assertEqual(response3.data.get('errors'), detail)
        self.assertEqual(response3.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_favorite_article_not_found(self):
        """Test favorite non existent article."""
        response = self.client.post(self.invalid_favorite_url,
                                    **self.header_user1, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
