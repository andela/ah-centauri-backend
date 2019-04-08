from django.contrib.contenttypes.models import ContentType
from rest_framework import generics
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from authors.apps.articles.models import Articles, Favorite
from authors.apps.articles.models import Ratings
from authors.apps.articles.permissions import IsOwnerOrReadOnly
from authors.apps.articles.renderers import ArticleJSONRenderer
from authors.apps.articles.renderers import RatingJSONRenderer
from authors.apps.articles.serializers import ArticleSerializer, RatingsSerializer
from authors.apps.authentication.permissions import IsVerifiedUser
from .models import LikeDislike
from .serializers import FavoriteSerializer


class ArticleNotFound(Exception):
    pass

class RatingNotFound(Exception):
    pass

class CreateArticlesAPIView(APIView):
    """
    Allow any user (authenticated or not) to hit this endpoint.
    List all articles, or create a new article.
    """
    permission_classes = (IsAuthenticatedOrReadOnly, IsVerifiedUser,)
    serializer_class = ArticleSerializer
    renderer_classes = (ArticleJSONRenderer,)

    def get(self, request, format=None):
        articles = Articles.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response({'data': serializer.data, 'articlesCount': len(serializer.data)}, status=status.HTTP_200_OK)

    def post(self, request):
        article = request.data.get('article', {})
        serializer = self.serializer_class(data=article)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RetrieveUpdateDeleteArticleAPIView(RetrieveUpdateAPIView):
    """
    Allow only authenticated users to hit these endpoints.
    List edit or delete an article
    only an article owner can edit or delete his/her article
    """
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, IsVerifiedUser, )
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
        raises an excepition if not found

        """
        try:
            return Articles.objects.get(slug=slug)
        except Articles.DoesNotExist:
            raise ArticleNotFound

    def get(self, request, slug, format=None):
        article = self.get_object(slug)
        serializer = ArticleSerializer(article)
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
        return Response(status=status.HTTP_204_NO_CONTENT)
    

# add ratings views
class CreateListRatingsAPIView(APIView):
    """
    Allow any authenticated/verified users to hit this endpoint.
    List all ratings, or create a new rating.
    """
    permission_classes = (IsAuthenticatedOrReadOnly, IsVerifiedUser, )
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
        filtered_ratings = [x for x in serializer.data if x['slug']==slug]
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
            serializer.save(author=request.user, article=article)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        
        
class RetrieveUpdateDeleteRatingAPIView(APIView):
    """
    Allow only authenticated users to hit these endpoints.
    List edit or delete a rating
    only a rating owner can edit or delete his/her article
    """
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, IsVerifiedUser )
    serializer_class = RatingsSerializer
    renderer_classes = (RatingJSONRenderer,)

    def get_object(self, pk):
        """
        Method to return an article 

        Params
        -------
        slug: referende to article to be returned

        Returns
        --------
        an article object if found
        raises an excepition if not found
        
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
        return Response(status=status.HTTP_204_NO_CONTENT)


class LikesView(APIView):
    """
    View for liking and disliking Articles and later on Comments
    """
    model = None  # Data Model - Articles or Comments
    vote_type = None  # Vote type Like/Dislike
    permission_classes = (IsAuthenticatedOrReadOnly, IsVerifiedUser,)

    def post(self, request, *args, **kwargs):
        """
        Method to like or dislike an article

        Params
        -------
        request: Object with request data and functions.
        kwargs: reference to the article to liked/disliked

        Returns
        --------
        total number of likes and dislikes for that article
        """
        obj = self.model.objects.get(slug=self.kwargs['slug'])
        # GenericForeignKey does not support get_or_create
        content_type = ContentType.objects.get_for_model(obj)
        try:
            like_dislike = LikeDislike.objects.get(
                content_type=content_type, object_id=obj.id, user=request.user
            )
            # Checks if the object has not been liked or disliked before
            # then likes/dislikes if it hasn't if it has
            # then it the like/dislike is deleted
            if like_dislike.vote is not self.vote_type:
                like_dislike.vote = self.vote_type
                like_dislike.save(update_fields=['vote'])
            else:
                like_dislike.delete()
        except LikeDislike.DoesNotExist:
            obj.likes.create(user=request.user, vote=self.vote_type)

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
    permission_classes = (IsAuthenticatedOrReadOnly, )

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
