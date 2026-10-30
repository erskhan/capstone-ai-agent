"""Caching service for performance optimization."""

from typing import Any, Optional, Dict
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import json
from sqlalchemy.orm import Session

from shared.logger import get_logger

logger = get_logger("cache_service")


class CacheService:
    """Multi-level caching for decision results and analysis."""

    # In-memory cache (first level)
    _memory_cache: Dict[str, Dict[str, Any]] = {}
    _cache_ttl_seconds = 3600  # 1 hour

    @classmethod
    def set_decision_cache(
        cls,
        application_id: str,
        decision_result: Dict[str, Any],
        ttl_seconds: int = 3600,
    ) -> None:
        """Cache decision result in memory.

        Args:
            application_id: Application ID
            decision_result: Decision data to cache
            ttl_seconds: Time-to-live in seconds
        """
        cls._memory_cache[application_id] = {
            "data": decision_result,
            "expires_at": datetime.utcnow() + timedelta(seconds=ttl_seconds),
        }

        logger.debug(
            f"Cached decision for {application_id}",
            extra={"ttl_seconds": ttl_seconds},
        )

    @classmethod
    def get_decision_cache(cls, application_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached decision result.

        Args:
            application_id: Application ID

        Returns:
            Cached decision or None if expired/not found
        """
        if application_id not in cls._memory_cache:
            return None

        cached = cls._memory_cache[application_id]

        # Check expiration
        if datetime.utcnow() > cached["expires_at"]:
            del cls._memory_cache[application_id]
            logger.debug(f"Cache expired for {application_id}")
            return None

        logger.debug(f"Cache hit for {application_id}")
        return cached["data"]

    @classmethod
    def clear_decision_cache(cls, application_id: str) -> None:
        """Clear cache for an application.

        Args:
            application_id: Application ID
        """
        if application_id in cls._memory_cache:
            del cls._memory_cache[application_id]
            logger.debug(f"Cleared cache for {application_id}")

    @classmethod
    def cache_query_result(
        cls,
        query_key: str,
        result: Any,
        ttl_seconds: int = 300,
    ) -> None:
        """Cache a database query result.

        Args:
            query_key: Unique query identifier
            result: Query result to cache
            ttl_seconds: Time-to-live in seconds
        """
        cache_key = f"query_{query_key}"
        cls._memory_cache[cache_key] = {
            "data": result,
            "expires_at": datetime.utcnow() + timedelta(seconds=ttl_seconds),
        }

    @classmethod
    def get_query_cache(cls, query_key: str) -> Optional[Any]:
        """Retrieve cached query result.

        Args:
            query_key: Unique query identifier

        Returns:
            Cached result or None
        """
        cache_key = f"query_{query_key}"

        if cache_key not in cls._memory_cache:
            return None

        cached = cls._memory_cache[cache_key]

        if datetime.utcnow() > cached["expires_at"]:
            del cls._memory_cache[cache_key]
            return None

        return cached["data"]

    @classmethod
    def get_cache_stats(cls) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Cache stats dictionary
        """
        total_entries = len(cls._memory_cache)
        expired = sum(
            1
            for entry in cls._memory_cache.values()
            if datetime.utcnow() > entry["expires_at"]
        )

        return {
            "total_entries": total_entries,
            "expired_entries": expired,
            "active_entries": total_entries - expired,
            "cache_enabled": True,
        }

    @classmethod
    def clear_all(cls) -> None:
        """Clear entire cache."""
        cls._memory_cache.clear()
        logger.info("Cleared entire cache")


def cache_decision(ttl_seconds: int = 3600):
    """Decorator to cache decision results.

    Args:
        ttl_seconds: Time-to-live in seconds
    """

    def decorator(func):
        @wraps(func)
        def wrapper(application_id: str, *args, **kwargs):
            # Try cache first
            cached = CacheService.get_decision_cache(application_id)
            if cached:
                logger.debug(f"Using cached decision for {application_id}")
                return cached

            # Call function
            result = func(application_id, *args, **kwargs)

            # Cache result
            if result:
                CacheService.set_decision_cache(application_id, result, ttl_seconds)

            return result

        return wrapper

    return decorator


def cache_query(ttl_seconds: int = 300):
    """Decorator to cache query results.

    Args:
        ttl_seconds: Time-to-live in seconds
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = hashlib.md5(
                (func.__name__ + json.dumps({str(arg): str(val) for arg, val in enumerate(args)})).encode()
            ).hexdigest()

            # Try cache
            cached = CacheService.get_query_cache(cache_key)
            if cached:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached

            # Call function
            result = func(*args, **kwargs)

            # Cache result
            if result:
                CacheService.cache_query_result(cache_key, result, ttl_seconds)

            return result

        return wrapper

    return decorator
