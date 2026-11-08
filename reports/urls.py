from django.urls import path

from .views import AdminCategoryDetailView, AdminCategoryListCreateView, CategoryBreakdownView, SpendTrendView

urlpatterns = [
    path("analytics/", CategoryBreakdownView.as_view(), name="analytics-breakdown"),
    path("analytics/trend/", SpendTrendView.as_view(), name="analytics-trend"),
    path("admin/categories/", AdminCategoryListCreateView.as_view(), name="admin-category-list"),
    path("admin/categories/<uuid:pk>/", AdminCategoryDetailView.as_view(), name="admin-category-detail"),
]
