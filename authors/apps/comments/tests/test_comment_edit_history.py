from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from authors.apps.articles.models import Articles
from authors.apps.authentication.models import User
from authors.apps.comments.models import Comment


class TestCommentEdit(TestCase):

    def setUp(self):
        self.author = User.objects.create_user(
            "tess",
            "tess@email.com",
            "sTr0ng%weR"
        )
        self.author.is_verified = True

        self.reader = User.objects.create_user(
            "reader",
            "reader@email.com",
            "sTr0ng%weR"
        )

        self.reader.is_verified = True

        self.article = Articles.objects.create(
            author=self.author,
            title="The haves and the have nots",
            body="the quick brown fox jumped over the lazy dog"
        )

        self.headers = {'HTTP_AUTHORIZATION': f'Bearer {self.reader.token}'}

        self.client = APIClient()

    def test_creating_comment_creates_history_record(self):
        # setup
        # act
        self.comment = Comment.objects.create(
            article=self.article,
            author=self.reader,
            body="I don't like this article"
        )

        # assert
        self.assertEqual(self.comment.history.count(), 1)

    def test_updating_comment_creates_associated_history_record(self):
        # setup
        # act
        comment = Comment.objects.create(
            article=self.article,
            author=self.reader,
            body="I don't like this article"
        )

        comment_body = "this is an updated comment body"
        comment.body = comment_body
        comment.save()

        # assert
        self.assertEqual(comment.history.count(), 2)
        self.assertEqual(comment.history.most_recent().body, comment_body)
        self.assertEqual(comment.history.earliest().body, "I don't like this article")

    def test_fetch_comments_returns_edit_information(self):
        # setup
        # create some articles and comments on them
        comment = Comment.objects.create(
            article=self.article,
            author=self.reader,
            body="I don't like this article"
        )

        # update comment
        comment.body = "this is an update"
        comment.save()

        # act
        # make api call to fetch some comments
        response = self.client.get(
            reverse("comments:list_comment", args=[self.article.slug, comment.id]))

        data = response.data

        # assert
        # that edited comments come back with edit history
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(data['has_edits'])

    def test_fetch_comment_edits(self):
        # setup
        # create some articles and comments on them
        comment = Comment.objects.create(
            article=self.article,
            author=self.reader,
            body="I don't like this article"
        )

        # update comment
        comment.body = "this is an update"
        comment.save()

        # act
        # make api call to fetch some comments
        response = self.client.get(
            reverse("comments:comment_history", args=[comment.id]), **self.headers)

        data = response.data

        # assert
        # that edited comments come back with edit history
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 2)

    def test_fetching_nonexistent_comment_raises_exception(self):
        # setup
        # make api call to fetch some comments
        response = self.client.get(
            reverse("comments:comment_history", args=[32]), **self.headers)

        data = response.data

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
