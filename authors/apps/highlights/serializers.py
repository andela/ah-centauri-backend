from rest_framework import serializers

from .models import Highlights
from .response_messages import HL_VALIDATION_MSGS


class HighlightSerializer(serializers.ModelSerializer):
    """
    Serializer to validate and transform data related
    to a users highlights for an article.
    """

    text = serializers.SerializerMethodField()
    start_index = serializers.IntegerField(required=True, min_value=0)
    end_index = serializers.IntegerField(required=True, min_value=1)
    comment = serializers.CharField(required=False)
    article = serializers.SerializerMethodField()
    highlighted_by = serializers.SerializerMethodField()

    class Meta:
        model = Highlights
        fields = ('id', 'start_index', 'article', 'end_index', 'comment', 'text', 'highlighted_by')
        read_only_fields = ('created_at',)

    def validate(self, data):
        """
        Check that start is less than finishing index and length
        of article is within index range.
        """
        article = self.initial_data['article']
        if data['start_index'] > data['end_index']:
            raise serializers.ValidationError(HL_VALIDATION_MSGS["END_LESS_THAN_START"])
        article_length = len(self.initial_data['article'].body) - 1
        if article_length < data['start_index'] or article_length < data['end_index']:
            raise serializers.ValidationError(HL_VALIDATION_MSGS["OUT_OF_RANGE"])
        data.update({'article': self.initial_data['article']})
        data.update({'profile': self.initial_data['profile']})
        return data

    def get_text(self, obj):
        """
        Return the highlighted text of an article using the indexes

        Params
        -------
        request: Object with request data and functions.

        Returns
        --------
        String object with the highlighted text
        """
        highlight_text = obj.article.body[obj.start_index:obj.end_index]
        return highlight_text

    def get_article(self, obj):
        """
        Return a current user's bookmarked articles.

        Params
        -------
        obj: Object with highlight data and functions.

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
            "slug": obj.article.slug,
            "author": obj.article.author.username
        }
        return article

    def get_highlighted_by(self, obj):
        """
        Return username for user who highlighted.

        Params
        -------
        obj: Object with highlight data and functions.

        Returns
        --------
        String for the user who highlighted the article
        """
        return obj.profile.get_username
