from rest_framework import status
from rest_framework.permissions import (
    IsAuthenticated)
from rest_framework.response import Response
from rest_framework.views import APIView

from authors.apps.articles.models import Articles
from authors.apps.authentication.permissions import IsVerifiedUser
from .models import Highlights
from .response_messages import HIGHLIGHT_MSGS
from .serializers import HighlightSerializer


class CreateGetDeleteMyHighlightsAPIView(APIView):
    """
    Provide methods for creating a highlight
    """

    permission_classes = (IsAuthenticated, IsVerifiedUser,)
    serializer_class = HighlightSerializer

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
        highlights = HighlightSerializer(highlights, many=True)
        return Response({
            'message': HIGHLIGHT_MSGS['HIGHLIGHTS_FOUND'],
            'highlights': highlights.data
        },
            status=status.HTTP_200_OK)

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
        # Check if the article exists
        try:
            article = Articles.objects.get(slug=slug)
            highlight_data['article'] = article
            highlight_data['profile'] = current_user.profile
            new_highlight = self.serializer_class(data=highlight_data)
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
