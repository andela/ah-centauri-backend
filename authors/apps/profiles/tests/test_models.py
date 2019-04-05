from django.test import TestCase

from ..models import Profile
from authors.apps.authentication.models import User


class TestProfile(TestCase):
   """ class to test the profile models"""

   def setUp(self):
      """ Setup some code that is used by the unittests"""
      self.email = 'daniel@gmail.com'
      self.username = 'dan1234'
      self.password = 'daniel!!'

      # create a user that will be logged in
      self.user = User.objects.create_user(
         self.username, self.email, self.password)
      self.profile = self.user.profile

   def test_string_representation(self):
      """ test for the value returned by __str__ """
      self.assertEqual(str(self.profile), self.username)
