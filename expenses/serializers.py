from rest_framework import serializers

from .models import Expense
from .services import category_problem


class ExpenseSerializer(serializers.ModelSerializer):
    """Validates expenses (FR-005, FR-008). amount > 0 and note <= 255 come from the model's own rules."""

    class Meta:
        model = Expense
        fields = ["id", "category", "amount", "expense_date", "note", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_category(self, category):
        problem = category_problem(category, self.context["request"].user)
        if problem:
            raise serializers.ValidationError(problem)
        return category