from rest_framework import serializers

from authors.apps.analytics.models import ReadsReport


class ReportAPISerializer(serializers.ModelSerializer):
    article = serializers.SerializerMethodField()
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = ReadsReport
        fields = ('id', 'user', 'article',
                  'full_read',)
        read_only_fields = ('id',)

    def get_article(self, obj):
        """
        Return a current user's Viewed articles.

        Params
        -------
        request: Object with request data and functions.

        Returns
        --------
        Dictionary object:
        {
            "title": Viewed article title
            "description": Viewed article description
            "slug": Viewed article slug
            "author": Viewed article author username
            "created_at": Viewed article date of creation
        }
        """
        all_views = ReadsReport.objects.filter(article=obj.article).count()
        article = {
            "title": obj.article.title,
            "description": obj.article.description,
            "slug": obj.article.slug,
            "author": obj.article.author.username,
            "created_at": str(obj.article.created_at),
            "totalViews": all_views,
        }
        return article
