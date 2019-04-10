from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from authors.apps.articles.models import Articles
from authors.apps.articles.permissions import IsOwnerOrReadOnly
from authors.apps.authentication.permissions import IsVerifiedUser
from authors.apps.comments.models import Comment
from authors.apps.comments.renderers import CommentJSONRenderer
from authors.apps.comments.serializers import CommentSerializer
from authors.apps.comments.response_messages import COMMENTS_MSG


class RetrieveCommentAPIView(APIView):
    """
    Handles viewing of comments if not authenticated and\
    Handles creating comments on an article if authenticated
    """
    permission_classes = (IsAuthenticatedOrReadOnly, IsVerifiedUser,)
    serializer_class = CommentSerializer
    renderer_classes = (CommentJSONRenderer,)

    def get(self, request, slug):
        """
        Handles listing all comments on an article

        :param slug:
        :return: [comments]
        """
        try:
            article = Articles.objects.get(slug=slug)
            comments = Comment.objects.all().filter(article_id=article.id, parent=request.query_params.get("parent",
                                                                                                           None))
            serializer = self.serializer_class(comments, many=True)

            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        except Articles.DoesNotExist:
            return Response({"errors": COMMENTS_MSG['ARTICLE_DOES_NOT_EXIST']}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, slug):
        """
        Handles creating a new comment on an article
        :param request:
        :param slug:
        :return: comment
        """
        try:
            article = Articles.objects.get(slug=slug)
            comment = request.data.get('comment', {})
            serializer = self.serializer_class(data=comment)
            serializer.is_valid(raise_exception=True)
            serializer.save(author=request.user, article=article)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Articles.DoesNotExist:
            return Response({"errors": COMMENTS_MSG['ARTICLE_DOES_NOT_EXIST']}, status=status.HTTP_404_NOT_FOUND)


class RetrieveUpdateDeleteCommentAPIView(APIView):
    """
    Handles viewing of a specific comment if not authenticated and\
    Handles replying to a comment on an article if authenticated
    Handles Deleting a comment from an article
    """
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, IsVerifiedUser,)
    serializer_class = CommentSerializer
    renderer_classes = (CommentJSONRenderer,)

    def get(self, request, *args, **kwargs):
        """
        Handles retrieving a specific comment and all their replies
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            article = Articles.objects.get(slug=self.kwargs['slug'])
        except Articles.DoesNotExist:
            return Response({"errors": COMMENTS_MSG['ARTICLE_DOES_NOT_EXIST']}, status=status.HTTP_404_NOT_FOUND)
        try:
            comment = Comment.objects.get(pk=self.kwargs['id'])
            serializer = self.serializer_class(comment)
            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response({"errors": COMMENTS_MSG['COMMENT_DOES_NOT_EXIST']}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, *args, **kwargs):
        """
        Handles updating a comment if author is same as the requester
        :param request:
        :param args:
        :param kwargs:
        :return: [updated comment]
        """
        try:
            article = Articles.objects.get(slug=self.kwargs['slug'])
        except Articles.DoesNotExist:
            return Response({"errors": COMMENTS_MSG['ARTICLE_DOES_NOT_EXIST']}, status=status.HTTP_404_NOT_FOUND)
        try:
            comment = Comment.objects.get(id=self.kwargs['id'])
            self.check_object_permissions(request, comment)
            serializer = self.serializer_class(comment, data=request.data.get('comment', {}), partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response({"errors": COMMENTS_MSG['COMMENT_DOES_NOT_EXIST']}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, **kwargs):
        """
        Handles method the user to delete his/her comment
        :param request:
        :param kwargs:
        :return: {success: message}
        """
        try:
            article = Articles.objects.get(slug=self.kwargs['slug'])
        except Articles.DoesNotExist:
            return Response({"errors": COMMENTS_MSG['ARTICLE_DOES_NOT_EXIST']}, status=status.HTTP_404_NOT_FOUND)
        try:
            comment = Comment.objects.get(pk=self.kwargs['id'])
            self.check_object_permissions(request, comment)
            comment.delete()
            return Response({"message": COMMENTS_MSG['DELETE_SUCCESS']}, status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response({"errors": COMMENTS_MSG['COMMENT_DOES_NOT_EXIST']}, status=status.HTTP_404_NOT_FOUND)
