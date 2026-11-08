from datetime import date

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services

MAX_TREND_DAYS = 366


def date_range(request):
    """Read ?from=YYYY-MM-DD&to=YYYY-MM-DD. Returns (start, end, None) or (None, None, error response)."""
    try:
        start = date.fromisoformat(request.query_params["from"])
        end = date.fromisoformat(request.query_params["to"])
    except (KeyError, ValueError):
        return None, None, Response(
            {"detail": "Give both from and to as dates, e.g. ?from=2026-01-01&to=2026-01-31."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if start > end:
        return None, None, Response({"detail": "from must not be after to."}, status=status.HTTP_400_BAD_REQUEST)
    return start, end, None


class CategoryBreakdownView(APIView):
    """GET /api/v1/analytics/?from=YYYY-MM-DD&to=YYYY-MM-DD -> spend per category (FR-016)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        start, end, error = date_range(request)
        if error:
            return error
        breakdown, total = services.category_breakdown(request.user, start, end)
        return Response({"from": start, "to": end, "total": total, "categories": breakdown})


class SpendTrendView(APIView):
    """GET /api/v1/analytics/trend/?from=...&to=...&granularity=daily|weekly -> chart points (FR-017).

    granularity defaults to daily. A range longer than 366 days gives 400.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        start, end, error = date_range(request)
        if error:
            return error
        granularity = request.query_params.get("granularity", "daily")
        if granularity not in ("daily", "weekly"):
            return Response({"detail": "granularity must be daily or weekly."}, status=status.HTTP_400_BAD_REQUEST)
        if (end - start).days >= MAX_TREND_DAYS:
            return Response({"detail": "The range can be at most 366 days."}, status=status.HTTP_400_BAD_REQUEST)
        points = services.spend_trend(request.user, start, end, granularity)
        return Response({"from": start, "to": end, "granularity": granularity, "points": points})
