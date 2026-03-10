from cachetools import TTLCache
from functools import wraps
import hashlib
import json

# Per-resource TTL caches
_overview_cache = TTLCache(maxsize=200, ttl=60)         # 1 minute
_technicals_cache = TTLCache(maxsize=200, ttl=300)      # 5 minutes
_fundamentals_cache = TTLCache(maxsize=200, ttl=3600)   # 1 hour
_news_cache = TTLCache(maxsize=200, ttl=900)            # 15 minutes
_research_cache = TTLCache(maxsize=50, ttl=1800)        # 30 minutes
_signals_cache = TTLCache(maxsize=200, ttl=120)         # 2 minutes
_competitors_cache = TTLCache(maxsize=200, ttl=3600)    # 1 hour
_history_cache = TTLCache(maxsize=200, ttl=300)         # 5 minutes


def _make_key(*args, **kwargs) -> str:
    raw = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
    return hashlib.md5(raw.encode()).hexdigest()


def cached(cache: TTLCache):
    """Decorator that caches async function results in the given TTLCache."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = _make_key(func.__name__, *args, **kwargs)
            if key in cache:
                return cache[key]
            result = await func(*args, **kwargs)
            cache[key] = result
            return result
        return wrapper
    return decorator


# Convenience decorators
def cache_overview(func):
    return cached(_overview_cache)(func)

def cache_technicals(func):
    return cached(_technicals_cache)(func)

def cache_fundamentals(func):
    return cached(_fundamentals_cache)(func)

def cache_news(func):
    return cached(_news_cache)(func)

def cache_research(func):
    return cached(_research_cache)(func)

def cache_signals(func):
    return cached(_signals_cache)(func)

def cache_competitors(func):
    return cached(_competitors_cache)(func)

def cache_history(func):
    return cached(_history_cache)(func)


def get_research_cache_key(ticker: str) -> str:
    from datetime import date
    return _make_key("research", ticker.upper(), str(date.today()))


def get_cached_research(ticker: str) -> str | None:
    key = get_research_cache_key(ticker)
    return _research_cache.get(key)


def set_cached_research(ticker: str, content: str):
    key = get_research_cache_key(ticker)
    _research_cache[key] = content
