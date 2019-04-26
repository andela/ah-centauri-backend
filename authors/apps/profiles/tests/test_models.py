from django.test import TestCase

from authors.apps.authentication.models import User
from authors.apps.profiles.models import CustomFollows


class TestProfile(TestCase):
    """ class to test the profile models"""

    def setUp(self):
        """ Setup some code that is used by the unittests"""
        self.email = 'daniel@gmail.com'
        self.username = 'dan1234'
        self.password = 'P@55worD$'

        # create a user that will be logged in
        self.user = User.objects.create_user(
            self.username, self.email, self.password)
        self.profile = self.user.profile

    def test_string_representation(self):
        """ test for the value returned by __str__ """
        self.assertEqual(str(self.profile), self.username)


class TestCustomFollow(TestCase):
    """
    Test to verify the functionality of the CustomFollow table.
    """

    def setUp(self):
        """ Setup users for testing the CustomFollow Functionality"""
        self.user1 = {
            "email": "user_new1@mailinator.com",
            "username": "usernew1",
            "password": "P@55worD$"
        }
        self.user2 = {
            "email": "user_new2@mailinator.com",
            "username": "usernew2",
            "password": "P@55worD$"
        }
        # Create new users to follow each other.
        self.new_user1 = User.objects.create_user(**self.user1)
        self.new_user2 = User.objects.create_user(**self.user2)
        self.user1_profile = self.new_user1.profile
        self.user2_profile = self.new_user2.profile

    def test_user_can_follow_another_user(self):
        """
        Test if users can follow each other
        """
        # Make user1 follow user2
        self.user1_profile.follows.add(self.user2_profile)
        follow_record = CustomFollows.objects.get(
            to_profile_id=self.user2_profile.id
        )
        self.assertEqual(follow_record.to_profile_id, self.user2_profile.id)

    def test_user_can_unfollow_another_user(self):
        """
        Test if users can unfollow each other
        """
        # Make user1 follow user2
        self.user1_profile.follows.add(self.user2_profile)
        follow_record = CustomFollows.objects.get(
            to_profile_id=self.user2_profile.id
        )
        self.assertEqual(follow_record.to_profile_id, self.user2_profile.id)
        self.user1_profile.follows.remove(self.user2_profile)
        self.assertRaises(
            CustomFollows.DoesNotExist,
            CustomFollows.objects.get,
            to_profile_id=self.user2_profile.id
        )

    def test_user_can_follow_another_user_using_model(self):
        """
        Test if we can use the CustomFollows model
        to follow users
        """
        # Make user1 unfollow user2
        self.user1_profile.follows.add(self.user2_profile)
        follow_record = CustomFollows.objects.get(
            to_profile_id=self.user2_profile.id
        )
        self.assertEqual(follow_record.to_profile_id, self.user2_profile.id)
        self.user1_profile.follows.remove(self.user2_profile)
        self.assertRaises(
            CustomFollows.DoesNotExist,
            CustomFollows.objects.get,
            to_profile_id=self.user2_profile.id
        )

    def test_user_can_get_their_highlights(self):
        """
        Test that a user can get their article highlights as a profile property
        :return:
        """
        self.assertEqual([], self.user1_profile.highlights)
