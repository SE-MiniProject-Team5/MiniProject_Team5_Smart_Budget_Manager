from django.urls import path

from .views import CategoryListCreateView, ExpenseDetailView, ExpenseListCreateView

urlpatterns = [
    path("expenses/", ExpenseListCreateView.as_view(), name="expense-list"),
    path("expenses/<uuid:pk>/", ExpenseDetailView.as_view(), name="expense-detail"),
    path("categories/", CategoryListCreateView.as_view(), name="category-list"),
]