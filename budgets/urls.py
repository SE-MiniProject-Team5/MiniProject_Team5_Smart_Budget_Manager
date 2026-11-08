from django.urls import path

from .views import AlertAcknowledgeView, AlertListView, BudgetDetailView, BudgetListCreateView

urlpatterns = [
    path("budgets/", BudgetListCreateView.as_view(), name="budget-list"),
    path("budgets/<uuid:pk>/", BudgetDetailView.as_view(), name="budget-detail"),
    path("alerts/", AlertListView.as_view(), name="alert-list"),
    path("alerts/<uuid:pk>/acknowledge/", AlertAcknowledgeView.as_view(), name="alert-acknowledge"),
]
