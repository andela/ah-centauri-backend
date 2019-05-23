from rest_framework import serializers
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType

from authors.apps.articles.models import LikeDislike
from authors.apps.comments.models import Comment



class CommentSerializer(serializers.ModelSerializer):
    """
    Handles serialization and deserialization of Comment objects.
    """
    replies = serializers.SerializerMethodField(label='replyCount')
    article = serializers.ReadOnlyField(source='article.slug')
    author = serializers.ReadOnlyField(source='author.username')
    body = serializers.CharField(max_length=250, required=True)
    likes = serializers.ReadOnlyField(source='likes.likes')
    dislikes = serializers.ReadOnlyField(source='likes.dislikes')
    has_liked = serializers.SerializerMethodField()
    has_disliked = serializers.SerializerMethodField()
    has_edits = serializers.SerializerMethodField()

    def get_has_liked(self, instance):
        """
        Handle checking if a user has liked an article before
        :param instance:
        :return:
        """

        request = self.context.get('request')

        ld = []

        if request and not isinstance(request.user, AnonymousUser):
            ct = ContentType.objects.get_for_model(Comment)
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
            ct = ContentType.objects.get_for_model(Comment)
            ld = LikeDislike.objects.filter(content_type=ct,
                                        user=request.user,
                                        object_id=instance.id,
                                        vote=-1)

        return bool(len(list(ld)))


    class Meta:
        model = Comment
        fields = ('id', 'article', 'author',
                  'body', 'has_liked', 'has_disliked', 'created_at', 'updated_at',
                  'replies', 'parent', 'likes', 'dislikes', 'has_edits')
        read_only_fields = ('id',)

    
    @staticmethod
    def get_replies(obj):
        """
        Handle retrieving reply count linked to the current comment
        :param obj:
        :return: [comment:replies]
        """
        return len(CommentSerializer(obj.children(), many=True).data)

    def get_has_edits(self, instance):
        """
        Handle checking if comment has been edited.
        :param instance:
        :return:
        """
        edit_count = instance.history.count()

        return True if edit_count > 1 else False


class EditHistorySerializer(serializers.ModelSerializer):
    body = serializers.CharField(max_length=250, required=True)

    class Meta:
        model = Comment
        fields = ('id', 'body', 'created_at', 'updated_at')
        read_only_fields = ('id',)
