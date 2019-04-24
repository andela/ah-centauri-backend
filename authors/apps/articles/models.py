from django.contrib.contenttypes.fields import (GenericForeignKey,
                                                GenericRelation, )
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Avg
from django.utils.text import slugify
from taggit.managers import TaggableManager

from authors.apps.core.models import TimeStampModel
from authors.apps.profiles.models import Profile
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

    @property
    def article(self):
        return self.articles.first()


class Articles(TimeStampModel):
    likes = GenericRelation(LikeDislike, related_query_name='articles')
    author = models.ForeignKey('authentication.User', related_name='articles',
                               on_delete=models.CASCADE, null=False, default='')
    title = models.CharField(max_length=100, default='')
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    body = models.TextField()
    description = models.CharField(max_length=140, default='')
    tags = TaggableManager()

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
        profile = Profile.objects.get(user=self.author)
        author = {
            "username": profile.get_username,
            "bio": profile.bio,
            "image": profile.get_cloudinary_url
        }
        return author

    @property
    def favoriters(self):
        queryset = Favorite.objects.filter(article_id=self)
        favoriters = []
        for favoriter in queryset:
            profile = Profile.objects.get(user=favoriter.user_id)
            favoriters.append(profile.get_username)
        return favoriters

    class Meta:
        ordering = ('-created_at',)


# add ratings model
class Ratings(TimeStampModel):
    author = models.ForeignKey('authentication.User', related_name='ratings', on_delete=models.CASCADE, null=False)
    article = models.ForeignKey('articles.Articles', related_name='ratings', on_delete=models.CASCADE, null=False)
    value = models.IntegerField(null=False)
    review = models.TextField(blank=True)
    slug = models.SlugField(max_length=140, blank=True)

    def __str__(self):
        return str(self.value)

    class Meta:
        ordering = ('-created_at',)
        unique_together = (('author', 'article'),)


class Favorite(models.Model):
    """Implement storage of favorites"""
    user_id = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='favorites')
    article_id = models.ForeignKey('articles.articles', on_delete=models.CASCADE, related_name='favorites')


class ReportArticles(TimeStampModel):
    """ Model to hold instances of reports posted by users. """
    PLAGIARISM = 'plagiarism'
    SPAM = 'spam'
    HARASSMENT = 'harassment'
    RULES_VIOLATION = 'rules violation'
    REPORT_CHOICES = (
        (PLAGIARISM, 'plagiarism'),
        (SPAM, 'spam'),
        (HARASSMENT, 'harassment'),
        (RULES_VIOLATION, 'rules violation'),
    )
    author = models.ForeignKey('authentication.User', related_name='reports', on_delete=models.CASCADE, null=False)
    article =  models.ForeignKey('articles.Articles', related_name='reports', on_delete=models.CASCADE, null=False)
    report = models.CharField(max_length=140)
    type_of_report = models.CharField(
        max_length=20,
        choices=REPORT_CHOICES,
        default=''
    )

    def __str__(self):
        return self.report

    class Meta:
        ordering = ('-created_at',)

