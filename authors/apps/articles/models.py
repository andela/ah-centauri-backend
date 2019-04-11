import itertools
from django.db import models
from django.utils.text import slugify
from django.db.models import Avg
from django.core.validators import MaxValueValidator, MinValueValidator

from authors.apps.authentication.serializers import UserSerializer
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import Sum
from ..authentication.models import User


class LikeDislikeManager(models.Manager):
    """
    Manager that holds the methods for
    the LikeDislike class
    """
    use_for_related_fields = True

    def likes(self):
        """
        We take the queryset with records greater than 0 because 
        the likes add a negative value
        """
        return self.get_queryset().filter(vote__gt=0).count()

    def dislikes(self):
        """
        We take the queryset with records less than 0 because 
        the dislikes add a negative value
        """
        return self.get_queryset().filter(vote__lt=0).count()


class LikeDislike(models.Model):
    """
    Handles like and dislike of articles
    """
    LIKE = 1
    DISLIKE = -1

    VOTES = (
        (DISLIKE, 'Dislike'),
        (LIKE, 'Like')
    )

    vote = models.SmallIntegerField(verbose_name="vote", choices=VOTES)
    user = models.ForeignKey(User, verbose_name="user",
                             on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    objects = LikeDislikeManager()


class Articles(models.Model):
    likes = GenericRelation(LikeDislike, related_query_name='articles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey('authentication.User', related_name='articles',
                               on_delete=models.CASCADE, null=False, default='')
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


    

 
