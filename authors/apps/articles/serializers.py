from rest_framework import serializers
from authors.apps.articles.models import Articles
from authors.apps.authentication.serializers import UserSerializer

class ArticleSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=False, allow_blank=True, max_length=100)
    body = serializers.CharField()
    description = serializers.CharField(required=True, max_length=140)
    author = UserSerializer(required=False)
    
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
        instance.save()
        return instance

    class Meta:
        model = Articles
        fields = ('id', 'created_at', 'updated_at', 'author',
                    'title', 'body', 'description', 'slug')
        extra_kwargs = {
            'url': {
                'view_name': 'articles:article-detail'
            }
        }