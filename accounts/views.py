from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer
from .services import DuplicateEmailError, register_user
class RegisterView(APIView):
    """POST /api/v1/auth/register/ -> 201 created, 400 invalid input, 409
    duplicate email (SAD 8, 9.1)."""
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True) # invalid email or short password -> 400
        data = serializer.validated_data
        try:
            user = register_user(data["email"], data["password"])
        except DuplicateEmailError:
            return Response(
        {"email": ["An account with this email already exists."]},
        status=status.HTTP_409_CONFLICT,
        )
        # Only id and email go back: never the password or its hash (SEC006).
        return Response({"id": str(user.id), "email": user.email},
        status=status.HTTP_201_CREATED)