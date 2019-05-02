from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    IsAuthenticated)
from rest_framework.response import Response
from rest_framework.views import APIView

from authors.apps.articles.models import Articles
from authors.apps.authentication.permissions import IsVerifiedUser
from .models import Highlights
from .permissions import IsOwner
from .response_messages import HIGHLIGHT_MSGS
from .serializers import HighlightSerializer


class CreateGetDeleteMyHighlightsAPIView(APIView):
    """
    Provide methods for creating a highlight
    """

    permission_classes = (IsAuthenticated, IsVerifiedUser,)
    serializer_class = HighlightSerializer
    pagination_class = LimitOffsetPagination

    def get(self, request, slug):
        """
        Get all my highlights for an article

        Params
        -------
        request: Object with request data and functions.

        Returns
        --------
        Response object:
        {
            "message": "message body",
            "highlights": list of highlights and their details
        }
                OR
        {
            "errors": "error details body"
        }
        """
        # Retrieve the user from the request if they have been authenticated
        current_user = request.user
        highlight_data = request.data.get("highlight_data", {})

        # Check if the article exists
        try:
            article = Articles.objects.get(slug=slug)
        except Articles.DoesNotExist:
            return Response(
                {
                    "errors": HIGHLIGHT_MSGS['ARTICLE_NOT_FOUND']
                },
                status=status.HTTP_404_NOT_FOUND
            )
        # Get all highlights for the article for the current user
        highlights = Highlights.objects.filter(article=article,
                                               profile=current_user.profile)
        if len(highlights) < 1:
            return Response({
                'errors': HIGHLIGHT_MSGS['NO_HIGHLIGHTS']},
                status=status.HTTP_404_NOT_FOUND)
        paginator = self.pagination_class()
        highlights_page = paginator.paginate_queryset(highlights, request)
        highlights = self.serializer_class(highlights_page, many=True, context={'request': request})
        paginated_highlights = paginator.get_paginated_response(highlights.data)
        return Response({
            'message': HIGHLIGHT_MSGS['HIGHLIGHTS_FOUND'],
            'highlights': paginated_highlights.data['results'],
            'count': paginated_highlights.data['count'],
            'next': paginated_highlights.data['next'],
            'previous': paginated_highlights.data['previous']
        },
            status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=HighlightSerializer,
                         responses={
                             201: HighlightSerializer()})
    def post(self, request, slug):
        """
        Create a highlight for an article

        Params
        -------
        request: Object with request data and functions.

        Returns
        --------
        Response object:
        {
            "message": "message body",
            "highlight": dictionary of highlight details created by current user
        }
                OR
        {
            "errors": "error details body"
        }
        """
        # Retrieve the user from the request if they have been authenticated
        current_user = request.user
        highlight_data = request.data.get("highlight_data", {})
        # Check if the article being highlighted exists
        try:
            article = Articles.objects.get(slug=slug)
            highlight_data['article'] = article
            highlight_data['profile'] = current_user.profile
            new_highlight = self.serializer_class(data=highlight_data,
                                                  context={'article': highlight_data['article'],
                                                           'profile': current_user.profile,
                                                           'request': request})
            new_highlight.is_valid(raise_exception=True)
        except Articles.DoesNotExist:
            return Response(
                {
                    "errors": HIGHLIGHT_MSGS['ARTICLE_NOT_FOUND']
                },
                status=status.HTTP_404_NOT_FOUND
            )
        # Delete the highlight if the start and end index are the same.
        try:
            highlight = Highlights.objects.get(article=article,
                                               profile=current_user.profile,
                                               start_index=highlight_data['start_index'],
                                               end_index=highlight_data['end_index'])
            highlight.delete()
            return Response({
                'message': HIGHLIGHT_MSGS['HIGHLIGHT_REMOVED']},
                status=status.HTTP_200_OK)
        except:
            pass
        new_highlight.save()
        return Response({
            'message': HIGHLIGHT_MSGS['HIGHLIGHTED_ADDED'],
            'highlight': new_highlight.data
        }, status=status.HTTP_201_CREATED)


class GetAllHighlightsForArticleAPIView(APIView):
    """
    Provide method to get all my highlights highlight
    """

    permission_classes = (IsAuthenticated, IsVerifiedUser,)
    serializer_class = HighlightSerializer
    pagination_class = LimitOffsetPagination

    def get(self, request, slug):
        """
        Get all public highlights for an article when the user want to see other peoples highlights

        Params
        -------
        request: Object with request data and functions.

        Returns
        --------
        Response object:
        {
            "message": "message body",
            "highlights": list of public highlights for the article and their details
        }
                OR
        {
            "errors": "error details body"
        }
        """
        # Check if the article exists
        try:
            article = Articles.objects.get(slug=slug)
        except Articles.DoesNotExist:
            return Response(
                {
                    "errors": HIGHLIGHT_MSGS['ARTICLE_NOT_FOUND']
                },
                status=status.HTTP_404_NOT_FOUND
            )
        # Get all public highlights for the current article
        highlights = Highlights.objects.filter(article=article, private=False)
        if len(highlights) < 1:
            return Response({
                'errors': HIGHLIGHT_MSGS['NO_PUBLIC_HIGHLIGHTS']},
                status=status.HTTP_404_NOT_FOUND)
        paginator = self.pagination_class()
        highlights_page = paginator.paginate_queryset(highlights, request)
        highlights = self.serializer_class(highlights_page, many=True, context={'request': request})
        paginated_highlights = paginator.get_paginated_response(highlights.data)
        return Response({
            'message': HIGHLIGHT_MSGS['PUBLIC_HIGHLIGHTS_FOUND'],
            'highlights': paginated_highlights.data['results'],
            'count': paginated_highlights.data['count'],
            'next': paginated_highlights.data['next'],
            'previous': paginated_highlights.data['previous']
        },
            status=status.HTTP_200_OK)


class GetAllMyHighlightsAPIView(APIView):
    """
    Provide method to get all my highlights highlight
    """

    permission_classes = (IsAuthenticated, IsVerifiedUser,)
    serializer_class = HighlightSerializer
    pagination_class = LimitOffsetPagination

    def get(self, request):
        """
        Get all my highlights for an article

        Params
        -------
        request: Object with request data and functions.

        Returns
        --------
        Response object:
        {
            "message": "message body",
            "highlights": list of highlights and their details
        }
                OR
        {
            "errors": "error details body"
        }
        """
        # Retrieve the user from the request if they have been authenticated
        current_user = request.user
        # Get all highlights for the current user
        highlights = Highlights.objects.filter(profile=current_user.profile)
        paginator = self.pagination_class()
        highlights_page = paginator.paginate_queryset(highlights, request)
        highlights = self.serializer_class(highlights_page, many=True, context={'request': request})
        paginated_highlights = paginator.get_paginated_response(highlights.data)
        return Response({
            'message': HIGHLIGHT_MSGS['HIGHLIGHTS_FOUND'],
            'highlights': paginated_highlights.data['results'],
            'count': paginated_highlights.data['count'],
            'next': paginated_highlights.data['next'],
            'previous': paginated_highlights.data['previous']
        },
            status=status.HTTP_200_OK)


class UpdateMyHighlightsAPIView(APIView):
    """
    Provide methods for creating a highlight
    """

    permission_classes = (IsAuthenticated, IsVerifiedUser, IsOwner)
    serializer_class = HighlightSerializer

    @swagger_auto_schema(request_body=HighlightSerializer,
                         responses={
                             201: HighlightSerializer()})
    def patch(self, request, pk):
        """
        Edits a highlight's comment for an article highlight

        Params
        -------
        request: Object with request data and functions.

        Returns
        --------
        Response object:
        {
            "message": "message body",
            "highlight": dictionary of edited highlight details created by current user
        }
                OR
        {
            "errors": "error details body"
        }
        """
        # Retrieve the user from the request if they have been authenticated
        current_user = request.user
        highlight_data = request.data.get("highlight_data", {})
        if "comment" not in highlight_data and "private" not in highlight_data:
            return Response(
                {
                    "errors": HIGHLIGHT_MSGS["HIGHLIGHTS_COMMENT_OR_PRIVATE_FIELD_REQUIRED"]
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            highlight = Highlights.objects.get(id=pk)
            self.check_object_permissions(request, obj=highlight)
            # Check if we are changing the privacy setting of the highlight
            if "private" in highlight_data and isinstance(highlight_data["private"], bool):
                highlight.private = highlight_data["private"]
            highlight.comment = highlight_data['comment']
            update_highlight = {
                "article": highlight.article,
                "profile": current_user.profile,
                "start_index": highlight.start_index,
                "end_index": highlight.end_index,
                "comment": highlight.comment,
                "private": highlight.private
            }
            update_highlight = self.serializer_class(highlight, data=update_highlight,
                                                     context={'article': update_highlight["article"],
                                                              'profile': current_user.profile,
                                                              'request': request},
                                                     partial=True)
            update_highlight.is_valid(raise_exception=True)
            update_highlight.save()
            return Response({
                'message': HIGHLIGHT_MSGS['HIGHLIGHT_UPDATED'],
                'highlight': update_highlight.data
            }, status=status.HTTP_200_OK)
        except Highlights.DoesNotExist:
            return Response(
                {
                    "errors": HIGHLIGHT_MSGS['HIGHLIGHTS_NOT_FOUND']
                },
                status=status.HTTP_404_NOT_FOUND
            )
