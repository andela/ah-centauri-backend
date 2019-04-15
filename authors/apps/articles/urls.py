from django.urls import path

from authors.apps.articles.views import CreateArticlesAPIView, RetrieveUpdateDeleteArticleAPIView, FavoriteView, GetUserFavoritesView
from authors.apps.articles.views import CreateListRatingsAPIView, RetrieveUpdateDeleteRatingAPIView, LikesView
from authors.apps.articles.views import CreateListReportsAPIView, RetrieveUpdateDeleteReportAPIView, ListReportsAPIView
from .models import Articles, LikeDislike

app_name = 'articles'

urlpatterns = [
    path('articles/', CreateArticlesAPIView.as_view(), name='articles'),
    path('articles/<slug:slug>/',
         RetrieveUpdateDeleteArticleAPIView.as_view(), name='article'),
    path('articles/<slug:slug>/ratings/',
         CreateListRatingsAPIView.as_view(), name='ratings-list'),
    path('articles/ratings/<int:pk>/',
         RetrieveUpdateDeleteRatingAPIView.as_view(), name='rating-detail'),
    path('articles/<slug:slug>/like/',
         LikesView.as_view(model=Articles, vote_type=LikeDislike.LIKE),
         name='article_like'),
    path('articles/<slug:slug>/dislike/',
         LikesView.as_view(model=Articles, vote_type=LikeDislike.DISLIKE),
         name='article_dislike'),
    path('articles/favorites/me/', GetUserFavoritesView.as_view(), name="get_favorites"),
    path('articles/<slug:slug>/favorite/', FavoriteView.as_view(), name="favorite"),
    path('reports/articles/',
         ListReportsAPIView.as_view(), name='reports'),
    path('articles/<slug:slug>/reports/',
         CreateListReportsAPIView.as_view(), name='reports-list'),
    path('articles/reports/<int:pk>/',
         RetrieveUpdateDeleteReportAPIView.as_view(), name='report-detail'),

]
