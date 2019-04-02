from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from social_django.utils import load_backend, load_strategy

from social_core.backends.oauth import BaseOAuth1, BaseOAuth2
from social_core.exceptions import MissingBackend

from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer,
    RegistrationSerializer,
    UserSerializer,
    SocialOAuthSerializer
)


class RegistrationAPIView(APIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        token = serializer.instance.token
        return Response({'token': token, 'message': "you have successfully signed up!"}, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        user_object = serializer.validated_data['user']
        token = user_object.token
        return Response({'token': token, 'message': "you have successfully logged in!"}, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        # Here is that serialize, validate, save pattern we talked about
        # before.
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class SocialOAuthAPIView(CreateAPIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    # Login via social accounts
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = SocialOAuthSerializer

    def create(self, request, *args, **kwargs):
        """
        Overide 'create' instead of 'perform-create' to access request
        the request is necessary for 'load_strategy'

        :param request:
        :return:
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        provider = serializer.data.get('provider', None)

        # Check to see if social account is from an authenticated user
        authenticated_user = request.user if not request.user.is_anonymous else None
        # By loading `request` to `load_strategy` `social-app-auth-django`
        # will know to use Django
        strategy = load_strategy(request)

        # Getting the backend that associates the user's social auth provider
        # eg Facebook, Twitter and Google
        try:
            backend = load_backend(strategy=strategy, name=provider, redirect_uri=None)
            if isinstance(backend, BaseOAuth1):
                # Twitter uses OAuth1 and requires an access_token_secret
                # to be passed in the authentication
                token = {
                    'oauth_token': serializer.data['access_token'],
                    'oauth_token_secret': serializer.data['access_token_secret']
                }
            elif isinstance(backend, BaseOAuth2):
                # OAuth implicit grant type which is used for web
                # and mobile application, all we have to pass here is
                # an access_token
                token = serializer.data['access_token']
        except MissingBackend:
            return Response({
                'errors': "Provider not supported, Please use 'google-oauth2',"
                          "'facebook', or 'twitter'."""
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # if authenticated_user is None, social_auth_app will create a new user
            # else social account will be associated with the user that is passed in.
            user = backend.do_auth(token, user=authenticated_user)

        except BaseException:
            # you cannot associate a social account with more than one user
            return Response({
                'errors': "Your credentials aren't allowed"
            }, status=status.HTTP_400_BAD_REQUEST)

        if user and user.is_active:
            user.is_verified = True
            user.save()
            serializer = UserSerializer(user)
            serializer.instance = user

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'errors': "Social authentication error"},
                            status=status.HTTP_400_BAD_REQUEST)

