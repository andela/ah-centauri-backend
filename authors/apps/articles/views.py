from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import Http404

from authors.apps.authentication.permissions import IsVerifiedUser
from authors.apps.articles.serializers import ArticleSerializer, RatingsSerializer
from authors.apps.articles.permissions import IsOwnerOrReadOnly
from authors.apps.articles.renderers import ArticleJSONRenderer, RatingJSONRenderer
from authors.apps.articles.models import Articles, Ratings
from django.contrib.contenttypes.models import ContentType
from .models import LikeDislike


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
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly, IsVerifiedUser, )
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
    model = None    # Data Model - Articles or Comments
    vote_type = None  # Vote type Like/Dislike
    permission_classes = (IsAuthenticatedOrReadOnly, IsVerifiedUser, )

    def post(self, request, slug):
        obj = self.model.objects.get(slug=slug)
        # GenericForeignKey does not support get_or_create
        ct = ContentType.objects.get_for_model(obj)
        try:
            likedislike = LikeDislike.objects.get(
                content_type=ct, object_id=obj.id, user=request.user
            )
            if likedislike.vote is not self.vote_type:
                likedislike.vote = self.vote_type
                likedislike.save(update_fields=['vote'])
            else:
                likedislike.delete()
        except LikeDislike.DoesNotExist:
            obj.likes.create(user=request.user, vote=self.vote_type)

        return Response(
            {
                "like_count": obj.likes.likes(),
                "dislike_count": obj.likes.dislikes()
            },
            status=status.HTTP_200_OK
        )
