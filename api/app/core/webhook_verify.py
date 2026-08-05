"""
Synkora API — Webhook Verification

Utilities for verifying GitHub webhook signatures (HMAC-SHA256).
"""

import hashlib
import hmac
from typing import Optional

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("webhook_verify")


def verify_github_signature(
    payload: bytes,
    signature_header: Optional[str],
    secret: Optional[str] = None,
) -> bool:
    """
    Verify that a webhook payload was signed by GitHub.

    Args:
        payload: Raw request body bytes.
        signature_header: Value of the X-Hub-Signature-256 header.
        secret: Webhook secret. Defaults to settings.GITHUB_WEBHOOK_SECRET.

    Returns:
        True if the signature is valid, False otherwise.
    """
    webhook_secret = secret or getattr(settings, "GITHUB_WEBHOOK_SECRET", None)

    if not webhook_secret:
        logger.warning("webhook_secret_not_configured")
        return False

    if not signature_header:
        logger.warning("missing_signature_header")
        return False

    # GitHub sends: sha256=<hex_digest>
    if not signature_header.startswith("sha256="):
        logger.warning("invalid_signature_format")
        return False

    expected_signature = signature_header[7:]  # Strip "sha256="

    computed = hmac.new(
        key=webhook_secret.encode("utf-8"),
        msg=payload,
        digestmod=hashlib.sha256,
    ).hexdigest()

    is_valid = hmac.compare_digest(computed, expected_signature)

    if not is_valid:
        logger.warning("webhook_signature_mismatch")

    return is_valid
