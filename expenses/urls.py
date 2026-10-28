

from django.urls import path

from .views import ExpenseListCreateView

urlpatterns = [
    path("expenses/", ExpenseListCreateView.as_view(), name="expense-list"),
]