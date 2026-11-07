"""Server-side input sanitisation for free-text fields (SEC-003).

Every text field a user types (expense notes, category names) goes through clean_text
before it is saved, whatever the client did. The rules:
- surrounding spaces are removed;
- control characters (tabs, newlines, null bytes and similar) are rejected;
- angle brackets < and > are rejected, so HTML or <script> tags can never be stored.
"""
from rest_framework import serializers

FORBIDDEN_CHARACTERS = "<>"


def clean_text(value):
    """Return the trimmed text, or raise a 400 validation error if it is unsafe."""
    value = value.strip()
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        raise serializers.ValidationError("Control characters are not allowed.")
    if any(ch in FORBIDDEN_CHARACTERS for ch in value):
        raise serializers.ValidationError("The characters < and > are not allowed.")
    return value
