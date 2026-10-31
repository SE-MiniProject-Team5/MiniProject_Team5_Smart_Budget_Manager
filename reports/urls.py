from django.urls import path

from .views import CategoryBreakdownView


urlpatterns = [
    path("analytics/", CategoryBreakdownView.as_view(), name="analytics-breakdown"),
]