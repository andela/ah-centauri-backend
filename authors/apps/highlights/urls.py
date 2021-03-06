from django.urls import path

from authors.apps.highlights.views import (
    CreateGetDeleteMyHighlightsAPIView,
    GetAllMyHighlightsAPIView,
    UpdateMyHighlightsAPIView,
    GetAllHighlightsForArticleAPIView)

app_name = 'bookmarks'

urlpatterns = [
    path('highlights/', GetAllMyHighlightsAPIView.as_view(),
         name='get-all-highlights'),

    path('highlights/<int:pk>/',
         UpdateMyHighlightsAPIView.as_view(),
         name='update-highlights'),
    path('highlights/<slug:slug>/',
         CreateGetDeleteMyHighlightsAPIView.as_view(),
         name='create-get-delete-highlights'),
    path('highlights/<slug:slug>/all/', GetAllHighlightsForArticleAPIView.as_view(),
         name='get-all-public-highlights'),
]
