from django.urls import path

from .views import (
    LoginAPIView,
    RegistrationAPIView,
    UserRetrieveUpdateAPIView,
    PasswordResetAPIView,
    SetPasswordAPIView,
    VerifyEmailView,
    NotificationsView,
    NotificationSettingsView,
    VerifyEmailView,
    GoogleAuthAPIView,
    FacebookAuthAPIView,
    TwitterAuthAPIView,
)

app_name = 'authentication'

urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view(), name='get'),
    path('users/', RegistrationAPIView.as_view(), name='register'),
    path('users/login/', LoginAPIView.as_view(), name='login'),
    path('users/password_reset/',
         PasswordResetAPIView.as_view(), name='password_reset'),
    path('users/password_reset/<reset_token>/',
         SetPasswordAPIView.as_view(), name='password_change'),
    path('verify-email/<token>/<uidb64>/',
         VerifyEmailView.as_view(), name='verify'),
    path('me/notifications', NotificationsView.as_view(), name='notifications'),
    path('notification/settings', NotificationSettingsView.as_view(), name='notification_settings')
    path('users/google/', GoogleAuthAPIView.as_view(), name='google'),
    path('users/facebook/', FacebookAuthAPIView.as_view(), name='facebook'),
    path('users/twitter/', TwitterAuthAPIView.as_view(), name='twitter'),
]
