"""Slack request signature verification."""

import hashlib
import hmac
import logging
import time

logger = logging.getLogger(__name__)


class SlackRequestVerifier:
    """
    Verifies Slack webhook signatures to ensure requests are authentic.
    
    Implements Slack's signature verification algorithm to prevent
    unauthorized requests and replay attacks.
    """

    def __init__(self, signing_secret: str):
        """
        Initialize the verifier with Slack signing secret.
        
        Args:
            signing_secret: Slack app signing secret from app settings
        """
        self.signing_secret = signing_secret

    def verify(self, body: bytes, timestamp: str, signature: str) -> bool:
        """
        Verify that a request came from Slack.
        
        Args:
            body: Raw request body as bytes
            timestamp: X-Slack-Request-Timestamp header value
            signature: X-Slack-Signature header value
            
        Returns:
            True if signature is valid, False otherwise
        """
        # Reject old requests (replay attack protection)
        if abs(time.time() - int(timestamp)) > 60 * 5:
            logger.warning(f"Request timestamp too old: {timestamp}")
            return False

        # Create signature base string
        sig_basestring = f"v0:{timestamp}:{body.decode('utf-8')}"

        # Generate HMAC signature
        my_signature = "v0=" + hmac.new(
            self.signing_secret.encode(),
            sig_basestring.encode(),
            hashlib.sha256
        ).hexdigest()

        # Compare signatures
        is_valid = hmac.compare_digest(my_signature, signature)
        
        if not is_valid:
            logger.warning("Invalid Slack signature")
        
        return is_valid

