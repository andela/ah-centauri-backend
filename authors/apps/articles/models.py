import itertools

from django.db import models
from django.utils.text import slugify


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

    def _get_unique_slug(self):
        slug = slugify(self.title)
        unique_slug = slug
        num = 1
        while Articles.objects.filter(slug=unique_slug).exists():
            unique_slug = '{}-{}'.format(slug, num)
            num += 1
        return unique_slug
 
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return 'authors:articles', (self.slug,)


    class Meta:
        ordering = ('-created_at',)