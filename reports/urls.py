from django.urls import path

from .views import CategoryBreakdownView, SpendTrendView

urlpatterns = [
    path("analytics/", CategoryBreakdownView.as_view(), name="analytics-breakdown"),
    path("analytics/trend/", SpendTrendView.as_view(), name="analytics-trend"),
]
