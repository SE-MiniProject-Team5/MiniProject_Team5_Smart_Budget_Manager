from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Category, Expense
from .permissions import IsOwner
from .serializers import CategorySerializer, ExpenseSerializer


class ExpenseListCreateView(generics.ListCreateAPIView):
    """GET lists the caller's own expenses; POST adds one (FR-005, FR-008)."""

    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.expenses.order_by("-expense_date", "-created_at")

    def perform_create(self, serializer):
        # The owner always comes from the logged-in user, never from the JSON.
        serializer.save(user=self.request.user)


class ExpenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET, PUT, PATCH, DELETE /api/v1/expenses/<id>/ for the owner only (FR-006).

    Another user's expense gives 403 (Test Plan 5.1); an id that does not exist gives 404.
    """

    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated, IsOwner]


class CategoryListCreateView(generics.ListCreateAPIView):
    """GET lists active categories the caller may use; POST creates a custom one (FR-007).

    Usable = predefined (no owner) or the caller's own, and active (SRS 6.5 business rule).
    """

    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Category.objects.filter(is_active=True).filter(
            Q(owner__isnull=True) | Q(owner=user)
        ).order_by("name")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)