from rest_framework import serializers

from expenses.models import Category


class AdminCategorySerializer(serializers.ModelSerializer):
    """A master (predefined) category as administrators manage it (FR-019). name <= 50 characters."""

    class Meta:
        model = Category
        fields = ["id", "name", "is_active"]
        read_only_fields = ["id"]

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Category name cannot be blank.")
        if "<" in value or ">" in value:
            raise serializers.ValidationError("The characters < and > are not allowed.")
        return value

    def create(self, validated_data):
        validated_data["owner"] = None  # master categories belong to nobody
        return super().create(validated_data)
