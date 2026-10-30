
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import BudgetSerializer
from .services import has_overlapping_budget


class BudgetListCreateView(APIView):
    """Create budgets while preventing overlapping periods."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BudgetSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        if has_overlapping_budget(
            user=request.user,
            category=serializer.validated_data["category"],
            period=serializer.validated_data["period"],
            start_date=serializer.validated_data["start_date"],
        ):
            return Response(
                {"detail": "An overlapping budget already exists."},
                status=status.HTTP_409_CONFLICT,
            )

        budget = serializer.save(user=request.user)

        return Response(
            BudgetSerializer(budget).data,
            status=status.HTTP_201_CREATED,
        )
