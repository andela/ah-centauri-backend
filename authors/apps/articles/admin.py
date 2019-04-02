from django.contrib import admin

# Register your models here.
from authors.apps.articles.models import Articles

admin.site.register(Articles)