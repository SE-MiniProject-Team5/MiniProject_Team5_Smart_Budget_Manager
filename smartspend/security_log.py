
"""Security event logging (SEC-005, SRS 7.1 Accountability).

Every entry has a timestamp (added by the log format in settings.py),
the event name, the account identifier and the endpoint.
Never pass a password to this function.
"""

import logging

logger = logging.getLogger("security")


def log_security_event(event, account, endpoint):
    """Record one security-relevant event, e.g. a failed login or a blocked admin call."""
    logger.warning(
        "event=%s account=%s endpoint=%s",
        event,
        account or "anonymous",
        endpoint,
    )
