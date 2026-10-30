
from rest_framework import serializers

from .models import Budget
from expenses.services import category_problem


class BudgetSerializer(serializers.ModelSerializer):
    """Validates budget creation data (FR-009, FR-012)."""

    class Meta:
        model = Budget
        fields = [
            "id",
            "category",
            "period",
            "limit_amount",
            "start_date",
        ]
        read_only_fields = ["id"]

    def validate_category(self, category):
        problem = category_problem(
            category,
            self.context["request"].user,
        )
        if problem:
            raise serializers.ValidationError(problem)
        return category

    def validate_limit_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Budget limit must be greater than zero."
            )
        return value

    def validate_period(self, value):
        if value not in Budget.Period.values:
            raise serializers.ValidationError(
                "Period must be WEEKLY or MONTHLY."
            )
        return value
