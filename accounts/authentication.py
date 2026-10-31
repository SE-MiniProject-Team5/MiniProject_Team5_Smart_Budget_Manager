"""Bearer token authentication for every API endpoint (SEC-004).
A request sends: Authorization: Bearer <token from /api/v1/auth/login/>
A missing header means "not logged in". A malformed, tampered or expired
token gives HTTP 401.
"""
from django.core import signing
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from smartspend.security_log import log_security_event
from .models import User
from .tokens import read_token
class BearerTokenAuthentication(BaseAuthentication):
    keyword = "Bearer"
    def authenticate(self, request):
        parts = get_authorization_header(request).split()
        if not parts or parts[0].lower() != self.keyword.lower().encode():
            return None # no token sent: other checks decide (usually 401)
        if len(parts) != 2:
            self._reject(request)
        try:
            user_id = read_token(parts[1].decode())
            user = User.objects.get(pk=user_id, is_active=True)
        except (signing.BadSignature, UnicodeError, ValueError,
            User.DoesNotExist):
            self._reject(request)
        return (user, None)
    def authenticate_header(self, request):
        # Makes DRF answer 401 (not 403) when a protected endpoint gets no valid token.
        return self.keyword
    def _reject(self, request):
        log_security_event("invalid_token", "anonymous", request.path) # SEC-005
        raise AuthenticationFailed("Invalid or expired token.")