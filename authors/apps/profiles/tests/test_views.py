import json

from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status

from authors.apps.articles.models import Articles
from authors.apps.authentication.models import User
from authors.apps.highlights.models import Highlights
from authors.apps.profiles.models import CustomFollows
from authors.apps.profiles.response_messages import (
    FOLLOW_USER_MSGS,
    get_followers_found_message)
from authors.apps.profiles.utils import get_follow_username_list


class TestProfileViews(TestCase):
    def setUp(self):
        """ Funtion to setup some code that will be needed for unittests """
        self.email = 'daniel@gmail.com'
        self.username = 'testuser123'
        self.password = 'testpass123'

        # create a user that will be logged in
        self.user = User.objects.create_user(
            self.username, self.email, self.password)

        # verify a user's account and save
        self.user.is_verified = True
        self.user.save()

        self.data = {
            'user': {
                'username': self.username,
                'email': self.email,
                'password': self.password,
            }
        }
        self.updated_data = {

            'username': "kamar",
            'email': "daniel1@email.com",
            'password': "testpass1",
            'bio': 'i like mountain hiking'

        }
        self.errornious_updated_data = {
            "website": "notavalidurlforasite"
        }
        self.image_link = {
            "image": "dogs.jpg"
        }
        self.bad_image_link = {
            "image": "dogs.rar"
        }

        self.test_client = Client()

        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}

    def login_a_user(self):
        """
        Reusable function to login a user
        """

        response = self.test_client.post(
            "/api/users/login/", data=json.dumps(self.data),
            content_type='application/json')
        token = response.json()['user']['token']
        return token

    def register_user(self, user_details_dict):
        """ Register a new user to the system
        Args:
            user_details_dict: a dictionary with username, email,
            password of the user
        Returns: an issued post request to the user registration endpoint
        """
        return self.test_client.post(
            "/api/users/", data=json.dumps(user_details_dict),
            content_type='application/json')

    @property
    def token(self):
        return self.login_a_user()

    def test_retrieve_profile(self):
        """ test for the retrive profile endpoint """
        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        response = self.test_client.get(
            "/api/profiles/{}/".format(self.username), **headers,
            content_type='application/json')

        self.assertEqual(response.status_code, 200)

    def test_retrieve_current_user_profile(self):
        """ test for the retrieve my profile endpoint """
        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        new_article = Articles.objects.create(
            title="Time in a tree.",
            description="Raleigh Ritchie",
            body="Stuck on repeat",
            author=self.user
        )
        new_article.save()
        Highlights.objects.create(
            start_index=2,
            end_index=8,
            profile=self.user.profile,
            article=new_article
        ).save()
        response = self.test_client.get(
            reverse('profiles:my_profile'), **headers,
            content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_update_existing_profie(self):
        """ test for updating exisiting user profile"""
        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        self.register_user(self.data)
        response = self.test_client.put(
            "/api/user/", **headers, content_type='application/json',
            data=json.dumps(self.updated_data))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['user']['email'], "daniel1@email.com")
        self.assertEqual(response.json()['user']['username'], "kamar")
        self.assertEqual(
            response.json()['user']['profile']['bio'], 'i like mountain hiking')

    def test_list_all_profiles(self):
        """ test for checking if app returns all available profiles """
        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        response = self.client.get(
            "/api/profiles/", **headers, content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_get_non_existing_profile(self):
        """ test for checking if app catches non-existing profile error """
        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        response = self.client.get(
            "/api/profiles/serdgddddadscw/",
            **headers,
            content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()['profile']['detail'],
            "The requested profile does not exist.")

    def test_if_renderer_catches_errors(self):
        """ test is an error is caught by profile json renderer """
        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        self.register_user(self.data)
        response = self.test_client.put(
            "/api/user/", **headers, content_type='application/json',
            data=json.dumps(self.errornious_updated_data))
        self.assertEqual(response.json()['errors']['profile']['website'], [
            "Enter a valid URL."])

    def test_if_image_uploads_successfully(self):
        """ test if an profile image uploads successfully """
        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        self.register_user(self.data)
        response = self.test_client.put(
            "/api/user/", **headers, content_type='application/json',
            data=json.dumps(self.image_link))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['user']['profile']['image_url'],
                         "https://res.cloudinary.com/daniel2019/image/upload/c_fill,h_150,w_100/dogs")

    def test_if_one_can_upload_pdf_as_profile_image(self):
        """ test if an profile image uploads successfully """
        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        self.register_user(self.data)
        response = self.test_client.put(
            "/api/user/", **headers, content_type='application/json',
            data=json.dumps(self.bad_image_link))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['user']['image'],
                         "Only '.png', '.jpg', '.jpeg' files are accepted")


class TestProfileFollowView(TestCase):
    """

    """

    def setUp(self, ):
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
        self.user3 = {
            "email": "user_new3@mailinator.com",
            "username": "usernew3",
            "password": "P@55worD$"
        }
        # Create new users to follow each other.
        self.new_user1 = User.objects.create_user(**self.user1)
        self.new_user2 = User.objects.create_user(**self.user2)
        self.new_user3 = User.objects.create_user(**self.user3)
        self.new_user1.is_verified = True
        self.new_user2.is_verified = True
        self.new_user3.is_verified = True
        self.new_user1.save()
        self.new_user2.save()
        self.new_user3.save()
        self.user1_profile = self.new_user1.profile
        self.user2_profile = self.new_user2.profile
        self.test_client = Client()
        self.data = {
            'user': {
                'username': self.user1["username"],
                'email': self.user1["email"],
                'password': self.user1["password"]
            }
        }

    def login_a_user(self):
        """
        Reusable function to login a user
        """

        response = self.test_client.post(
            "/api/users/login/",
            data=json.dumps(self.data),
            content_type='application/json')
        token = response.json()['user']['token']
        return token

    def test_user_can_follow_another_user(self):
        """
        Test if a user can follow another user from the view endpoint
        """
        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        response = self.test_client.post(
            reverse('profiles:follow_user',
                    kwargs={'username': self.new_user2.username}
                    ), **headers,
            content_type='application/json',
            data=json.dumps({})
        )
        response = self.test_client.post(
            reverse('profiles:follow_user',
                    kwargs={'username': self.new_user3.username}
                    ), **headers,
            content_type='application/json',
            data=json.dumps({})
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            FOLLOW_USER_MSGS['USER_FOLLOW_SUCCESSFUL'],
            response.data['message'])

    def test_user_can_unfollow_another_user(self):
        """
        Test if a user can unfollow another user from the view endpoint
        """
        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        response = self.test_client.post(
            reverse('profiles:follow_user',
                    kwargs={'username': self.new_user2.username}
                    ), **headers,
            content_type='application/json',
            data=json.dumps({})
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            FOLLOW_USER_MSGS['USER_FOLLOW_SUCCESSFUL'],
            response.data['message'])
        response = self.test_client.delete(
            reverse('profiles:follow_user',
                    kwargs={'username': self.new_user2.username}
                    ), **headers,
            content_type='application/json'
        )
        self.assertEqual(
            FOLLOW_USER_MSGS['USER_UNFOLLOW_SUCCESSFUL'],
            response.data['message'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.test_client.delete(
            reverse('profiles:follow_user',
                    kwargs={'username': 'mkmk'}
                    ), **headers,
            content_type='application/json'
        )
        self.assertEqual(
            FOLLOW_USER_MSGS['USER_NOT_FOUND'],
            response.data['errors'])
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_follow_themselves(self):
        """
        Test if a user can follow themselves
        """
        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        response = self.test_client.post(
            reverse('profiles:follow_user',
                    kwargs={'username': self.new_user1.username}
                    ), **headers,
            content_type='application/json',
            data=json.dumps({})
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            FOLLOW_USER_MSGS['CANNOT_FOLLOW_SELF'],
            response.data['errors']
        )

    def test_user_cannot_follow_non_existent(self):
        """
        Test if a user cannot follow non-existent
        """
        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        response = self.test_client.post(
            reverse('profiles:follow_user',
                    kwargs={'username': "dsadsdsa"}
                    ), **headers,
            content_type='application/json',
            data=json.dumps({})
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )
        self.assertEqual(
            FOLLOW_USER_MSGS['USER_NOT_FOUND'],
            response.data['errors']
        )

    def test_user_cannot_unfollow_users_they_dont_follow(self):
        """
        Test if a user can unfollow users they do not follow
        """
        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        response = self.test_client.delete(
            reverse('profiles:follow_user',
                    kwargs={'username': self.new_user2.username}
                    ), **headers,
            content_type='application/json',
            data=json.dumps({})
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            FOLLOW_USER_MSGS['USER_UNFOLLOWED_ALREADY'],
            response.data['errors']
        )

    def test_user_cannot_unfollow_themselves(self):
        """
        Test if a user can follow themselves
        """
        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        response = self.test_client.delete(
            reverse('profiles:follow_user',
                    kwargs={'username': self.new_user1.username}
                    ), **headers,
            content_type='application/json',
            data=json.dumps({})
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            FOLLOW_USER_MSGS['CANNOT_UNFOLLOW_SELF'],
            response.data['errors']
        )

    def test_user_can_retrieve_other_users_followers(self):
        """
        Test if a user can view followers of other users
        """
        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        response = self.test_client.get(
            reverse('profiles:follow_user',
                    kwargs={'username': self.new_user1.username}
                    ), **headers,
            content_type='application/json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            get_followers_found_message(self.new_user1.username),
            response.data['message']
        )
        response = self.test_client.get(
            reverse('profiles:follow_user',
                    kwargs={'username': "kmimim"}
                    ), **headers,
            content_type='application/json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )
        self.assertEqual(
            FOLLOW_USER_MSGS['USER_NOT_FOUND'],
            response.data['errors']
        )

    def test_user_can_retrieve_their_followers(self):
        """
        Test if a user can view followers of other users
        """
        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        response = self.test_client.get(
            reverse('profiles:my_following'), **headers,
            content_type='application/json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            FOLLOW_USER_MSGS['MY_FOLLOWERS_SUCCESSFUL'],
            response.data['message']
        )
        user_instance = User.objects.get(id=self.new_user1.id)

    def test_get_followers_found_message(self):
        """
        Test if function returns a string
        with accurate username and message
        """
        username = self.new_user1.username
        self.assertEqual(
            get_followers_found_message(username),
            f"Here are the users {username} follows and is followed by."
        )

    def test_get_user_following_username_list(self):
        """
        Test we can return current user's followers and following
        """
        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        response = self.test_client.post(
            reverse('profiles:follow_user',
                    kwargs={'username': self.new_user2.username}
                    ), **headers,
            content_type='application/json',
            data=json.dumps({})
        )
        response = self.test_client.post(
            reverse('profiles:follow_user',
                    kwargs={'username': self.new_user3.username}
                    ), **headers,
            content_type='application/json',
            data=json.dumps({})
        )
        user_following = CustomFollows.objects.filter(
            from_profile_id=self.new_user1.profile.id
        )
        user_followers_set = CustomFollows.objects.filter(
            to_profile_id=self.new_user2.profile.id,
        )
        user_following = get_follow_username_list(user_following)
        user_followers = get_follow_username_list(
            user_followers_set,
            followers=True)
        user_dets2 = {
            "username": self.new_user2.username,
            "email": self.new_user2.email
        }
        user_dets1 = {
            "username": self.new_user1.username,
            "email": self.new_user1.email
        }
        self.assertIn(user_dets2, user_following)
        self.assertIn(user_dets1, user_followers)
