"""Event deduplication cache to prevent processing the same Slack event twice."""

from collections import OrderedDict
from time import time
from typing import Optional


class EventCache:
    """
    Simple TTL cache for tracking recently processed events.
    
    Prevents duplicate processing when Slack retries the same event
    due to timeouts or network issues.
    """

    def __init__(self, ttl_seconds: int = 300):
        """
        Initialize the event cache.
        
        Args:
            ttl_seconds: Time-to-live for cache entries (default: 5 minutes)
        """
        self.cache: OrderedDict[str, float] = OrderedDict()
        self.ttl = ttl_seconds

    def has_event(self, event_id: str) -> bool:
        """
        Check if an event has been processed recently.
        
        Args:
            event_id: Unique identifier for the event
            
        Returns:
            True if event exists in cache, False otherwise
        """
        self._cleanup()
        return event_id in self.cache

    def add_event(self, event_id: str) -> None:
        """
        Mark an event as processed.
        
        Args:
            event_id: Unique identifier for the event
        """
        self.cache[event_id] = time()

    def get_age(self, event_id: str) -> Optional[float]:
        """
        Get how long ago an event was processed.
        
        Args:
            event_id: Unique identifier for the event
            
        Returns:
            Seconds since event was processed, or None if not in cache
        """
        if event_id not in self.cache:
            return None
        return time() - self.cache[event_id]

    def _cleanup(self) -> None:
        """Remove expired entries from the cache."""
        now = time()
        expired_keys = [
            key for key, timestamp in self.cache.items()
            if now - timestamp > self.ttl
        ]
        for key in expired_keys:
            del self.cache[key]

