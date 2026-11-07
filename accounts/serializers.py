from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User
class RegisterSerializer(serializers.Serializer):
    """Checks the JSON sent to POST /api/v1/auth/register/ (FR-001)."""
    # 150 = the length of Django's username field, which we fill with the email.
    email = serializers.EmailField(max_length=150)
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    def validate_password(self, value):
        validate_password(value) # Django validators from settings.py: at least 8 characters
        return value
class LoginSerializer(serializers.Serializer):
    """Checks the JSON sent to POST /api/v1/auth/login/ (FR-003). Only the
    shape is checked here."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)
class UserSerializer(serializers.ModelSerializer):
    """The only user fields the API ever returns (SEC-006).
    An explicit allow-list: the password hash and every other field are left
    out on purpose,
    so adding a field to the User model can never leak it by accident.
    """
    class Meta:
        model = User
        fields = ["id", "email", "role"]
        read_only_fields = fields

