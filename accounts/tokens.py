"""Signed login tokens (FR-004, SEC-004). A token is valid for at most 24
hours."""
from django.core import signing
SALT = "smartspend.auth.token"
MAX_AGE_SECONDS = 24 * 60 * 60 # FR-004: no more than 24 hours
def issue_token(user):
    """Return a signed, timestamped token that identifies this user."""
    return signing.dumps({"uid": str(user.pk)}, salt=SALT)
def read_token(token):
    """Return the user id inside a valid token. Raises signing.BadSignature
    if it is
    tampered with, malformed or older than MAX_AGE_SECONDS (SignatureExpired
    is a BadSignature)."""
    data = signing.loads(token, salt=SALT, max_age=MAX_AGE_SECONDS)
    return data["uid"]
