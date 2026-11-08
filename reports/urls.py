from django.urls import path

from .views import (
    AdminAnalyticsView,
    AdminCategoryDetailView,
    AdminCategoryListCreateView,
    CategoryBreakdownView,
    ExportCsvView,
    SpendTrendView,
)

urlpatterns = [
    path("analytics/", CategoryBreakdownView.as_view(), name="analytics-breakdown"),
    path("analytics/trend/", SpendTrendView.as_view(), name="analytics-trend"),
    path("reports/export/", ExportCsvView.as_view(), name="reports-export"),
    path("admin/categories/", AdminCategoryListCreateView.as_view(), name="admin-category-list"),
    path("admin/categories/<uuid:pk>/", AdminCategoryDetailView.as_view(), name="admin-category-detail"),
    path("admin/analytics/", AdminAnalyticsView.as_view(), name="admin-analytics"),
]
