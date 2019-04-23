from django.db import models

from authors.apps.articles.models import Articles
from authors.apps.authentication.models import User
from authors.apps.core.models import TimeStampModel


class ReadsReport(TimeStampModel):
    """
    Implement Views Stats model
    Display no of users who clicked on an article.
    """
    article = models.ForeignKey(Articles, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Shows if user has read the entire article.
    full_read = models.BooleanField(default=False)

    def __str__(self):
        """
        ReadReport String representation
        :return:
        """
        return f'{self.article.slug} viewed by {self.user.username}: ' \
            f'read entire article == {self.full_read}'

    class Meta:
        ordering = ['created_at']
