from rest_framework import serializers
from authors.apps.articles.models import Articles, Ratings


class ArticleSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=False, allow_blank=True, max_length=100)
    body = serializers.CharField()
    description = serializers.CharField(required=True, max_length=140)
    author = serializers.ReadOnlyField(source='get_author')
    average_rating = serializers.ReadOnlyField(source='get_average_rating')
    
    def create(self, validated_data):
        """
        Create and return a new `Article` instance, given the validated data.
        """
        return Articles.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Article` instance, given the validated data.
        """
        instance.title = validated_data.get('title', instance.title)
        instance.body = validated_data.get('body', instance.body)
        instance.description = validated_data.get('description', instance.description)
        if validated_data.get('title'):
            instance.slug = instance.get_unique_slug()
        instance.save()
        return instance

    
    class Meta:
        model = Articles
        fields = ('id', 'created_at', 'updated_at', 'title',
        'body', 'description', 'slug', 'average_rating', 'author')
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
            raise serializers.ValidationError('please keep range of rating from 1-5')
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