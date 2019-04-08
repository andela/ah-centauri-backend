from django.urls import path

from authors.apps.articles.views import CreateArticlesAPIView, RetrieveUpdateDeleteArticleAPIView
from authors.apps.articles.views import CreateListRatingsAPIView, RetrieveUpdateDeleteRatingAPIView

app_name = 'articles'

urlpatterns = [
    path('articles/', CreateArticlesAPIView.as_view(), name='articles'),
    path('articles/<slug:slug>/', RetrieveUpdateDeleteArticleAPIView.as_view(), name='article'),
    path('articles/<slug:slug>/ratings/', CreateListRatingsAPIView.as_view(), name='ratings-list'),
    path('articles/ratings/<int:pk>/', RetrieveUpdateDeleteRatingAPIView.as_view(), name='rating-detail')
]