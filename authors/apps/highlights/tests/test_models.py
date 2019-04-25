from django.test import TestCase

from authors.apps.articles.models import Articles
from authors.apps.authentication.models import User
from authors.apps.highlights.models import Highlights
from authors.apps.highlights.serializers import HighlightSerializer


class TestHighlightsModel(TestCase):
    """
    Test the Highlights model functions and methods
    """

    def setUp(self):
        """
        Set up dummy data for use in the model
        """

        self.user_data = {
            "username": "test_user",
            "email": "test_user@mailinator.com",
            "password": "P@ssW0rd!"
        }

        self.user = User.objects.create_user(**self.user_data)
        self.article_data = {
            'title': 'the quick brown fox',
            'body': """
                this article is nice. It needs more paragraphs and text.
                this article is nice. It needs more paragraphs and text.
                this article is nice. It needs more paragraphs and text.
                this article is nice. It needs more paragraphs and text.
            """,
            'description': 'this is a description',
            'author': self.user
        }
        self.article = Articles.objects.create(**self.article_data)

        self.highlight_data = {
            "profile": self.user.profile,
            "article": self.article,
            "start_index": 0,
            "end_index": 20
        }

    def test_highlight_model_can_create_highlight(self):
        """
        Test if we can create a highlight object using the highlight model class
        """

        highlight = Highlights.objects.create(**self.highlight_data)
        self.assertEqual(highlight.profile, self.user.profile)

    def test_if_profile_can_access_highlights(self):
        """
        Test if the profile returns the highlights a user has made
        :return:
        """
        highlight = Highlights.objects.create(**self.highlight_data)
        highlights = Highlights.objects.filter(profile=self.user.profile)
        self.assertEqual(highlight.profile, self.user.profile)
        serializer = HighlightSerializer(highlights, many=True)
        self.assertEqual(serializer.data, self.user.profile.highlights)

    def test_highlight_model_string_representation(self):
        """
        Test if the string of the highlight model returns the expected string
        """
        highlight = Highlights.objects.create(**self.highlight_data)
        username = highlight.profile.user.username
        article_title = highlight.article.title
        highlight_id = highlight.id
        rep = """
            Highlight - 
            id:{} username: {}, 
            title: {}, 
            start_index: {}, 
            end_index: {}
        """.format(
            highlight_id,
            username,
            article_title,
            highlight.start_index,
            highlight.end_index
        )
        self.assertIn(str(rep), str(highlight))
