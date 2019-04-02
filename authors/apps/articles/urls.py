from django.urls import path

from authors.apps.articles.views import CreateArticlesAPIView, RetrieveUpdateDeleteArticleAPIView

app_name = 'articles'

urlpatterns = [
    path('articles/', CreateArticlesAPIView.as_view(), name='articles'),
    path('article/<slug:slug>/', RetrieveUpdateDeleteArticleAPIView.as_view(), name='article')
]