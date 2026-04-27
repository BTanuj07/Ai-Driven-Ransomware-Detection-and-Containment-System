"""
Simple in-memory cache service for API optimization
Reduces database queries for frequently accessed data
"""

from datetime import datetime, timedelta
from typing import Any, Optional, Dict
import threading


class CacheService:
    """Thread-safe in-memory cache with TTL support"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if datetime.now() < entry["expires_at"]:
                    return entry["value"]
                else:
                    # Expired, remove it
                    del self._cache[key]
            return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 5):
        """Set value in cache with TTL (default 5 seconds)"""
        with self._lock:
            self._cache[key] = {
                "value": value,
                "expires_at": datetime.now() + timedelta(seconds=ttl_seconds)
            }
    
    def delete(self, key: str):
        """Delete specific key from cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
    
    def cleanup_expired(self):
        """Remove all expired entries"""
        with self._lock:
            now = datetime.now()
            expired_keys = [
                key for key, entry in self._cache.items()
                if now >= entry["expires_at"]
            ]
            for key in expired_keys:
                del self._cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total = len(self._cache)
            now = datetime.now()
            expired = sum(1 for entry in self._cache.values() if now >= entry["expires_at"])
            return {
                "total_entries": total,
                "active_entries": total - expired,
                "expired_entries": expired
            }


# Global cache instance
cache_service = CacheService()
