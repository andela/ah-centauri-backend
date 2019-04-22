from django.urls import path

from authors.apps.highlights.views import (
    CreateGetDeleteMyHighlightsAPIView
)

app_name = 'bookmarks'

urlpatterns = [

    path('highlights/<slug:slug>/',
         CreateGetDeleteMyHighlightsAPIView.as_view(),
         name='create-get-delete-highlights'),
]
