import functools
import time
import requests
import os
import hashlib
import pickle
from enum import Enum

MUSICBRAINZ_API = "https://musicbrainz.org/ws/2/"
LIVE_MUSIC_ARCHIVE_API = "https://archive.org/advancedsearch.php"

CACHE_DIR = "./.cache"

# Why cache?
# 1. API rate limits: Many APIs have rate limits, and caching can help you avoid hitting those limits.
# 2. Performance: Caching can significantly speed up your application by reducing the need to make network requests.


def cache(ttl=-1, cache_dir=CACHE_DIR):
    os.makedirs(cache_dir, exist_ok=True)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key_str = f"{func.__name__}:{args}:{kwargs}"
            key_hash = hashlib.md5(key_str.encode()).hexdigest()
            cache_file = os.path.join(cache_dir, key_hash + ".pkl")
            if os.path.exists(cache_file):
                with open(cache_file, "rb") as f:
                    result, timestamp = pickle.load(f)
                current_time = time.time()
                if ttl is None or (current_time - timestamp < ttl):
                    print(f"Get cache: {func.__name__} {key_hash}")
                    return result
                elif ttl < 0:
                    return result
                else:
                    print(f"Expire cache: {func.__name__} {key_hash}")
                    os.remove(cache_file)
            result = func(*args, **kwargs)
            with open(cache_file, "wb") as f:
                pickle.dump((result, time.time()), f)
            return result

        return wrapper
    return decorator
