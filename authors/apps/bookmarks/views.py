from rest_framework import status
from rest_framework.permissions import (
    IsAuthenticated)
from rest_framework.response import Response
from rest_framework.views import APIView

from authors.apps.articles.models import Articles
from authors.apps.authentication.permissions import IsVerifiedUser
from .models import Bookmark
from .permissions import IsOwner
from .response_messages import BOOKMARK_MSGS
from .serializers import BookmarkSerializer


class GetBookmarkListAPIView(APIView):
    """
    Allows current user to get all their bookmarked articles
    """
    permission_classes = (IsAuthenticated, IsVerifiedUser,)
    serializer_class = BookmarkSerializer

    def get(self, request):
        """
        Return a current user's bookmarked articles.

        Params
        -------
        request: Object with request data and functions.

        Returns
        --------
        Response object:
        {
            "message": "message body",
            "bookmarks": List of all bookmarks by current user
        }
                OR
        {
            "errors": "error details body"
        }
        """
        # Retrieve the user from the request if they have been authenticated
        current_user = request.user
        bookmarks = Bookmark.objects.filter(profile=current_user.profile)
        if len(bookmarks) > 0:
            bookmarks = self.serializer_class(bookmarks, many=True)
            return Response(
                {
                    "message": BOOKMARK_MSGS['BOOKMARKS_FOUND'],
                    "bookmarks": bookmarks.data
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                "message": BOOKMARK_MSGS['NO_BOOKMARKS'],
                "bookmarks": []
            },
            status=status.HTTP_200_OK
        )


class DeleteBookmarkAPIView(APIView):
    """
    Provide methods for retrieving, updating and deleting bookmarks
    """

    permission_classes = (IsAuthenticated, IsVerifiedUser, IsOwner)
    serializer_class = BookmarkSerializer

    def get_object(self, pk):
        """
        Method to return a bookmark

        Params
        -------
        slug: refers to the slug of a bookmarked article

        Returns
        --------
        a bookmark object if found
        raises an exception if not found

        """
        try:
            return Bookmark.objects.get(id=pk)
        except Bookmark.DoesNotExist:
            return None

    def delete(self, request, pk, format=None):
        """
        Method to delete a specific booking

        Params
        -------
        request: Object with request data and functions.

        Returns
        --------
        Response object:
        {
            "message": "message body"
        }
                OR
        {
            "errors": "error details body"
        }

        """
        bookmark = self.get_object(pk)
        if bookmark is None:
            return Response(
                {
                    "errors": BOOKMARK_MSGS['BOOKMARK_NOT_FOUND']
                },
                status=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(request, bookmark)
        bookmark.delete()
        return Response(
            {
                "message": BOOKMARK_MSGS['BOOKMARK_REMOVED']
            },
            status=status.HTTP_200_OK)


class CreateBookmarkAPIView(APIView):
    """
    Provide methods for retrieving, updating and deleting bookmarks
    """

    permission_classes = (IsAuthenticated, IsVerifiedUser, IsOwner)
    serializer_class = BookmarkSerializer

    def post(self, request, slug):
        """
        Create a bookmark for an article

        Params
        -------
        request: Object with request data and functions.

        Returns
        --------
        Response object:
        {
            "message": "message body",
            "bookmark": dictionary of bookmark created by current user
        }
                OR
        {
            "errors": "error details body"
        }
        """
        # Retrieve the user from the request if they have been authenticated
        current_user = request.user
        try:
            article = Articles.objects.get(slug=slug)
        except Articles.DoesNotExist:
            return Response(
                {
                    "errors": BOOKMARK_MSGS['ARTICLE_NOT_FOUND']
                },
                status=status.HTTP_404_NOT_FOUND
            )
        try:
            Bookmark.objects.get(article=article, profile=current_user.profile)
            return Response({
                'errors': BOOKMARK_MSGS['ARTICLE_ALREADY_BOOKMARKED']},
                status=status.HTTP_400_BAD_REQUEST)
        except:
            pass
        bookmark_data = {
            "article": article,
            "profile": current_user.profile
        }
        bookmark = Bookmark.objects.create(**bookmark_data)
        serialized_bookmark = BookmarkSerializer(bookmark)
        return Response(
            {
                "message": BOOKMARK_MSGS['BOOKMARK_SUCCESSFUL'],
                "bookmark": serialized_bookmark.data
            },
            status=status.HTTP_201_CREATED
        )
