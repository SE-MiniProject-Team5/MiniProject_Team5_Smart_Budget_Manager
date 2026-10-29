from django.shortcuts import render

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

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
