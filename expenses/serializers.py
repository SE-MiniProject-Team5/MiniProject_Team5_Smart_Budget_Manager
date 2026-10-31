from rest_framework import serializers

from .models import Category, Expense
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


class CategorySerializer(serializers.ModelSerializer):
    """Predefined and custom categories (FR-007). name <= 50 characters comes from the model."""

    is_custom = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "is_custom"]
        read_only_fields = ["id"]

    def get_is_custom(self, category):
        return category.owner_id is not None

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Category name cannot be blank.")
        return value