"""
Enhanced caching system for Pokemon Translation app
Provides multi-level caching with TTL, compression, and analytics
"""

import hashlib
import json
import os
import pickle
import time
import zlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import streamlit as st

from .logger import get_api_logger


class CacheManager:
    """Advanced caching manager with multiple storage layers and analytics"""

    def __init__(
        self,
        cache_dir: str = "storage/cache",
        max_memory_items: int = 100,
        default_ttl: int = 3600,  # 1 hour
        max_disk_size_mb: int = 500,
    ):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.max_memory_items = max_memory_items
        self.default_ttl = default_ttl
        self.max_disk_size_mb = max_disk_size_mb

        # Memory cache for frequently accessed items
        self.memory_cache: Dict[str, Dict[str, Any]] = {}

        # Cache analytics
        self.analytics = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_requests": 0,
            "memory_usage": 0,
            "disk_usage": 0,
        }

        self.logger = get_api_logger()

        # Load existing analytics
        self._load_analytics()

        # Clean expired entries on startup
        self._cleanup_expired()

    def _get_cache_key(self, url: str, extra_params: Dict = None) -> str:
        """Generate consistent cache key from URL and parameters"""
        cache_data = {"url": url}
        if extra_params:
            cache_data.update(extra_params)

        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()

    def _get_file_path(self, cache_key: str) -> Path:
        """Get file path for cache key"""
        return self.cache_dir / f"{cache_key}.cache"

    def _load_analytics(self):
        """Load cache analytics from disk"""
        analytics_file = self.cache_dir / "analytics.json"
        if analytics_file.exists():
            try:
                with open(analytics_file, "r") as f:
                    loaded_analytics = json.load(f)
                    self.analytics.update(loaded_analytics)
            except Exception as e:
                self.logger.warning(f"Failed to load cache analytics: {e}")

    def _save_analytics(self):
        """Save cache analytics to disk"""
        analytics_file = self.cache_dir / "analytics.json"
        try:
            with open(analytics_file, "w") as f:
                json.dump(self.analytics, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to save cache analytics: {e}")

    def _cleanup_expired(self):
        """Remove expired cache entries"""
        current_time = time.time()
        expired_keys = []

        # Clean memory cache
        for key, entry in list(self.memory_cache.items()):
            if entry["expires_at"] < current_time:
                expired_keys.append(key)

        for key in expired_keys:
            del self.memory_cache[key]
            self.analytics["evictions"] += 1

        # Clean disk cache
        for cache_file in self.cache_dir.glob("*.cache"):
            try:
                with open(cache_file, "rb") as f:
                    data = pickle.load(f)
                    if data.get("expires_at", 0) < current_time:
                        cache_file.unlink()
                        self.analytics["evictions"] += 1
            except Exception:
                # Remove corrupted files
                cache_file.unlink()

    def _enforce_memory_limit(self):
        """Enforce memory cache size limit using LRU eviction"""
        while len(self.memory_cache) > self.max_memory_items:
            # Find least recently used item
            oldest_key = min(
                self.memory_cache.keys(),
                key=lambda k: self.memory_cache[k]["last_accessed"],
            )
            del self.memory_cache[oldest_key]
            self.analytics["evictions"] += 1

    def _enforce_disk_limit(self):
        """Enforce disk cache size limit"""
        total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.cache"))
        max_size = self.max_disk_size_mb * 1024 * 1024

        if total_size > max_size:
            # Remove oldest files first
            cache_files = sorted(
                self.cache_dir.glob("*.cache"), key=lambda f: f.stat().st_mtime
            )

            for cache_file in cache_files:
                cache_file.unlink()
                total_size -= cache_file.stat().st_size
                self.analytics["evictions"] += 1

                if total_size <= max_size * 0.8:  # Keep under 80% of limit
                    break

    def get(self, url: str, extra_params: Dict = None) -> Optional[Dict[str, Any]]:
        """Get cached data for URL"""
        cache_key = self._get_cache_key(url, extra_params)
        current_time = time.time()

        self.analytics["total_requests"] += 1

        # Check memory cache first
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
            if entry["expires_at"] > current_time:
                entry["last_accessed"] = current_time
                self.analytics["hits"] += 1
                self.logger.debug(f"Memory cache hit for: {url}")
                self.logger.debug(f"Memory cache data type: {type(entry['data'])}")
                return entry["data"]
            else:
                # Expired
                del self.memory_cache[cache_key]
                self.analytics["evictions"] += 1

        # Check disk cache
        cache_file = self._get_file_path(cache_key)
        if cache_file.exists():
            try:
                with open(cache_file, "rb") as f:
                    entry = pickle.load(f)

                if entry["expires_at"] > current_time:
                    # Check if data is compressed and decompress if needed
                    if entry.get("compressed", False):
                        try:
                            decompressed_data = json.loads(
                                zlib.decompress(entry["data"]).decode()
                            )
                            entry["data"] = decompressed_data
                        except Exception as decompress_error:
                            self.logger.error(
                                f"Failed to decompress cache data: {decompress_error}"
                            )
                            return None

                    # Move to memory cache for faster access
                    self.memory_cache[cache_key] = {
                        "data": entry["data"],
                        "expires_at": entry["expires_at"],
                        "last_accessed": current_time,
                        "size": len(str(entry["data"])),
                    }

                    self._enforce_memory_limit()
                    self.analytics["hits"] += 1
                    self.logger.debug(f"Disk cache hit for: {url}")
                    self.logger.debug(f"Disk cache data type: {type(entry['data'])}")
                    return entry["data"]
                else:
                    # Expired
                    cache_file.unlink()
                    self.analytics["evictions"] += 1
            except Exception as e:
                self.logger.warning(f"Failed to load cache file {cache_file}: {e}")
                cache_file.unlink()

        self.analytics["misses"] += 1
        return None

    def set(
        self,
        url: str,
        data: Dict[str, Any],
        ttl: Optional[int] = None,
        extra_params: Dict = None,
    ):
        """Store data in cache"""
        cache_key = self._get_cache_key(url, extra_params)
        current_time = time.time()
        expires_at = current_time + (ttl or self.default_ttl)

        # Prepare cache entry
        entry = {
            "data": data,
            "expires_at": expires_at,
            "last_accessed": current_time,
            "created_at": current_time,
            "url": url,
            "size": len(str(data)),
        }

        # Store in memory cache
        self.memory_cache[cache_key] = entry.copy()
        self._enforce_memory_limit()

        # Store in disk cache (compressed)
        cache_file = self._get_file_path(cache_key)
        try:
            with open(cache_file, "wb") as f:
                # Compress data to save disk space
                compressed_entry = entry.copy()
                compressed_entry["data"] = zlib.compress(json.dumps(data).encode())
                compressed_entry["compressed"] = True
                pickle.dump(compressed_entry, f)

            self._enforce_disk_limit()
            self.logger.debug(f"Cached data for: {url}")
        except Exception as e:
            self.logger.error(f"Failed to write cache file {cache_file}: {e}")

        self._save_analytics()

    def delete(self, url: str, extra_params: Dict = None):
        """Delete cached data for URL"""
        cache_key = self._get_cache_key(url, extra_params)

        # Remove from memory
        if cache_key in self.memory_cache:
            del self.memory_cache[cache_key]

        # Remove from disk
        cache_file = self._get_file_path(cache_key)
        if cache_file.exists():
            cache_file.unlink()

        self.logger.debug(f"Deleted cache for: {url}")

    def clear(self, keep_analytics: bool = True):
        """Clear all cached data"""
        # Clear memory cache
        self.memory_cache.clear()

        # Clear disk cache
        for cache_file in self.cache_dir.glob("*.cache"):
            cache_file.unlink()

        if not keep_analytics:
            analytics_file = self.cache_dir / "analytics.json"
            if analytics_file.exists():
                analytics_file.unlink()

            self.analytics = {
                "hits": 0,
                "misses": 0,
                "evictions": 0,
                "total_requests": 0,
                "memory_usage": 0,
                "disk_usage": 0,
            }

        self.logger.info("Cache cleared")

    def get_analytics(self) -> Dict[str, Any]:
        """Get cache performance analytics"""
        # Update current usage stats
        self.analytics["memory_usage"] = len(self.memory_cache)
        self.analytics["disk_usage"] = len(list(self.cache_dir.glob("*.cache")))

        # Calculate hit rate
        total_requests = self.analytics["total_requests"]
        if total_requests > 0:
            hit_rate = self.analytics["hits"] / total_requests
        else:
            hit_rate = 0

        return {
            **self.analytics,
            "hit_rate": hit_rate,
            "cache_efficiency": hit_rate * 100,
        }

    def get_cached_urls(self) -> List[Dict[str, Any]]:
        """Get list of all cached URLs with metadata"""
        cached_urls = []
        current_time = time.time()

        # Check all disk cache files
        for cache_file in self.cache_dir.glob("*.cache"):
            try:
                with open(cache_file, "rb") as f:
                    entry = pickle.load(f)

                if entry["expires_at"] > current_time:
                    cached_urls.append(
                        {
                            "url": entry.get("url", "Unknown"),
                            "created_at": datetime.fromtimestamp(
                                entry.get("created_at", 0)
                            ).isoformat(),
                            "expires_at": datetime.fromtimestamp(
                                entry["expires_at"]
                            ).isoformat(),
                            "size_kb": entry.get("size", 0) / 1024,
                            "in_memory": cache_file.stem in self.memory_cache,
                        }
                    )
            except Exception:
                continue

        return sorted(cached_urls, key=lambda x: x["created_at"], reverse=True)

    def prewarm_cache(self, urls: List[str], fetch_function: callable):
        """Pre-warm cache with multiple URLs"""
        for url in urls:
            if not self.get(url):
                try:
                    data = fetch_function(url)
                    self.set(
                        url, data, ttl=self.default_ttl * 2
                    )  # Longer TTL for prewarmed
                    self.logger.info(f"Prewarmed cache for: {url}")
                except Exception as e:
                    self.logger.error(f"Failed to prewarm cache for {url}: {e}")


# Global cache instance
cache_manager = CacheManager()


@st.cache_data(ttl=300)  # 5 minute Streamlit cache for frequently accessed data
def get_cached_summary(url: str) -> Optional[Dict[str, Any]]:
    """Streamlit-cached wrapper for getting cached summaries"""
    return cache_manager.get(url)


def set_cached_summary(url: str, data: Dict[str, Any], ttl: int = 3600):
    """Set cached summary data"""
    cache_manager.set(url, data, ttl)


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics for dashboard"""
    return cache_manager.get_analytics()


def clear_cache():
    """Clear all cache data"""
    cache_manager.clear()
    # Also clear Streamlit cache
    st.cache_data.clear()


def display_cache_dashboard():
    """Display cache performance dashboard in Streamlit"""
    st.subheader("🚀 Cache Performance")

    stats = get_cache_stats()

    # Main metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Hit Rate",
            f"{stats['cache_efficiency']:.1f}%",
            delta=f"{stats['hits']} hits",
        )

    with col2:
        st.metric(
            "Total Requests", stats["total_requests"], delta=f"{stats['misses']} misses"
        )

    with col3:
        st.metric(
            "Memory Items", stats["memory_usage"], delta=f"{stats['evictions']} evicted"
        )

    with col4:
        st.metric("Disk Files", stats["disk_usage"])

    # Cache efficiency chart
    if stats["total_requests"] > 0:
        chart_data = {
            "Cache Results": ["Hits", "Misses"],
            "Count": [stats["hits"], stats["misses"]],
        }
        st.bar_chart(chart_data, x="Cache Results", y="Count")

    # Cached URLs
    cached_urls = cache_manager.get_cached_urls()
    if cached_urls:
        st.subheader("📄 Cached Articles")

        for item in cached_urls[:10]:  # Show last 10
            with st.expander(
                f"🔗 {item['url'][:60]}..." if len(item["url"]) > 60 else item["url"]
            ):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Created:** {item['created_at']}")
                    st.write(f"**Size:** {item['size_kb']:.1f} KB")
                with col2:
                    st.write(f"**Expires:** {item['expires_at']}")
                    st.write(f"**In Memory:** {'✅' if item['in_memory'] else '❌'}")

    # Cache management
    st.subheader("🛠️ Cache Management")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🗑️ Clear All Cache", type="secondary"):
            clear_cache()
            st.success("Cache cleared successfully!")
            st.rerun()

    with col2:
        if st.button("📊 Refresh Stats", type="secondary"):
            st.rerun()
