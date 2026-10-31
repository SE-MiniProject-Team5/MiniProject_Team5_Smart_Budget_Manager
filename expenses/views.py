from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Expense
from .permissions import IsOwner
from .serializers import ExpenseSerializer


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