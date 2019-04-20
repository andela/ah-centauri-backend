from django.urls import path

from authors.apps.comments.views import RetrieveCommentAPIView, RetrieveUpdateDeleteCommentAPIView
from authors.apps.articles.models import LikeDislike
from authors.apps.articles.views import LikesView
from .models import Comment

app_name = 'comments'

urlpatterns = [
    path('articles/<slug:slug>/comments/', RetrieveCommentAPIView.as_view(), name='comments'),
    path('articles/<slug:slug>/comments/<int:id>/', RetrieveUpdateDeleteCommentAPIView.as_view(), name='list_comment'),
    path('articles/comments/<int:id>/like/', LikesView.as_view(model=Comment, vote_type=LikeDislike.LIKE), name='comment_like'),
    path('articles/comments/<int:id>/dislike/', LikesView.as_view(model=Comment, vote_type=LikeDislike.DISLIKE), name='comment_dislike')
]
