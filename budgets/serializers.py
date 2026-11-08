from rest_framework import serializers

from expenses.services import category_problem

from .models import Alert, Budget
from .services import end_date, spent_for


class BudgetSerializer(serializers.ModelSerializer):
    """Validates budgets (FR-009, FR-012) and reports cumulative spend (FR-011)."""

    end_date = serializers.SerializerMethodField()
    spent = serializers.SerializerMethodField()
    remaining = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = ["id", "category", "period", "limit_amount", "start_date", "end_date", "spent", "remaining"]
        read_only_fields = ["id"]

    def get_end_date(self, budget):
        return end_date(budget.period, budget.start_date)

    def get_spent(self, budget):
        return f"{spent_for(budget):.2f}"

    def get_remaining(self, budget):
        return f"{budget.limit_amount - spent_for(budget):.2f}"

    def validate_category(self, category):
        problem = category_problem(category, self.context["request"].user)
        if problem:
            raise serializers.ValidationError(problem)
        return category

    def validate_limit_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Budget limit must be greater than zero.")
        return value

    def validate_period(self, value):
        if value not in Budget.Period.values:
            raise serializers.ValidationError("Period must be WEEKLY or MONTHLY.")
        return value


class AlertSerializer(serializers.ModelSerializer):
    """An alert as the user sees it (FR-015), with the budget it belongs to."""

    message = serializers.CharField(source="get_threshold_type_display", read_only=True)
    category = serializers.CharField(source="budget.category.name", read_only=True)

    class Meta:
        model = Alert
        fields = ["id", "budget", "category", "threshold_type", "message", "created_at", "acknowledged"]
        read_only_fields = fields
