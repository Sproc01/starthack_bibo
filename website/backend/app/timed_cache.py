import time
import hashlib
import inspect
import pandas as pd
from enum import Enum
from typing import Any, Callable, Optional, TypeVar
from functools import wraps

from util import SingletonMeta


class CacheCategory(Enum):
    WEATHER_FORECAST = "weather_forecast"
    STRESS_PREDICTION = "stress_prediction"


class TimedCache(metaclass=SingletonMeta):
    def __init__(self):
        # Associate an automatically generated key with the cached data, the time creation and the TTL
        self.cache: dict[str, tuple[Any, float, int]] = {}

    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            cached_value, timestamp, ttl = self.cache[key]

            # Cache entry still valid
            if time.time() - timestamp < ttl:
                return cached_value
            else:
                # Remove expired entry
                del self.cache[key]
        return None

    def set(self, key: str, cached_value: Any, ttl_seconds: int) -> None:
        self.cleanup_expired()
        self.cache[key] = (cached_value, time.time(), ttl_seconds)

    def delete(self, key: str) -> bool:
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    def clear(self) -> None:
        self.cache.clear()

    def cleanup_expired(self) -> int:
        current_time = time.time()
        expired_keys = [key for key, (_, timestamp, ttl) in self.cache.items() if current_time - timestamp >= ttl]

        for key in expired_keys:
            del self.cache[key]

        return len(expired_keys)


def generate_cache_key(*args: Any, **kwargs: Any) -> str:
    hasher = hashlib.sha1()

    # Recursively update hash with different data types
    def update_hash(data: Any) -> None:
        if isinstance(data, pd.DataFrame):
            hasher.update(data.columns.to_numpy().tobytes())
            hasher.update(pd.util.hash_pandas_object(data).to_numpy().tobytes())
        elif isinstance(data, (list, tuple)):
            for item in data:
                update_hash(item)
        elif isinstance(data, dict):
            for key, value in sorted(data.items()):
                update_hash(key)
                update_hash(value)
        else:
            hasher.update(str(data).encode())

    # Process all arguments
    for arg in args:
        update_hash(arg)

    # Process keyword arguments
    for key, value in sorted(kwargs.items()):
        update_hash(key)
        update_hash(value)

    return hasher.hexdigest()


T = TypeVar("T")


def cached(cache_instance: TimedCache, category: CacheCategory, ttl_seconds: int) -> Callable:

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            func_key = f"{func.__module__}.{func.__name__}"
            if category:
                func_key = f"{category.value}.{func_key}"
            cache_key = generate_cache_key(func_key, *args, **kwargs)

            # Try to retrieve from cache
            cached_result = cache_instance.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Call the function if not cached
            result = await func(*args, **kwargs)

            # Store in cache
            cache_instance.set(cache_key, result, ttl_seconds)
            return result

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            func_key = f"{func.__module__}.{func.__name__}"
            if category:
                func_key = f"{category.value}.{func_key}"
            cache_key = generate_cache_key(func_key, *args, **kwargs)

            # Try to retrieve from cache
            cached_result = cache_instance.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Call the function if not cached
            result = func(*args, **kwargs)

            # Store in cache
            cache_instance.set(cache_key, result, ttl_seconds)
            return result

        # Choose the appropriate wrapper based on whether the function is async
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
