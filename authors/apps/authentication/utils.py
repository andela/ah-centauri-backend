import os
from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

# Set the host url for the password reset link
host_url = os.environ.get('AH_HOST_URL')
# Set the sender email for the password reset emails
ah_centauri_sender_email = "ah.centauri@gmail.com"
# Set the url path for a password reset
password_reset_urlpath = "password_reset/"


class PasswordResetTokenHandler:
    """
    Class that defines methods used to send emails for password reseting and
    generate password reset tokens 
    """

    @staticmethod
    def send_reset_password_link(token, user, request):
        """
        Method to send the password reset link to a user's email address
        
        Params
        -------
        token: String with the token used to to allow a user
        user: User object for the user who made the password reset request
        
        Returns
        --------
        Boolean:
            True - if the email was sent successfully.
            False - if the email was not sent.
        """
        # Create the password reset link to be sent in the email using the token.
        password_reset_link = f"{request.scheme}://{request.get_host()}/" + password_reset_urlpath + token + "/"
        email_details_context = {
            'username': user.username,
            'password_reset_link': password_reset_link
        }
        # Add the link and username to the password reset email plain text template
        text_content = render_to_string(
            'password_reset/password_reset_email.txt',
            context=email_details_context
        )
        # Add the link and username details to the password reset email html content
        html_content = render_to_string('password_reset/password_reset_email.html', context=email_details_context)

        # Try to send the email to the user
        try:
            subject = 'Authors Haven: Password Reset Link'
            msg = EmailMultiAlternatives(subject, text_content, ah_centauri_sender_email, [user.email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            # send_mail( subject, text_content, ah_centauri_sender_email, [user.email],
            # fail_silently=False,html_message=html_content
            # )
            return True
        except Exception as e:
            return False

    def _generate_password_reset_token(self, user_email, reset_token_days=7):
        """ 
        Password reset token generator to generate a JWT token used to reset the users password
        
        Params
        -------
        user_email: String with the email of the user who made the request
        reset_token_days: Number of days before the token expires
        
        Returns
        --------
        String:
            Token string for the password reset link.
        """
        # Set the expire time of the token to be 7 days (default) from the current date and time
        dt = datetime.now() + timedelta(days=reset_token_days)

        # Create the JWT token for password reset request
        token = jwt.encode({
            'user_email': user_email,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        # Return the string version of the token
        return token.decode('utf-8')

    def get_reset_token(self, user_email, reset_token_days=7):
        """
        Return a generated password reset token
        """
        # Call the private _generate_reset_token and return a token string.
        return self._generate_password_reset_token(user_email, reset_token_days)


from rest_framework import status
from rest_framework.exceptions import APIException


def validate_image(avatar_name):
    """ Validates whether avatar is an image."""
    if avatar_name is None:
        return True

    ok_formats = [
        ".png",
        ".jpg",
        ".jpeg"
    ]

    avatar_name = str(avatar_name)

    if not avatar_name.lower().endswith((*ok_formats,)):
        APIException.status_code = status.HTTP_400_BAD_REQUEST
        raise APIException({"image":
                                "Only '{}', '{}', '{}' files are accepted".format(*ok_formats)})

    # noqa
