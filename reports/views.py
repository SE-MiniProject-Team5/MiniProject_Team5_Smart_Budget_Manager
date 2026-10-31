from datetime import date

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import category_breakdown


class CategoryBreakdownView(APIView):
    """GET /api/v1/analytics/?from=YYYY-MM-DD&to=YYYY-MM-DD."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            start = date.fromisoformat(request.query_params["from"])
            end = date.fromisoformat(request.query_params["to"])
        except (KeyError, ValueError):
            return Response(
                {
                    "detail": (
                        "Give both from and to as dates, "
                        "e.g. ?from=2026-01-01&to=2026-01-31."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if start > end:
            return Response(
                {"detail": "from must not be after to."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        breakdown, total = category_breakdown(request.user, start, end)

        return Response({
            "from": start,
            "to": end,
            "total": total,
            "categories": breakdown,
        })