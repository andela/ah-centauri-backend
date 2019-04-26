from rest_framework import serializers

from authors.apps.articles.models import Articles
from authors.apps.highlights.models import Highlights
from authors.apps.highlights.serializers import HighlightSerializer
from .models import Profile


class GetProfileSerializer(serializers.ModelSerializer):
    """
    serializers for user profile upon user registration.
    """

    username = serializers.ReadOnlyField(source='get_username')
    image_url = serializers.ReadOnlyField(source='get_cloudinary_url')

    class Meta:
        model = Profile

        fields = (
            'username', 'first_name', 'last_name', 'bio', 'image', 'image_url',
            'website', 'city', 'phone', 'country')

        read_only_fields = ("created_at", "updated_at")


class GetCurrentUserProfileSerializer(serializers.ModelSerializer):
    """
    serializers for current user profile.
    """

    highlights_on_my_articles = serializers.SerializerMethodField()
    highlights = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField(source='get_username')
    image_url = serializers.ReadOnlyField(source='get_cloudinary_url')

    class Meta:
        model = Profile

        fields = (
            'username', 'first_name', 'last_name', 'bio', 'image', 'image_url',
            'website', 'city', 'phone', 'country', 'highlights', 'highlights_on_my_articles')

        read_only_fields = ("created_at", "updated_at")

    def get_highlights_on_my_articles(self, obj):
        """
        Method to retrieve highlights made on my articles
        :return:
            List of highlights made on my articles
        """
        author_articles_ids = Articles.objects.filter(author=obj.user).values_list('id', flat=True)
        highlights = Highlights.objects.filter(article__in=author_articles_ids)
        return HighlightSerializer(highlights, many=True).data
