from django.test import TestCase

from authors.apps.authentication.models import User
from authors.apps.profiles.serializers import GetCurrentUserProfileSerializer


class TestHighlightsSerializer(TestCase):
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
        self.user.is_verified = True
        self.user.save()

    def test_current_user_profile_serializer(self):
        """
        Test if we can validate a highlight object using the highlight serializer class
        """
        user_profile = GetCurrentUserProfileSerializer(self.user.profile)
        self.assertEqual(user_profile.data['username'], self.user.username)
