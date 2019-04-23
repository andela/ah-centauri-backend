from django.urls import path

from authors.apps.analytics.views import (AnalyticsReportAPIView,
                                          AnalyticsUpdateReportAPIView,
                                          AuthorsAnalyticsReportAPIView,
                                          )

app_name = 'analytics'

urlpatterns = [
    path('analytics/', AnalyticsReportAPIView.as_view(), name='my_views'),
    path('analytics/me/', AuthorsAnalyticsReportAPIView.as_view(), name='total_reads'),
    path('analytics/<slug:slug>/', AnalyticsUpdateReportAPIView.as_view(), name='update'),
]
