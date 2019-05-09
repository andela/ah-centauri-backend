import json
import os

from facebook import GraphAPI, GraphAPIError
from google.auth.transport import requests
from google.oauth2 import id_token
from requests_oauthlib import OAuth1Session


class SocialValidation:
    """Social validation"""

    @staticmethod
    def google_auth_validation(access_token):
        """
        Provides support for verifying `OpenID Connect ID Tokens`_, especially ones
        generated by Google infrastructure.
        Verifies an ID Token issued by Google's OAuth 2.0 authorization server.

        Args:
            id_token (Union[str, bytes]): The encoded token.
            request (google.auth.transport.Request): The object used to make
                HTTP requests.
            audience (str): The audience that this token is intended for. This is
                typically your application's OAuth 2.0 client ID. If None then the
                audience is not verified.

        :param access_token:
        :return: Mapping[str, Any]: The decoded token
        """
        try:
            id_info = id_token.verify_oauth2_token(id_token=access_token,
                                                   request=requests.Request(),
                                                   audience=os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
                                                   )
        except ValueError:
            id_info = None
        return id_info

    @staticmethod
    def facebook_auth_validation(access_token):
        """
        A client for the Facebook Graph API.

        https://developers.facebook.com/docs/graph-api

        The Graph API is made up of the objects in Facebook (e.g., people,
        pages, events, photos) and the connections between them (e.g.,
        friends, photo tags, and event RSVPs). This client provides access
        to those primitive types in a generic way. For example, given an
        OAuth access token, this will fetch the profile of the active user
        and the list of the user's friends:
        :param access_token:
        :return: Mapping[str, Any]: The decoded token
        """
        try:
            graph = GraphAPI(access_token=access_token, version="3.1")
            id_info = graph.request('/me?fields=id,name,email')
        except GraphAPIError:
            id_info = None

        return id_info

    @staticmethod
    def twitter_auth_validation(access_token, access_token_secret):
        """
        Request signing and convenience methods for the oauth dance.

        What is the difference between OAuth1Session and OAuth1?

        OAuth1Session actually uses OAuth1 internally and its purpose is to assist
        in the OAuth workflow through convenience methods to prepare authorization
        URLs and parse the various token and redirection responses. It also provide
        rudimentary validation of responses.

        :param access_token:
        :param access_token_secret:
        :return:
        """
        url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
        try:
            twitter = OAuth1Session(client_key=os.environ.get('SOCIAL_AUTH_TWITTER_KEY'),
                                    client_secret=os.environ.get('SOCIAL_AUTH_TWITTER_SECRET'),
                                    resource_owner_key=access_token,
                                    resource_owner_secret=access_token_secret
                                    )
            response = twitter.get(f'{url}?include_email=true')
            id_info = json.loads(response.text)
        except:
            id_info = None
        return id_info
