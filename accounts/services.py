"""Auth business logic (SAD 3.1 Auth Service). Kept apart from the web code
so it can be unit tested."""
from django.db import IntegrityError
from .models import User

class DuplicateEmailError(Exception):
    """Raised when the email is already registered (FR-002). The view turns
    it into HTTP 409."""
def register_user(email, password):
    """Create a USER-role account. create_user stores a salted one-way hash,
    never the raw password (SEC-001)."""
    if User.objects.filter(email__iexact=email).exists():
        raise DuplicateEmailError(email)
    try:
        return User.objects.create_user(username=email, email=email,
    password=password)
    except IntegrityError as exc: # two requests racing with the same email
        raise DuplicateEmailError(email) from exc