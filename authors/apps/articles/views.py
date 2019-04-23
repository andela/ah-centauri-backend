from django.contrib.contenttypes.models import ContentType
from rest_framework import (generics,
                            status,
                            )
from rest_framework.generics import (RetrieveUpdateAPIView,
                                     ListAPIView,
                                     )
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated,
                                        )
from rest_framework.response import Response
from rest_framework.views import APIView

from authors.apps.articles.exceptions import (ArticleNotFound,
                                              RatingNotFound,
                                              ReportNotFound,
                                              CommentNotFound,
                                              )
from authors.apps.articles.models import (Articles,
                                          Favorite,
                                          Ratings,
                                          ReportArticles,
                                          )
from authors.apps.articles.permissions import (IsOwnerOrReadOnly,
                                               IsVerified,
                                               )
from authors.apps.articles.renderers import (ArticleJSONRenderer,
                                             RatingJSONRenderer,
                                             ReportJSONRenderer,
                                             )
from authors.apps.articles.response_messages import ERROR_MESSAGES
from authors.apps.articles.serializers import (ArticleSerializer,
                                               RatingsSerializer,
                                               ReportsSerializer,
                                               )
from authors.apps.authentication.models import User
from authors.apps.authentication.permissions import IsVerifiedUser
from authors.apps.authentication.serializers import UserSerializer
from authors.apps.comments.models import Comment
from authors.apps.core.reports import reporting
from authors.apps.core.utils import send_notifications
from .models import LikeDislike
from .serializers import FavoriteSerializer


class CreateArticlesAPIView(APIView):
    """
    Allow any user (authenticated or not) to hit this endpoint.
    List all articles, or create a new article.
    """
    permission_classes = (IsAuthenticatedOrReadOnly, IsVerifiedUser,)
    serializer_class = ArticleSerializer
    renderer_classes = (ArticleJSONRenderer,)
    pagination_class = LimitOffsetPagination

    def get(self, request, format=None):
        articles = Articles.objects.all()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(articles, request)
        serializer = self.serializer_class(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        article = request.data.get('article', {})
        serializer = self.serializer_class(data=article)
        serializer.is_valid(raise_exception=True)
        article = serializer.save(author=request.user)

        # notify all followers of new content
        send_notifications(request,
                           notification_type="article_published",
                           instance=article,
                           recipients=article.author.profile.followers)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RetrieveUpdateDeleteArticleAPIView(RetrieveUpdateAPIView):
    """
    Allow only authenticated users to hit these endpoints.
    List edit or delete an article
    only an article owner can edit or delete his/her article
    """

    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, IsVerifiedUser,)
    serializer_class = ArticleSerializer
    renderer_classes = (ArticleJSONRenderer,)

    def get_object(self, slug):
        """
        Method to return an article 

        Params
        -------
        slug: reference to article to be returned

        Returns
        --------
        an article object if found
        raises an exception if not found

        """
        try:
            return Articles.objects.get(slug=slug)
        except Articles.DoesNotExist:
            raise ArticleNotFound

    def get(self, request, slug, format=None):
        article = self.get_object(slug)
        serializer = ArticleSerializer(article, context={'request': request})

        # Reporting the reading starts of an article
        if request.user.is_authenticated:
            reporting(user=request.user, article=article)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, slug, format=None):
        article = self.get_object(slug)
        self.check_object_permissions(request, article)
        serializer = ArticleSerializer(article, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, slug, format=None):
        article = self.get_object(slug)
        self.check_object_permissions(request, article)
        article.delete()
        return Response(status=status.HTTP_200_OK)


# add ratings views
class CreateListRatingsAPIView(APIView):
    """
    Allow any authenticated/verified users to hit this endpoint.
    List all ratings, or create a new rating.
    """
    permission_classes = (IsAuthenticatedOrReadOnly, IsVerifiedUser,)
    serializer_class = RatingsSerializer
    renderer_classes = (RatingJSONRenderer,)

    def get_object(self, slug):
        """
        Method to return an article 

        Params
        -------
        slug: reference to article to be returned

        Returns
        --------
        an article object if found
        raises an excepition if not found
        
        """
        try:
            return Articles.objects.get(slug=slug)
        except Articles.DoesNotExist:
            raise ArticleNotFound

    def get(self, request, slug):
        """
        Method to return ratings of a particular article

        Params
        -------
        request: Object with request data and functions.
        slug: reference to article to be returned

        Returns
        --------
        ratings
        error message if not found
        
        """
        ratings = Ratings.objects.all()
        serializer = RatingsSerializer(ratings, many=True)
        filtered_ratings = [x for x in serializer.data if x['slug'] == slug]
        if filtered_ratings:
            return Response({'data': filtered_ratings, 'RatingsCount': len(serializer.data)}, status=status.HTTP_200_OK)
        return Response({'errors': 'no ratings for this article present'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, slug):
        """
        Method to post a rating of a particular article

        Params
        -------
        request: Object with request data and functions.
        slug: reference to article to be returned

        Returns
        --------
        rating that has just been posted
        error message if:
                - you try to rate your own article
                - you try to rate an article twice
                - any other validation errors encountered
        
        """
        rating = request.data.get('rating', {})
        serializer = self.serializer_class(data=rating)
        serializer.is_valid(raise_exception=True)

        article = self.get_object(slug)

        article_id = article.id
        author = self.request.user

        if article.author == author:
            return Response({'errors': 'cannot rate own article'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            Ratings.objects.get(article_id=article_id, author=author)
            return Response({'errors': 'cannot rate an article twice'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            rating = serializer.save(author=request.user, article=article)

            return Response(serializer.data, status=status.HTTP_201_CREATED)


class RetrieveUpdateDeleteRatingAPIView(APIView):
    """
    Allow only authenticated users to hit these endpoints.
    List edit or delete a rating
    only a rating owner can edit or delete his/her article
    """
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, IsVerifiedUser)
    serializer_class = RatingsSerializer
    renderer_classes = (RatingJSONRenderer,)

    def get_object(self, pk):
        """
        Method to return a rating

        Params
        -------
        pk: reference to rating to be returned

        Returns
        --------
        a rating object if found
        raises an exception if not found
        
        """
        try:
            return Ratings.objects.get(pk=pk)
        except Ratings.DoesNotExist:
            raise RatingNotFound

    def get(self, request, pk, format=None):
        """
        Method to return a specific rating

        Params
        -------
        request: Object with request data and functions.
        pk: reference to rating to be returned

        Returns
        --------
        rating matching the pk
        error message if not found

        """
        rating = self.get_object(pk)
        serializer = RatingsSerializer(rating)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        """
        Method to edit a specific rating

        Params
        -------
        request: Object with request data and functions.
        pk: reference to rating to be edited

        Returns
        --------
        edited rating matching the pk
        error message if not found

        """
        rating = self.get_object(pk)
        self.check_object_permissions(request, rating)
        serializer = RatingsSerializer(rating, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk, format=None):
        """
        Method to delete a specific rating

        Params
        -------
        request: Object with request data and functions.
        pk: reference to rating to be deleted

        Returns
        --------
        success message upon deletion of said rating
        errors, if any

        """
        rating = self.get_object(pk)
        self.check_object_permissions(request, rating)
        rating.delete()
        return Response(status=status.HTTP_200_OK)


class LikesView(APIView):
    """
    View for liking and disliking Articles and Comments
    """
    model = None  # Data Model - Articles or Comments
    vote_type = None  # Vote type Like/Dislike
    permission_classes = (IsAuthenticatedOrReadOnly, IsVerifiedUser,)

    def post(self, request, *args, **kwargs):
        """
        Method to like or dislike an article or a comment

        Params
        -------
        request: Object with request data and functions.
        kwargs: reference to the article/comment to be liked/disliked

        Returns
        --------
        total number of likes and dislikes for that article/comment
        """

        model_mapper = {
            Comment: ({'id': self.kwargs.get('id', '')}, CommentNotFound),
            Articles: ({'slug': self.kwargs.get('slug', '')}, ArticleNotFound),
        }
        try:
            obj = self.model.objects.get(**model_mapper[self.model][0])
        except self.model.DoesNotExist:
            raise model_mapper[self.model][1]

        # GenericForeignKey does not support get_or_create
        content_type = ContentType.objects.get_for_model(obj)
        try:
            like_dislike = LikeDislike.objects.get(
                content_type=content_type, object_id=obj.id, user=request.user
            )
            # Checks if the object has not been liked or disliked before
            # then likes/dislikes if it hasn't if it has
            # then the like/dislike is deleted
            if like_dislike.vote is not self.vote_type:
                like_dislike.vote = self.vote_type
                like_dislike.save(update_fields=['vote'])
            else:
                like_dislike.delete()
        except LikeDislike.DoesNotExist:
            like_dislike = obj.likes.create(user=request.user, vote=self.vote_type)
            send_notifications(request,
                                notification_type="resource_liked",
                                instance=like_dislike,
                                recipients=[obj.author])

        return Response(
            {
                "like_count": obj.likes.likes(),
                "dislike_count": obj.likes.dislikes()
            },
            status=status.HTTP_200_OK
        )


class FavoriteView(generics.CreateAPIView):
    """This class creates a new favorite"""
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = FavoriteSerializer

    def post(self, request, slug):
        """Creates a favorite"""
        data = request.data
        article = Articles.objects.filter(
            # slug=slug, published=True, activated=True).first()
            slug=slug).first()

        if article is None:
            not_found = {
                "errors": "This article has not been found."
            }
            return Response(data=not_found, status=status.HTTP_404_NOT_FOUND)

        favorite = Favorite.objects.filter(
            user_id=request.user.pk, article_id=article.id).first()
        if favorite is not None:
            favorite_found = {
                "errors": "Article already in favorites."
            }
            return Response(data=favorite_found,
                            status=status.HTTP_400_BAD_REQUEST)

        data['article_id'] = article.id
        data['user_id'] = request.user.pk
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        data = serializer.data
        data['message'] = 'Article added to favorites.'
        return Response(data, status=status.HTTP_201_CREATED)

    def delete(self, request, slug):
        article = Articles.objects.filter(
            slug=slug).first()

        if article is None:
            not_found = {
                "errors": "This article has not been found."
            }
            return Response(data=not_found, status=status.HTTP_404_NOT_FOUND)
        favorite = Favorite.objects.filter(
            article_id=article.id, user_id=request.user.pk).first()
        if favorite:
            message = {"message": "Article removed from favorites"}
            favorite.delete()
            return Response(data=message, status=status.HTTP_204_NO_CONTENT)
        not_found = {"message": "Article not favorite"}
        return Response(not_found, status.HTTP_404_NOT_FOUND)

    def get(self, request, slug):
        article = Articles.objects.filter(
            slug=slug)
        if article:
            favorite = Favorite.objects.filter(
                article_id=article[0].id, user_id=request.user.pk).first()
            if favorite:
                serializer = self.serializer_class(favorite)
                return Response({'message': 'article favorited', 'article': serializer.data}, status=status.HTTP_200_OK)
            not_found = {"message": "Article not favorited"}
            return Response(not_found, status.HTTP_404_NOT_FOUND)
        not_found = {
            "errors": "This article has not been found."
        }
        return Response(data=not_found, status=status.HTTP_404_NOT_FOUND)


class GetUserFavoritesView(APIView):
    """Gets one user's favorite articles"""
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        favorites_queryset = Favorite.objects.filter(
            user_id=request.user.id)

        favorite_articles = []
        for favorite in favorites_queryset:
            article = ArticleSerializer(favorite.article_id).data
            favorite_articles.append(article)
        favorites = {
            "favorites": favorite_articles
        }
        return Response(data=favorites, status=status.HTTP_200_OK)


class ListReportsAPIView(APIView):
    """
    View to handle fetching of reports for particular articles.
    Allow any users to fetch reports.
    """
    serializer_class = ReportsSerializer
    renderer_classes = (ReportJSONRenderer,)
    permission_classes = (IsAuthenticated, IsVerifiedUser)

    def get(self, request):
        """
        Method to get reports made by current user

        Params
        -------
        request: Object with request data and functions.

        Returns
        --------
        reports made by current user
        error message if:
             - any validation errors encountered
        """
        reports = ReportArticles.objects.filter(author=request.user)
        if reports:
            serializer = ReportsSerializer(reports, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"errors": ERROR_MESSAGES['not found']}, status=status.HTTP_404_NOT_FOUND)


class CreateListReportsAPIView(APIView):
    """
    View to handle posting and fetching of reports by users.
    Allow only both authenticated and verified users to post reports.
    """
    serializer_class = ReportsSerializer
    renderer_classes = (ReportJSONRenderer,)
    permission_classes = (IsAuthenticatedOrReadOnly, IsVerifiedUser,)

    def get_object(self, slug):
        """
        Method to get an article

        Params
        -------
        slug: reference to article to be fetched

        Returns
        --------
        article corresponding to given slug
        raises an exception if not found
        """
        try:
            return Articles.objects.get(slug=slug)
        except Articles.DoesNotExist:
            raise ArticleNotFound

    def post(self, request, slug):
        """
        Method to post a report of a particular article

        Params
        -------
        request: Object with request data and functions.
        slug: reference to article to be reported

        Returns
        --------
        report that has just been posted
        error message if:
            - you try to report your own article
            - you are either not authenticated or not verified
            - any other validation errors encountered
        
        """
        report = request.data.get('report', {})
        serializer = self.serializer_class(data=report)
        serializer.is_valid(raise_exception=True)

        article = self.get_object(slug)
        author = request.user

        if article.author == author:
            return Response({'errors': ERROR_MESSAGES['forbidden']}, status=status.HTTP_400_BAD_REQUEST)

        rating = serializer.save(author=request.user, article=article)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, slug):
        """
        Method to get reports related to current article

        Params
        -------
        request: Object with request data and functions.
        slug: reference to current article

        Returns
        --------
        reports of current article
        error message if:
             - any validation errors encountered
        """
        article = self.get_object(slug)
        reports = ReportArticles.objects.filter(article=article)
        serializer = ReportsSerializer(reports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RetrieveUpdateDeleteReportAPIView(APIView):
    """
    Allow only authenticated users to hit these endpoints(save for the get endpoint).
    List edit or delete a report
    only a report owner can edit or delete his/her article
    """
    serializer_class = ReportsSerializer
    renderer_classes = (ReportJSONRenderer,)
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, IsVerifiedUser)

    def get_object(self, pk):
        """
        Method to return a report

        Params
        -------
        pk: reference to report to be returned

        Returns
        --------
        a report object if found
        raises an exception if not found
        
        """
        try:
            return ReportArticles.objects.get(pk=pk)
        except ReportArticles.DoesNotExist:
            raise ReportNotFound

    def get(self, request, pk, format=None):
        """
        Method to return a specific report

        Params
        -------
        request: Object with request data and functions.
        pk: reference to report to be returned

        Returns
        --------
        report matching the pk
        error message if not found

        """
        report = self.get_object(pk)
        serializer = ReportsSerializer(report)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        """
        Method to edit a specific report

        Params
        -------
        request: Object with request data and functions.
        pk: reference to report to be edited

        Returns
        --------
        edited report matching the pk
        error message if not found

        """
        report = self.get_object(pk)
        self.check_object_permissions(request, report)
        serializer = ReportsSerializer(report, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk, format=None):
        """
        Method to delete a specific report

        Params
        -------
        request: Object with request data and functions.
        pk: reference to report to be deleted

        Returns
        --------
        success message upon deletion of said report
        errors, if any

        """
        report = self.get_object(pk)
        self.check_object_permissions(request, report)
        report.delete()
        return Response(status=status.HTTP_200_OK)


class CreateListAuthorsAPIView(ListAPIView):
    """
    Allow any authenticated/verified users to hit this endpoint.
    List all authors plus their profiles.
    """
    permission_classes = (IsAuthenticated, IsVerified,)
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        articles = Articles.objects.values_list('author_id', flat=True).distinct()
        users = User.objects.filter(id__in=articles)
        return users
