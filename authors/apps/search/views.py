from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny

from authors.apps.articles.models import (Articles,
                                          Favorite, )
from authors.apps.articles.serializers import ArticleSerializer
from authors.apps.search.renderer import SearchJSONRenderer


class ArticleFilter(filters.FilterSet):
    author = filters.CharFilter(field_name='author__username', lookup_expr='exact')
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')

    class Meta:
        model = Articles
        fields = ['author', 'title', 'created_at']


class SearchArticleListAPIView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ArticleSerializer
    queryset = Articles.objects.all()
    renderer_classes = (SearchJSONRenderer,)

    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = ArticleFilter
    search_fields = ('author__username', 'title', 'created_at',)

    # @swagger_auto_schema(query_serializer=ArticleSerializer,
    #                      responses={
    #                          200: ArticleSerializer()})
    def get_queryset(self):
        # Getting specific properties from the request body
        favorited = self.request.query_params.get('favorited', '')  # returns username
        tags = self.request.query_params.get('tags', '')  # returns tags

        if favorited:
            # Filtering through favourite model by username provided
            # returns a list of all article id's
            # The values_list method returns a ValuesListQuerySet.
            # This means it has the advantages of the queryset to return only article ids.
            article_ids = Favorite.objects.filter(user_id__username=favorited).values_list('article_id', flat=True)
            # Then Returns all articles that are linked to
            articles = Articles.objects.filter(id__in=article_ids)

            return articles

        if tags:
            # Create a list of unique tags by splitting the returned string from where comma appears.
            tag_list = tags.split(",")
            # To find all of a model with a specific tags you can filter
            article_by_tag = Articles.objects.filter(tags__name__in=tag_list)
            # If you’re filtering on multiple tags, it’s very common to get duplicate results,
            # because of the way relational databases work.
            # That's why i used `distinct` to prevent it.
            return article_by_tag.distinct()

        # This returns the current queryset
        return self.queryset
