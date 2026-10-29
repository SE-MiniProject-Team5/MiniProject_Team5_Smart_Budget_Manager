from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
class RegisterSerializer(serializers.Serializer):
    """Checks the JSON sent to POST /api/v1/auth/register/ (FR-001)."""
    # 150 = the length of Django's username field, which we fill with the email.
    email = serializers.EmailField(max_length=150)
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    def validate_password(self, value):
        validate_password(value) # Django validators from settings.py: at least 8 characters
        return value