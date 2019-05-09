import re

from django.core import mail
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from bs4 import BeautifulSoup as Soup


class EmailTest(TestCase):
    """ Test the Email verification implementation """

    def setUp(self):
        """Sets up the dependencies for the tests"""
        self.user_data = {
            'user': {
                'email': 'Steve@mail.com',
                'username': 'Steve',
                'password': 'Password#1'
            }
        }

        self.client = APIClient()

    def sign_up_user(self):
        """Signs up a user"""
        res = self.client.post(
            reverse('authentication:register'),
            self.user_data,
            format='json'
        )
        return res

    def get_links(self, text):
        html = Soup(text, 'html.parser')
        link = html.find_all('a')[0]['href']

        return link.split('/')

    def test_email_sent(self):
        """Tests that a verification email is sent"""
        response = self.sign_up_user()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(mail.outbox), 1)

    def test_can_verify_mail(self):
        """Tests if the verification link works"""
        res = self.sign_up_user()

        url_string = self.get_links(mail.outbox[0].body)
        url = url_string[-2] + '/' + url_string[-1]

        url = reverse('authentication:verify',
                      kwargs={'token': url_string[-2], 'uidb64': url_string[-1]})
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual("Email successfully verified", res.data['message'])

    def test_cannot_verify_twice_with_same_link(self):
        """Tests that the verification link cannot be used twice"""
        self.sign_up_user()

        url_string = self.get_links(mail.outbox[0].body)
        url = url_string[-2] + '/' + url_string[-1]

        url = reverse('authentication:verify',
                      kwargs={'token': url_string[-2], 'uidb64': url_string[-1]})
        res = self.client.get(url)

        self.client.get(url)
        invalid_res = self.client.get(url)

        self.assertEqual(invalid_res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual("Verification link has expired",
                         invalid_res.data['message'])

    def test_cannot_verify_with_invalid_link(self):
        """Tests that an invalid verification link cannot be used"""
        res = self.sign_up_user()
        invalid_url = reverse('authentication:verify', kwargs={
                      'token': 'faketoken', 'uidb64': '24782937492'})
        res = self.client.get(invalid_url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
