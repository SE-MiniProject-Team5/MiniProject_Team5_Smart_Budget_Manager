
from django.urls import path

from .views import BudgetListCreateView

urlpatterns = [
    path("budgets/", BudgetListCreateView.as_view(), name="budget-list-create"),
]
