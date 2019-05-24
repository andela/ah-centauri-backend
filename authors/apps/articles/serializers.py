import os
from urllib import parse

import readtime
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer, )

from authors.apps.articles.models import (Articles,
                                          Ratings,
                                          Favorite,
                                          ReportArticles, LikeDislike)
from authors.apps.articles.utils import ChoicesField


class TagSerializer(TagListSerializerField):
    default_error_messages = {
        'not_a_list':
            'Expected a list of items but got type "{input_type}".',
        'invalid_json': 'tags provided must be in a list',
        'not_a_str': 'All list items must be of string type.'
    }


class ArticleSerializer(TaggitSerializer, serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(
        required=True,
        max_length=100)
    body = serializers.CharField()
    description = serializers.CharField(required=True, max_length=250)
    author = serializers.ReadOnlyField(source='get_author')
    average_rating = serializers.ReadOnlyField(source='get_average_rating')
    likes = serializers.ReadOnlyField(source='likes.likes')
    dislikes = serializers.ReadOnlyField(source='likes.dislikes')
    has_liked = serializers.SerializerMethodField()
    has_disliked = serializers.SerializerMethodField()
    tags = TagSerializer()
    share_links = serializers.SerializerMethodField()
    # string describe the read time of an article e.g '1 min read'
    read_time = serializers.ReadOnlyField()
    favorited = serializers.ReadOnlyField(source="favoriters")
    has_rating = serializers.SerializerMethodField()
    auth_user_rating = serializers.SerializerMethodField()

    def get_has_liked(self, instance):
        """
        Handle checking if a user has liked an article before
        :param instance:
        :return:
        """

        request = self.context.get('request')

        ld = []

        if request and not isinstance(request.user, AnonymousUser):
            ct = ContentType.objects.get_for_model(Articles)
            ld = LikeDislike.objects.filter(content_type=ct,
                                            user=request.user,
                                            object_id=instance.id,
                                            vote=1)

        return bool(len(list(ld)))

    def get_has_disliked(self, instance):
        """
        Handle checking if a user has disliked an article before
        :param instance:
        :return:
        """

        request = self.context.get('request')

        ld = []

        if request and not isinstance(request.user, AnonymousUser):
            ct = ContentType.objects.get_for_model(Articles)
            ld = LikeDislike.objects.filter(content_type=ct,
                                            user=request.user,
                                            object_id=instance.id,
                                            vote=-1)

        return bool(len(list(ld)))

    def to_representation(self, instance):
        """ Add the read time of the article."""
        article_rep = super().to_representation(instance)
        # Get read time for an article instance,
        #  given it has HTML elements e.g images
        # read time (seconds) = num_words / 265 * 60 + img_weight * num_images
        article_rep['read_time'] = str(readtime.of_html(article_rep['body']))
        # return the article's details along with it's read time
        return article_rep

    def get_auth_user_rating(self, instance):
        rating = {}

        if isinstance(instance, Articles):
            request = self.context.get('request')

            if request and not isinstance(request.user, AnonymousUser):
                rating = Ratings.objects.filter(
                    author=request.user, article=instance).first()

            if rating:
                rating = {
                    'id': rating.id,
                    'created_at': rating.created_at.strftime('%c'),
                    'updated_at': rating.updated_at.strftime('%c'),
                    'value': rating.value,
                    'review': rating.review,
                }

        return rating

    def get_has_rating(self, instance):

        has_rating = False

        if isinstance(instance, Articles):
            request = self.context.get('request')

            if request and not isinstance(request.user, AnonymousUser):
                has_rating = Ratings.objects.filter(
                    author=request.user, article=instance).exists()

        return has_rating

    def get_share_links(self, obj):
        links = {}

        if isinstance(obj, Articles):
            title = obj.title
            description = obj.description

            react_url = os.environ.get('REACT_CLIENT_URL')  # Get the react client URL
            article_link = react_url + 'article/' + obj.slug
            request = self.context.get('request')

            if request:
                article_link = parse.quote(article_link)
                title = parse.quote(title)
                description = parse.quote(description)

                links['facebook'] = "https://www.facebook.com/sharer/sharer.php?u={}".format(article_link)
                links['twitter'] = "https://twitter.com/intent/tweet?url={}&text={}".format(article_link, title)
                links['email'] = "mailto:?&subject={}&body={}".format(title, description, article_link)

        # return whatever we now have in the :links dictionary
        return links

    def create(self, validated_data):
        """
        Create and return a new `Article` instance, given the validated data.
        """
        tags = [tag.lower() for tag in validated_data.pop('tags')]
        instance = super().create(validated_data)
        instance.tags.set(*tags)
        return instance

    def update(self, instance, validated_data):
        """
        Update and return an existing `Article`, given the validated data.
        """
        old_tags = [tag for tag in instance.tags.all()]
        tags = validated_data.pop('tags', old_tags)
        instance.title = validated_data.get('title', instance.title)
        instance.body = validated_data.get('body', instance.body)
        instance.description = validated_data.get(
            'description', instance.description)
        unique_tags = list(set(old_tags + tags))
        instance.tags.set(*unique_tags)

        if validated_data.get('title'):
            instance.slug = instance.get_unique_slug()

        instance.save()
        return instance

    class Meta:
        model = Articles

        fields = ('id', 'likes', 'dislikes', 'has_liked', 'has_disliked', 'created_at', 'updated_at',
                  'author', 'title', 'tags', 'body', 'description',
                  'average_rating', 'slug', 'read_time', 'share_links', 'has_rating', 'auth_user_rating', 'favorited')

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

    class Meta:
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
    type_of_report = ChoicesField(
        choices=["spam", "harassment", "rules violation", "plagiarism"])

    class Meta:
        model = ReportArticles
        fields = ('id', 'created_at', 'updated_at', 'author', 'article', 'type_of_report', 'slug',
                  'report')
        extra_kwargs = {
            'url': {
                'view_name': 'reports:report-detail'
            }
        }
