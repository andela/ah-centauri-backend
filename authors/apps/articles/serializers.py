from rest_framework import serializers
import readtime
from authors.apps.articles.models import Articles, Ratings
from authors.apps.authentication.serializers import UserSerializer
from authors.apps.articles.models import Articles, Ratings, Favorite, ReportArticles
from authors.apps.articles.utils import ChoicesField
from authors.apps.authentication.serializers import UserSerializer


class ArticleSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(
        required=True,
        max_length=100)
    body = serializers.CharField()
    description = serializers.CharField(required=True, max_length=140)
    author = serializers.ReadOnlyField(source='get_author')
    average_rating = serializers.ReadOnlyField(source='get_average_rating')
    likes = serializers.ReadOnlyField(source='likes.likes')
    dislikes = serializers.ReadOnlyField(source='likes.dislikes')
    # string describe the read time of an article e.g '1 min read'
    read_time = serializers.ReadOnlyField()

    def to_representation(self, instance):
        """ Add the read time of the article."""
        article_rep = super().to_representation(instance)
        # Get read time for an article instance,
        #  given it has HTML elements e.g images
        # read time (seconds) = num_words / 265 * 60 + img_weight * num_images
        article_rep['read_time'] = str(readtime.of_html(article_rep['body']))
        # return the article's details along with it's read time
        return article_rep

    def create(self, validated_data):
        """
        Create and return a new `Article` instance, given the validated data.
        """
        return Articles.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Article`, given the validated data.
        """
        instance.title = validated_data.get('title', instance.title)
        instance.body = validated_data.get('body', instance.body)
        instance.description = validated_data.get(
            'description',
            instance.description)
        if validated_data.get('title'):
            instance.slug = instance.get_unique_slug()
        instance.save()
        return instance

    class Meta:
        model = Articles
        fields = ('id', 'likes', 'dislikes', 'created_at', 'updated_at',
                  'author', 'title', 'body', 'description',
                  'average_rating', 'slug', 'read_time')
        extra_kwargs = {
            'url': {
                'view_name': 'articles:article-detail'
            }
        }


# add ratings serializer
class RatingsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    author = serializers.ReadOnlyField(source='rater.username')
    value = serializers.IntegerField()
    review = serializers.CharField()
    article = serializers.ReadOnlyField(source='article.title')
    slug = serializers.ReadOnlyField(source='article.slug')

    def validate_value(self, data):
        """
        Method to validate value given during rating 

        Params
        -------
        data: attributes to be validated

        Returns
        --------
        data after successful validation
        errors if validation fails

        """
        if not (0 < data < 6):
            raise serializers.ValidationError(
                'please keep range of rating from 1-5')
        return data

    class Meta:
        model = Ratings
        fields = ('id', 'created_at', 'updated_at', 'author', 'article', 'slug',
                  'value', 'review')
        extra_kwargs = {
            'url': {
                'view_name': 'ratings:rating-detail'
            }
        }


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Serializers for favorites
    """
    class Meta():
        model = Favorite
        fields = ('id', 'user_id', 'article_id')
        read_only_fields = ['id']




# add reports serializer
class ReportsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    author = serializers.ReadOnlyField(source='reporter.username')
    article = serializers.ReadOnlyField(source='article.title')
    slug = serializers.ReadOnlyField(source='article.slug')
    report = serializers.CharField(max_length=140)
    type_of_report = ChoicesField(choices=["spam", "harassment", "rules violation", "plagiarism"])

    class Meta:
        model = ReportArticles
        fields = ('id', 'created_at', 'updated_at', 'author', 'article', 'type_of_report', 'slug',
                'report')
        extra_kwargs = {
            'url': {
                'view_name': 'reports:report-detail'
            }
        }

