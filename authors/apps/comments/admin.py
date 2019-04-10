from django.contrib import admin

from authors.apps.comments.models import Comment

admin.site.register(Comment)
