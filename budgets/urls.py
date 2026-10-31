from django.urls import path

from .views import BudgetDetailView, BudgetListCreateView

urlpatterns = [
    path("budgets/", BudgetListCreateView.as_view(), name="budget-list"),
    path(
        "budgets/<uuid:pk>/",
        BudgetDetailView.as_view(),
        name="budget-detail",
    ),
]
