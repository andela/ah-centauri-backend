from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
                                                
from authors.apps.articles.models import Articles, LikeDislike
from simple_history.models import HistoricalRecords

from authors.apps.articles.models import Articles
from authors.apps.authentication.models import User
from authors.apps.core.models import TimeStampModel


class Comment(TimeStampModel):
    """
    Handles adding comments a specified article
    """
    article = models.ForeignKey(Articles, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField(max_length=255, null=False, blank=False)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    likes = GenericRelation(LikeDislike, related_query_name='comments')
    history = HistoricalRecords()

    def __str__(self):
        """
        Model string representation
        :return: model body
        """
        return self.body

    class Meta:
        ordering = ('-created_at',)

    def children(self):
        """
        Handles retrieving all comments linked to the parent object on a specific article.
        :return: [comments]
        """
        return Comment.objects.filter(article=self.article, parent=self)
