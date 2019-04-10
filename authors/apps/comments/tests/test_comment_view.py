from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from authors.apps.articles.models import Articles
from authors.apps.comments.models import Comment
from authors.apps.comments.serializers import CommentSerializer
from authors.apps.comments.response_messages import COMMENTS_MSG


def sample_article(user_id):
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


def sample_comment(author, article):
    """
    Handle Create sample comment
    :param author:
    :param article:
    :return: [comment object]
    """
    return Comment.objects.create(
        author=author,
        article=article,
        body="Test comment",
    )


def specific_articles_url(slug):
    return reverse("comments:comments", args=[slug])


def specific_comment_url(slug, comment_id):
    return reverse('comments:list_comment', args=[slug, comment_id])


class PublicCommentAPiTest(TestCase):
    """
    Test unauthorized api access
    """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            "test_user"
            'T35tP45w0rd'
        )
        self.user.is_verified = True
        self.user.save()
        self.client = APIClient()

    def test_retrieve_comments(self):
        """Test that authorization is not required to view"""
        article = sample_article(user_id=self.user.pk)
        sample_comment(author=self.user, article=article)

        url = specific_articles_url(slug=article.slug)
        res = self.client.get(url)

        comments = Comment.objects.all().order_by('created_at')
        serializers = CommentSerializer(comments, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializers.data)

    def test_retrieve_comment_if_article_is_invalid(self):
        """Test retrieving and article where the article is not found"""
        url = specific_articles_url(slug="Not_valid_article")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(res.data, {'errors': COMMENTS_MSG['ARTICLE_DOES_NOT_EXIST']})

    def test_auth_required_to_create_comment(self):
        """Test unauthorized user can not post"""
        article = sample_article(user_id=self.user.pk)
        payload = {
            "comment": {
                "body": "His name was my name too."
            }
        }
        url = specific_articles_url(slug=article.slug)
        res = self.client.post(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PrivateCommentApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            "test_user"
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

    def create_comment(self):
        """return Create a comment successfully"""
        article = sample_article(user_id=self.user.pk)
        url = specific_articles_url(slug=article.slug)
        return self.client.post(url, self.payload, **self.headers, format='json')

    def test_create_comment_successfully(self):
        """Test authorized user can post"""
        res = self.create_comment()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_comment_invalid_article(self):
        """Test that a user can not comment on a non existing article"""
        url = specific_articles_url(slug="not_valid_slug")
        res = self.client.post(url, self.payload, **self.headers, format='json')

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(res.data, {"errors": COMMENTS_MSG['ARTICLE_DOES_NOT_EXIST']})

    def test_get_specific_comment(self):
        """Test user can view multiple comments"""
        comment = self.create_comment()

        url = specific_comment_url(slug=comment.data['article'], comment_id=comment.data['id'])
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_specific_comment_not_found(self):
        """Test user can not view a comment that does not exist"""
        comment = self.create_comment()

        url = specific_comment_url(slug=comment.data['article'], comment_id='5')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(res.data, {"errors": COMMENTS_MSG['COMMENT_DOES_NOT_EXIST']})

    def test_get_specific_comment_invalid_article_slug(self):
        """Test user can not view comment of an article if article is not found"""
        comment = self.create_comment()

        url = specific_comment_url(slug="invalid-article-slug", comment_id=comment.data['id'])
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(res.data, {"errors": COMMENTS_MSG['ARTICLE_DOES_NOT_EXIST']})

    def test_reply_to_comment_successfully(self):
        """test user can reply to a specific comment successfully"""
        comment = self.create_comment()

        url = specific_articles_url(slug=comment.data['article'])
        self.payload.get('comment')['parent'] = comment.data['id']
        res = self.client.post(url, self.payload, **self.headers, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_reply_to_comment_invalid_article(self):
        """Test that a user can not comment on a non existing article"""
        comment = self.create_comment()

        url = specific_articles_url(slug="not_valid_slug")
        self.payload.get('comment')['parent'] = comment.data['id']
        res = self.client.post(url, self.payload, **self.headers, format='json')

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(res.data, {"errors": COMMENTS_MSG['ARTICLE_DOES_NOT_EXIST']})

    def test_can_partial_update_comment_successfully(self):
        """Test updating a comment with 'PATCH'"""
        article = sample_article(user_id=self.user.pk)
        comment = sample_comment(author=self.user, article=article)
        payload = {
            "comment": {
                "body": "His name was not my name!"
            }
        }

        url = specific_comment_url(slug=comment.article.slug, comment_id=comment.pk)
        res = self.client.patch(url, payload, **self.headers, format='json')

        comment.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(comment.body, payload['comment']['body'])

    def test_can_partial_update_comment_invalid_article_slug(self):
        """Test user can not update comment of an article if article is not found"""
        article = sample_article(user_id=self.user.pk)
        comment = sample_comment(author=self.user, article=article)
        payload = {
            "comment": {
                "body": "His name was not my name!"
            }
        }

        url = specific_comment_url(slug="invalid-article-slug", comment_id=comment.pk)
        res = self.client.patch(url, payload, **self.headers, format='json')

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(res.data, {"errors": COMMENTS_MSG['ARTICLE_DOES_NOT_EXIST']})

    def test_can_partial_update_comment_not_found(self):
        """Test user can not update comment of an article if comment is not found"""
        article = sample_article(user_id=self.user.pk)
        comment = sample_comment(author=self.user, article=article)
        payload = {
            "comment": {
                "body": "His name was not my name!"
            }
        }

        url = specific_comment_url(slug=comment.article.slug, comment_id='5')
        res = self.client.patch(url, payload, **self.headers, format='json')

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(res.data, {"errors": COMMENTS_MSG['COMMENT_DOES_NOT_EXIST']})

    def test_cannot_partial_update_others_comment_successfully(self):
        """test comment author can not delete other authors comments"""
        user = get_user_model().objects.create_user(
            'test2@gmail.com',
            "test_user2"
            'T35tP45w0rd'
        )
        user.is_verified = True
        user.save()

        comment = self.create_comment()
        payload = {
            "comment": {
                "body": "His name was not my name!"
            }
        }

        url = specific_comment_url(slug=comment.data['article'], comment_id=comment.data['id'])
        res = self.client.patch(url, payload, **{'HTTP_AUTHORIZATION': f'Bearer {user.token}'}, format='json')

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(res.data, {
            "detail": "You do not have permission to perform this action."
        })

    def test_can_delete_own_comment_successfully(self):
        """test comment author can delete own comment"""
        comment = self.create_comment()

        url = specific_comment_url(slug=comment.data['article'], comment_id=comment.data['id'])
        res = self.client.delete(url, **self.headers)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertDictEqual(res.data, {"message": COMMENTS_MSG['DELETE_SUCCESS']})

    def test_cannot_delete_others_comment_successfully(self):
        """test comment author can not delete other authors comments"""
        user = get_user_model().objects.create_user(
            'test2@gmail.com',
            "test_user2"
            'T35tP45w0rd'
        )
        user.is_verified = True
        user.save()

        comment = self.create_comment()

        url = specific_comment_url(slug=comment.data['article'], comment_id=comment.data['id'])
        res = self.client.delete(url, **{'HTTP_AUTHORIZATION': f'Bearer {user.token}'})

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(res.data, {
            "detail": "You do not have permission to perform this action."
        })

    def test_cannot_delete_others_comment_invalid_article_slug(self):
        """Test user can not update comment of an article if article is not found"""
        user = get_user_model().objects.create_user(
            'test2@gmail.com',
            "test_user2"
            'T35tP45w0rd'
        )
        user.is_verified = True
        user.save()

        comment = self.create_comment()

        url = specific_comment_url(slug="invalid-article-slug", comment_id=comment.data['id'])
        res = self.client.delete(url, **{'HTTP_AUTHORIZATION': f'Bearer {user.token}'})

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(res.data, {"errors": COMMENTS_MSG['ARTICLE_DOES_NOT_EXIST']})

    def test_cannot_delete_others_comment_not_found(self):
        """Test user can not update comment of an article if comment is not found"""
        user = get_user_model().objects.create_user(
            'test2@gmail.com',
            "test_user2"
            'T35tP45w0rd'
        )
        user.is_verified = True
        user.save()

        comment = self.create_comment()

        url = specific_comment_url(slug=comment.data['article'], comment_id='5')
        res = self.client.delete(url, **{'HTTP_AUTHORIZATION': f'Bearer {user.token}'})

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(res.data, {"errors": COMMENTS_MSG['COMMENT_DOES_NOT_EXIST']})
