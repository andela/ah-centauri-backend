from django.urls import path

from authors.apps.comments.views import RetrieveCommentAPIView, RetrieveUpdateDeleteCommentAPIView

app_name = 'comments'

urlpatterns = [
    path('articles/<slug:slug>/comments/', RetrieveCommentAPIView.as_view(), name='comments'),
    path('articles/<slug:slug>/comments/<int:id>/', RetrieveUpdateDeleteCommentAPIView.as_view(), name='list_comment'),
]
