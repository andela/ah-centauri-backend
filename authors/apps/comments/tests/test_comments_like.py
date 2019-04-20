from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from authors.apps.articles.models import Articles
from authors.apps.comments.models import Comment


class LikeDislikeComment(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'valerie@gmail.com',
            "valerie_test"
            'T35tP45w0rd'
        )
        self.user.is_verified = True
        self.user.save()
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer {self.user.token}'}
        self.payload = {
            "comment": {
                "body": "His name was my name too."
            }
        }

    def sample_article(self, user_id):
        """
        handle Create a sample article
        :param user_id:
        :return: [Article object]
        """
        return Articles.objects.create(
            author_id=user_id,
            title="the 3 musketeers",
            body="is a timeless story",
            description="not written by me"
        )

    def specific_articles_url(self, slug):
        return reverse("comments:comments", args=[slug])

    def create_comment(self):
        """return Create a comment successfully"""
        article = self.sample_article(user_id=self.user.pk)
        url = self.specific_articles_url(slug=article.slug)
        return self.client.post(url, self.payload, **self.headers, format='json')

    def test_like_a_comment(self):
        """Test that a comment can be liked"""
        comment = self.create_comment()
        res = self.client.post(
            reverse("comments:comment_like", args=[comment.data['id']]),
            **self.headers,
            format='json'
        )
        self.assertEqual(res.data['like_count'], 1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_dislike_a_comment(self):
        """Test that a comment can be disliked"""
        comment = self.create_comment()
        res = self.client.post(
            reverse("comments:comment_dislike", args=[comment.data['id']]),
            **self.headers,
            format='json'
        )
        self.assertEqual(res.data['dislike_count'], 1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
