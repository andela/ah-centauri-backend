from django.urls import path

from .views import (
    LoginAPIView,
    RegistrationAPIView,
    UserRetrieveUpdateAPIView,
    SocialOAuthAPIView,
    PasswordResetAPIView,
    SetPasswordAPIView,
)

app_name = 'authentication'

urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view(), name='get'),
    path('users/', RegistrationAPIView.as_view(), name='register'),
    path('users/login/', LoginAPIView.as_view(), name='login'),
    path('users/social/', SocialOAuthAPIView.as_view(), name='social'),
    path('users/password_reset/', PasswordResetAPIView.as_view(), name='password_reset'),
    path('users/password_reset/<reset_token>/', SetPasswordAPIView.as_view(), name='password_change'),
]
