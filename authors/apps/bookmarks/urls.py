from django.urls import path

from authors.apps.bookmarks.views import (
    GetBookmarkListAPIView,
    CreateBookmarkAPIView,
    DeleteBookmarkAPIView,
)

app_name = 'bookmarks'

urlpatterns = [
    path('bookmarks/',
         GetBookmarkListAPIView.as_view(),
         name='list-bookmarks'),
    path('bookmarks/<int:pk>/',
         DeleteBookmarkAPIView.as_view(),
         name='delete-bookmark'),
    path('bookmarks/<slug:slug>/',
         CreateBookmarkAPIView.as_view(),
         name='create-bookmark'),
]
