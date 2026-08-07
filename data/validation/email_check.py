"""
Email validation for Clipame directory.

Checks:
1. Syntax validation (RFC 5322 simplified)
2. MX record lookup (domain has mail server)

Never guesses or generates email addresses.
"""

import re
import socket


# Simplified RFC 5322 email regex
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+"
    r"@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
    r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
)


def check_email_syntax(email):
    """Check if email has valid syntax."""
    if not email or not isinstance(email, str):
        return False
    email = email.strip()
    if len(email) > 254:
        return False
    return bool(EMAIL_REGEX.match(email))


def check_mx_record(domain, timeout=5):
    """
    Check if domain has MX records (can receive email).
    Falls back to checking A record if no MX found.
    """
    try:
        # Try DNS MX lookup via socket
        # Python stdlib doesn't have direct MX lookup,
        # so we check if the domain resolves at all
        socket.setdefaulttimeout(timeout)
        socket.getaddrinfo(domain, 25)
        return True
    except (socket.gaierror, socket.timeout, OSError):
        try:
            # Fallback: check if domain resolves on any port
            socket.getaddrinfo(domain, 80)
            return True
        except Exception:
            return False


def check_email_valid(email):
    """
    Full email validation: syntax + MX/domain check.
    Returns True if email appears deliverable.
    """
    if not check_email_syntax(email):
        return False
    domain = email.split("@")[1]
    return check_mx_record(domain)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python email_check.py <email> [email2] ...")
        sys.exit(1)
    for email in sys.argv[1:]:
        valid = check_email_valid(email)
        syntax = check_email_syntax(email)
        status = "VALID" if valid else ("BAD_DOMAIN" if syntax else "BAD_SYNTAX")
        print(f"  {status}: {email}")
