"""authors URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import (include,
                         path, )
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

...

schema_view = get_schema_view(
    openapi.Info(
        title="Authors Heaven API",
        default_version='v1',
        description="A social platform for the creative at heart.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@authorsheaven.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('admin/', admin.site.urls),
    path('api/', include('authors.apps.authentication.urls', namespace='authentication')),
    path('api/', include('authors.apps.profiles.urls', namespace='profiles')),
    path('api/', include('authors.apps.articles.urls', namespace='articles')),
    path('api/', include('authors.apps.comments.urls', namespace='comments')),
    path('api/', include('authors.apps.bookmarks.urls', namespace='bookmarks')),
    path('api/', include('authors.apps.highlights.urls', namespace='highlights')),
    path('api/', include('authors.apps.analytics.urls', namespace='analytics')),
]
