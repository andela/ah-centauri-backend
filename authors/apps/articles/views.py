from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import Http404

from authors.apps.articles.serializers import ArticleSerializer
from authors.apps.articles.permissions import IsOwnerOrReadOnly
from authors.apps.articles.renderers import ArticleJSONRenderer
from authors.apps.articles.models import Articles


class CreateArticlesAPIView(APIView):
    """
    Allow any user (authenticated or not) to hit this endpoint.
    List all articles, or create a new article.
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)
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
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, )
    serializer_class = ArticleSerializer
    renderer_classes = (ArticleJSONRenderer,)

    def get_object(self, slug):
        try:
            return Articles.objects.get(slug=slug)
        except Articles.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        article = self.get_object(slug)
        serializer = ArticleSerializer(article)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def put(self, request, slug, format=None):
        article = self.get_object(slug)
        self.check_object_permissions(request, article)
        serializer = ArticleSerializer(article, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug, format=None):
        article = self.get_object(slug)
        self.check_object_permissions(request, article)
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
