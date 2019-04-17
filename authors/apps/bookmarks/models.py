from django.db import models

from authors.apps.core.models import TimeStampModel


class Bookmark(TimeStampModel):
    """
    Bookmark model class to store the bookmarked articles of a user

    Class to provide fields that allow storing fields
    For articles a user has bookmarked
    """
    profile = models.ForeignKey('profiles.Profile',
                                on_delete=models.CASCADE,
                                null=False)
    article = models.ForeignKey('articles.Articles',
                                on_delete=models.CASCADE,
                                null=False)

    class Meta:
        unique_together = (('profile', 'article'),)

    def __str__(self):
        """
        __str__ return relevant fields for a bookmark

        Returns:
            String: A string with the article and user bookmark details
        """
        username = self.profile.user.username
        article_title = self.article.title
        bm_id = self.id
        return "Bookmark - id:{} username: {}, title: {}".format(
            bm_id,
            username,
            article_title
        )
