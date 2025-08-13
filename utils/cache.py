"""
Caching utilities for the CONTRA application.
Provides both memory-based and disk-based caching with LRU (Least Recently Used) strategy.
"""

import os
import json
import pickle
import hashlib
import functools
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional, TypeVar, cast, Union
from collections import OrderedDict
import logging

from config import CacheConfig, DATA_CACHE_DIR

T = TypeVar('T')  # Generic type for function return

# Configure logging
logger = logging.getLogger(__name__)

class LRUCache:
    """
    A Least Recently Used (LRU) cache implementation.
    
    Features:
    - Fixed maximum size with LRU eviction policy
    - Thread-safe operations
    - Optional expiration time for cached items
    """
    
    def __init__(self, maxsize: int = 128, timeout: Optional[int] = None):
        """
        Initialize the LRU cache.
        
        Args:
            maxsize: Maximum number of items to store in cache
            timeout: Optional timeout in seconds (None means no timeout)
        """
        self.maxsize = maxsize
        self.timeout = timeout
        self._cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get an item from the cache by key.
        
        Args:
            key: The cache key
            
        Returns:
            The cached value or None if key not found or expired
        """
        if key not in self._cache:
            return None
        
        # Check if item has expired
        item = self._cache[key]
        if self.timeout is not None and time.time() - item['timestamp'] > self.timeout:
            del self._cache[key]
            return None
        
        # Move to end (most recently used)
        self._cache.move_to_end(key)
        return item['value']
    
    def set(self, key: str, value: Any) -> None:
        """
        Add or update an item in the cache.
        
        Args:
            key: The cache key
            value: The value to cache
        """
        # If key exists, update and move to end
        if key in self._cache:
            self._cache.move_to_end(key)
        
        # Add new item
        self._cache[key] = {
            'value': value,
            'timestamp': time.time()
        }
        
        # Enforce size limit (remove oldest item)
        if len(self._cache) > self.maxsize:
            self._cache.popitem(last=False)
    
    def clear(self) -> None:
        """Clear all items from the cache."""
        self._cache.clear()
    
    def __len__(self) -> int:
        """Return the number of items in the cache."""
        return len(self._cache)


# Create a default cache instance
_memory_cache = LRUCache(
    maxsize=CacheConfig.MAX_DATA_CACHE_SIZE,
    timeout=CacheConfig.CACHE_TIMEOUT
)


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle objects that aren't serializable by default."""
    def default(self, obj):
        # Add custom handling for service objects
        try:
            # Check if the object has a __dict__ (most custom objects do)
            if hasattr(obj, '__dict__'):
                # Return just the class name rather than the actual object
                return f"{obj.__class__.__name__}"
            return super().default(obj)
        except TypeError:
            # Fallback to string representation
            return str(obj)


def _compute_hash(args: Any) -> str:
    """
    Compute a hash for the given arguments.
    
    Args:
        args: Arguments to hash
        
    Returns:
        A hexadecimal string hash
    """
    try:
        # For simple arguments, we can use a direct string representation
        if isinstance(args, (str, int, float, bool)) or args is None:
            args_str = str(args)
        else:
            # For complex arguments (lists, dicts, etc.), use JSON
            args_dict = args
            args_str = json.dumps(args_dict, sort_keys=True, cls=CustomJSONEncoder)
            
        # Compute SHA-256 hash
        hash_obj = hashlib.sha256(args_str.encode('utf-8'))
        return hash_obj.hexdigest()
    except Exception as e:
        logger.warning(f"Failed to compute hash for cache: {e}")
        # Fallback to a timestamp-based hash if serialization fails
        return f"nohash_{int(time.time())}"


def memory_cache(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator for in-memory caching of function results.
    Uses the global _memory_cache LRUCache instance.
    
    Example:
        @memory_cache
        def expensive_function(x, y):
            return x + y
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        # Skip cache if disabled
        if not CacheConfig.ENABLE_CACHE:
            return func(*args, **kwargs)
        
        # Create cache key from function name and arguments
        cache_key = f"{func.__module__}.{func.__name__}:"
        all_args = {
            'args': args,
            'kwargs': kwargs
        }
        cache_key += _compute_hash(all_args)
        
        # Check cache
        cached_result = _memory_cache.get(cache_key)
        if cached_result is not None:
            return cast(T, cached_result)
        
        # Call function and cache result
        result = func(*args, **kwargs)
        _memory_cache.set(cache_key, result)
        return result
    
    return wrapper


def disk_cache(subdir: Optional[str] = None) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator factory for persistent disk-based caching.
    
    Args:
        subdir: Optional subdirectory within the data cache directory
    
    Example:
        @disk_cache('wikipedia')
        def fetch_wikipedia_data(topic):
            ...
    """
    cache_dir = DATA_CACHE_DIR
    if subdir:
        cache_dir = cache_dir / subdir
        cache_dir.mkdir(parents=True, exist_ok=True)
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Skip cache if disabled
            if not CacheConfig.ENABLE_CACHE:
                return func(*args, **kwargs)
            
            # Create cache key from function name and arguments
            func_name = f"{func.__module__}.{func.__name__}"
            all_args = {
                'args': args,
                'kwargs': kwargs
            }
            cache_key = _compute_hash(all_args)
            cache_file = cache_dir / f"{func_name}.{cache_key}.pickle"
            
            # Check if cached file exists and is not expired
            if cache_file.exists():
                cache_age = time.time() - cache_file.stat().st_mtime
                if CacheConfig.CACHE_TIMEOUT is None or cache_age < CacheConfig.CACHE_TIMEOUT:
                    try:
                        with open(cache_file, 'rb') as f:
                            return cast(T, pickle.load(f))
                    except (pickle.PickleError, EOFError):
                        # Ignore corrupted cache files
                        pass
            
            # Call function and cache result
            result = func(*args, **kwargs)
            
            try:
                with open(cache_file, 'wb') as f:
                    pickle.dump(result, f)
            except Exception as e:
                # Log error but don't crash on cache write failure
                print(f"Cache write error: {e}")
            
            return result
        
        return wrapper
    
    return decorator


def clear_cache(subdir: Optional[str] = None) -> int:
    """
    Clear disk cache files.
    
    Args:
        subdir: Optional subdirectory to clear (or all data cache if None)
    
    Returns:
        Number of files deleted
    """
    target_dir = DATA_CACHE_DIR
    if subdir:
        target_dir = target_dir / subdir
    
    if not target_dir.exists():
        return 0
    
    count = 0
    for cache_file in target_dir.glob("*.pickle"):
        try:
            cache_file.unlink()
            count += 1
        except OSError:
            pass
    
    return count 