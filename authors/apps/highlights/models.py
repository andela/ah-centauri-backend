from django.db import models

from authors.apps.core.models import TimeStampModel


class Highlights(TimeStampModel):
    """
    Model that stores and manipulates relation for highlights
    """

    profile = models.ForeignKey('profiles.Profile',
                                on_delete=models.CASCADE,
                                null=False)
    article = models.ForeignKey('articles.Articles',
                                on_delete=models.CASCADE,
                                null=False
                                )
    # String index for the start of the highlighted text.
    start_index = models.IntegerField(null=False)
    # String index for the end of the highlighted string text.
    end_index = models.IntegerField(null=False)
    # User comment to go along with the highlight
    comment = models.TextField(max_length=500, default="")

    class Meta:
        """
        Make sure the article id, start and end index of string are unique as a combination.
        This reduces duplication of the highlights
        """
        unique_together = (('profile', 'article', 'start_index', 'end_index'),)

    def __str__(self):
        """
        __str__ return relevant fields string for a highlight

        Returns:
            String: A string with the article and user highlight details
        """
        username = self.profile.user.username
        article_title = self.article.title
        hl_id = self.id
        return """
            Highlight - 
            id:{} username: {}, 
            title: {}, 
            start_index: {}, 
            end_index: {}
        """.format(
            hl_id,
            username,
            article_title,
            self.start_index,
            self.end_index,
        )
