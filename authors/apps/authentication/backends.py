import jwt

from django.conf import settings

from rest_framework import authentication, exceptions

from .models import User


class JWTAuthentication(authentication.BaseAuthentication):
    auth_header_prefix = 'Bearer'

    def authenticate(self, request):
        """
        The `authenticate` method is called on every request.

        Authentication can either be successful or not.

        When successful, the method returns a user/token combination.

        When not successful, i.e, when we encounter errors,
        we raise the `AuthenticationFailed` exception.

        When we do not wish to authenticate, e.g. when no authentication
        credentials are provided we return None.

        """

        request.user = None

        # get auth_header from request
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.auth_header_prefix.lower()

        # Do not attempt to authenticate
        if not auth_header or len(auth_header) != 2:
            return None

        # We have to decode both the prefix and token
        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix:
            return None

        # delegate the actual authentication to the method below
        # since we are sure we have an auth header that is the correct
        # length and that has the proper prefix
        return self.authenticate_credentials(request, token)

    def authenticate_credentials(self, request, token):
        """
        Authenticate the given credentials, if successful, 
        return a user/token combination, otherwise, throw an error.
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
        except:
            msg = 'Invalid authentication. Could not decode token.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = User.objects.get(pk=payload['id'])
        except User.DoesNotExist:
            msg = 'No user matching this token was found.'
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = 'This user has been deactivated.'
            raise exceptions.AuthenticationFailed(msg)

        return (user, token)


