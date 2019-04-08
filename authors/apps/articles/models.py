import itertools
from django.db import models
from django.utils.text import slugify
from django.db.models import Avg
from django.core.validators import MaxValueValidator, MinValueValidator

from authors.apps.authentication.serializers import UserSerializer

class Articles(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey('authentication.User', related_name='articles', on_delete=models.CASCADE, null=False, default='')
    title = models.CharField(max_length=100, default='')
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    body = models.TextField()
    description = models.CharField(max_length=140, default='')

    def __str__(self):
        return self.title

    def get_unique_slug(self):
        slug = slugify(self.title)
        unique_slug = slug
        num = 1
        while Articles.objects.filter(slug=unique_slug).exists():
            unique_slug = '{}-{}'.format(slug, num)
            num += 1
        return unique_slug
 
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.get_unique_slug()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return 'authors:articles', (self.slug,)
    
    def get_average_rating(self):
        if Ratings.objects.all().count() > 0:
            rating = Ratings.objects.all().aggregate(Avg('value'))
            return round(rating['value__avg'], 1)
        return 0

    def get_author(self):
        user = UserSerializer(self.author)
        author = {
          "username":user.data['profile']['username'],
          "bio":user.data['profile']['bio'],
          "image":user.data['profile']['image']
        }
        return author


    class Meta:
        ordering = ('-created_at',)


# add ratings model
class Ratings(models.Model):
    author = models.ForeignKey('authentication.User', related_name='ratings', on_delete=models.CASCADE, null=False)
    article = models.ForeignKey('articles.Articles', related_name='ratings', on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    value = models.IntegerField(null=False)
    review = models.TextField(blank=True)
    slug = models.SlugField(max_length=140, blank=True)

    def __str__(self):
        return str(self.value)

    class Meta:
        ordering = ('-created_at',)
        unique_together = (('author', 'article'),)


    
