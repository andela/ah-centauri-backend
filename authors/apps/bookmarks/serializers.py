from rest_framework import serializers

from .models import Bookmark


class BookmarkSerializer(serializers.ModelSerializer):
    """
    BookmarkSerializer class to validate, transform bookmark datatypes
    """
    article = serializers.SerializerMethodField()

    class Meta:
        model = Bookmark
        fields = ('id', 'article', 'created_at')

    def get_article(self, obj):
        """
        Return a current user's bookmarked articles.

        Params
        -------
        request: Object with request data and functions.

        Returns
        --------
        Dictionary object:
        {
            "title": bookmarked article title
            "description": bookmarked article description
            "slug": bookmarked article slug
            "author": bookmarked article author username
            "created_at": bookmarked article date of creation
        }
        """
        article = {
            "title": obj.article.title,
            "description": obj.article.description,
            "slug": obj.article.slug,
            "author": obj.article.author.username,
            "created_at": obj.article.created_at
        }
        return article
