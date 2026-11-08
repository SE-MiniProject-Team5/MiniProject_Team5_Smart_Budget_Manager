from rest_framework import generics, status
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Alert, Budget
from .permissions import IsOwner
from .serializers import AlertSerializer, BudgetSerializer
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


class AlertListView(generics.ListAPIView):
    """GET /api/v1/alerts/ -> the caller's active (unacknowledged) alerts, newest first (FR-015).

    The front end calls this on login and every dashboard load.
    """

    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Alert.objects.filter(user=self.request.user, acknowledged=False)
            .select_related("budget__category")
            .order_by("-created_at")
        )


class AlertAcknowledgeView(APIView):
    """POST /api/v1/alerts/<id>/acknowledge/ -> marks one of the caller's alerts as seen (FR-015).

    It then disappears from GET /api/v1/alerts/. Another user's alert gives 404, so ids cannot be probed.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        alert = Alert.objects.filter(pk=pk, user=request.user).first()
        if alert is None:
            return Response({"detail": "Alert not found."}, status=status.HTTP_404_NOT_FOUND)
        alert.acknowledged = True
        alert.save(update_fields=["acknowledged"])
        return Response(AlertSerializer(alert).data)
