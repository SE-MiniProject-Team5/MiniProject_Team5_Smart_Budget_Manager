from rest_framework import generics, status
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated

from .models import Budget
from .permissions import IsOwner
from .serializers import BudgetSerializer
from .services import overlaps_existing


class BudgetConflict(APIException):
    """HTTP 409 for an overlapping budget period (SAD 9.1)."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = (
        "A budget for this category already covers part of this period."
    )
    default_code = "budget_overlap"


class BudgetListCreateView(generics.ListCreateAPIView):
    """GET lists the caller's budgets; POST creates one (FR-009, FR-012)."""

    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.budgets.order_by("-start_date")

    def perform_create(self, serializer):
        data = serializer.validated_data
        if overlaps_existing(
            self.request.user,
            data["category"],
            data["period"],
            data["start_date"],
        ):
            raise BudgetConflict()
        serializer.save(user=self.request.user)


class BudgetDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET, PUT, PATCH, DELETE /api/v1/budgets/<id>/ for the owner only."""

    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def perform_update(self, serializer):
        budget = serializer.instance
        data = serializer.validated_data

        category = data.get("category", budget.category)
        period = data.get("period", budget.period)
        start = data.get("start_date", budget.start_date)

        if overlaps_existing(
            self.request.user,
            category,
            period,
            start,
            exclude_id=budget.id,
        ):
            raise BudgetConflict()

        serializer.save()
