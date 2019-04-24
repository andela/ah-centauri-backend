from rest_framework import status
from rest_framework.permissions import (IsAuthenticated, )
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from authors.apps.analytics.models import ReadsReport
from authors.apps.analytics.renderers import AnalyticsJSONRenderer
from authors.apps.analytics.response_messages import REPORT_MSG
from authors.apps.analytics.serializers import ReportAPISerializer
from authors.apps.articles.models import Articles
from authors.apps.articles.permissions import IsVerified


class AnalyticsReportAPIView(APIView):
    """
    Handles viewing of read article analytics
    Traffic and visitor statistics are available for stories if authenticated
    """
    permission_classes = (IsAuthenticated, IsVerified,)
    serializer_class = ReportAPISerializer
    renderer_classes = (AnalyticsJSONRenderer,)

    def get(self, request):
        """
        Handles listing all report on an article

        :param request:
        :return: [report]
        """
        self.check_permissions(request)

        report = ReadsReport.objects.filter(user=request.user)

        serializer = self.serializer_class(report, many=True)

        return Response(serializer.data,
                        status=status.HTTP_200_OK)


class AuthorsAnalyticsReportAPIView(APIView):
    """
    Handles viewing of read article analytics for my articles
    Traffic and visitor statistics are available for stories if authenticated
    """
    permission_classes = (IsAuthenticated, IsVerified,)
    serializer_class = ReportAPISerializer
    renderer_classes = (AnalyticsJSONRenderer,)

    def get(self, request):
        """
        Handles listing all report on an article

        :param request:
        :return: [report]
        """
        self.check_permissions(request)

        report = ReadsReport.objects.filter(article__author=request.user)
        serializer = self.serializer_class(report, many=True)

        return Response(serializer.data,
                        status=status.HTTP_200_OK)


class AnalyticsUpdateReportAPIView(APIView):
    """
    Handles updating viewing of read article analytics
    Traffic and visitor statistics are available for stories if authenticated
    """
    permission_classes = (IsAuthenticated, IsVerified,)
    serializer_class = ReportAPISerializer
    renderer_classes = (AnalyticsJSONRenderer,)

    @swagger_auto_schema(request_body=ReportAPISerializer,
                         responses={
                             201: ReportAPISerializer()})
    def patch(self, request, slug):
        """
        Handles updating report if author is same as the requester and article is similar
        :param request:
        :param slug:
        :return: [updated report]
        """

        self.check_permissions(request)

        try:
            article = Articles.objects.get(slug=slug)
            report = ReadsReport.objects.get(user=request.user, article=article)
            if report.full_read is True:
                return Response({
                                    "errors": REPORT_MSG['REPORT_UPTO_DATE']},
                                status=status.HTTP_400_BAD_REQUEST)
            if request.data['full_read'] != report.full_read:
                serializer = self.serializer_class(report, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()

                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({
                                "errors": REPORT_MSG['CAN_NOT_UNREAD']}, status=status.HTTP_400_BAD_REQUEST)
        except (Articles.DoesNotExist, ReadsReport.DoesNotExist,) as e:
            message = ""

            if isinstance(e, Articles.DoesNotExist):
                message = REPORT_MSG['ARTICLE_DOES_NOT_EXIST']

            elif isinstance(e, ReadsReport.DoesNotExist):
                message = REPORT_MSG['READS_REPORT_DOES_NOT_EXIST']

            return Response({
                                "errors": message}, status=status.HTTP_404_NOT_FOUND)
