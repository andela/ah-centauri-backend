import os
import jwt
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings

host_url = os.environ.get('AH_HOST_URL')
ah_centauri_sender_email = "ah.centauri@gmail.com"
password_reset_urlpath = "password_reset/"

class PasswordResetTokenHandler:
    """
    Class that defines methods used to send emails for password reseting and
    generate password reset tokens 
    """

    @staticmethod
    def send_reset_password_link(token, user_email):
        password_reset_link = host_url+ password_reset_urlpath + token
        reset_email_html_message = """
        We received a password reset request for this email. Please follow the link provided to reset your password
        otherwise ignore this message if you did not make this request.
        <br/>
        <a href="{}">Password Reset Link</a>
        """.format(password_reset_link)
        reset_email_message = """
        We received a password reset request for this email. Please follow the link provided to reset your password
        otherwise ignore this message if you did not make this request.

        {}
        """.format(password_reset_link)
        try:
            subject = 'Authors Haven: Password Reset Link'
            send_mail( subject, reset_email_message, ah_centauri_sender_email, [user_email],
            fail_silently=False,html_message=reset_email_html_message
            )
            return True
        except Exception as e:
            return False
    
    def _generate_password_reset_token(self, user_email, reset_token_days=7):
        """ 
        Password reset token generator to generate a JWT token used to reset the users password
        """

        dt = datetime.now() + timedelta(days=reset_token_days)
        token = jwt.encode({
            'user_email': user_email,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')

    def get_reset_token(self,user_email, reset_token_days=7):
        """
        Return a generated password reset token
        """

        return self._generate_password_reset_token(user_email, reset_token_days)