from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from smartspend.security_log import log_security_event
from .serializers import LoginSerializer, RegisterSerializer
from .services import DuplicateEmailError, authenticate_user, register_user
from .tokens import MAX_AGE_SECONDS, issue_token
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
        return Response({"id": str(user.id), "email": user.email},status=status.HTTP_201_CREATED)

class LoginView(APIView):
    """POST /api/v1/auth/login/ -> 200 with a token, 400 bad input, 401 wrong
    email or password (FR-003, FR-004)."""
    permission_classes = [AllowAny]
    authentication_classes = [] # logging in must work without any token
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = authenticate_user(data["email"], data["password"])
        if user is None:
        # SEC-005: log the failed attempt with the account and endpoint, never the password.
            log_security_event("failed_login", data["email"], request.path)
            return Response(
            {"detail": "Invalid email or password."},
            status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(
        {"token": issue_token(user), "token_type": "Bearer",
        "expires_in": MAX_AGE_SECONDS},
        status=status.HTTP_200_OK,
        )
