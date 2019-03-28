from django.urls import path

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView
)

<<<<<<< HEAD
app_name = 'authentication'
=======
app_name='authentication'
>>>>>>> 164829189-refactor: update code

urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view(), name='get'),
    path('users/', RegistrationAPIView.as_view(), name='register'),
    path('users/login/', LoginAPIView.as_view(), name='login'),
]
