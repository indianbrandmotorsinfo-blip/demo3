from datetime import datetime
from urllib.parse import urlparse, urljoin
from flask import request


def is_safe_url(target: str) -> bool:
    """Protects against open redirect vulnerabilities."""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


def format_datetime(value, format_str="%b %d, %Y at %I:%M %p"):
    """Template filter for human-readable datetime formatting."""
    if not value:
        return "N/A"
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except Exception:
            return value
    return value.strftime(format_str)


def status_badge_class(status: str) -> str:
    """Returns corresponding Bootstrap badge class for assignment or group status."""
    mapping = {
        "OPEN": "bg-success text-white",
        "FULL": "bg-warning text-dark",
        "CLOSED": "bg-secondary text-white",
        "FORMING": "bg-info text-dark",
        "PENDING": "bg-warning text-dark",
        "APPROVED": "bg-success text-white",
        "REJECTED": "bg-danger text-white",
        "SUBMITTED": "bg-primary text-white",
    }
    return mapping.get(str(status).upper(), "bg-secondary text-white")
