"""
Cache management for Pokemon VGC Analysis application
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from config import Config
from utils import create_content_hash, ensure_cache_directory


class CacheManager:
    """Handles caching of analysis results and web content"""

    def __init__(self, ttl_hours: int = None):
        self.ttl_hours = ttl_hours or Config.CACHE_TTL_HOURS
        self.cache_dir = ensure_cache_directory()

    def _get_cache_file_path(self, content_hash: str) -> str:
        """Get cache file path for given hash"""
        return os.path.join(self.cache_dir, f"{content_hash}.json")

    def _is_cache_valid(self, cache_file: str) -> bool:
        """Check if cache file is still valid based on TTL"""
        if not os.path.exists(cache_file):
            return False

        try:
            mod_time = os.path.getmtime(cache_file)
            cache_time = datetime.fromtimestamp(mod_time)
            expiry_time = cache_time + timedelta(hours=self.ttl_hours)
            return datetime.now() < expiry_time
        except Exception:
            return False

    def get(self, content: str, url: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get cached result for content

        Args:
            content: Content to check cache for
            url: Optional URL for additional context

        Returns:
            Cached result if available and valid, None otherwise
        """
        if not Config.CACHE_ENABLED:
            return None

        try:
            content_hash = create_content_hash(content)
            cache_file = self._get_cache_file_path(content_hash)

            if not self._is_cache_valid(cache_file):
                return None

            with open(cache_file, "r", encoding="utf-8") as f:
                cached_data = json.load(f)

            # Verify the cached data structure
            if all(
                key in cached_data for key in ["result", "timestamp", "content_hash"]
            ):
                return cached_data["result"]

        except Exception as e:
            print(f"Cache read error: {e}")

        return None

    def set(
        self, content: str, result: Dict[str, Any], url: Optional[str] = None
    ) -> bool:
        """
        Save result to cache

        Args:
            content: Content that was analyzed
            result: Analysis result to cache
            url: Optional URL for additional context

        Returns:
            True if successfully cached
        """
        if not Config.CACHE_ENABLED:
            return False

        try:
            content_hash = create_content_hash(content)
            cache_file = self._get_cache_file_path(content_hash)

            cache_data = {
                "result": result,
                "timestamp": datetime.now().isoformat(),
                "content_hash": content_hash,
                "url": url,
                "ttl_hours": self.ttl_hours,
            }

            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"Cache write error: {e}")
            return False

    def clear_expired(self) -> int:
        """
        Clear expired cache files

        Returns:
            Number of files cleared
        """
        cleared_count = 0

        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(self.cache_dir, filename)
                    if not self._is_cache_valid(file_path):
                        os.remove(file_path)
                        cleared_count += 1
        except Exception as e:
            print(f"Cache cleanup error: {e}")

        return cleared_count

    def clear_all(self) -> bool:
        """
        Clear all cache files

        Returns:
            True if successful
        """
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(self.cache_dir, filename)
                    os.remove(file_path)
            return True
        except Exception as e:
            print(f"Cache clear error: {e}")
            return False

    def get_stats(self) -> Dict[str, int]:
        """
        Get cache statistics

        Returns:
            Dictionary with cache stats
        """
        stats = {
            "total_files": 0,
            "valid_files": 0,
            "expired_files": 0,
            "total_size_mb": 0,
        }

        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(self.cache_dir, filename)
                    stats["total_files"] += 1

                    # Check file size
                    file_size = os.path.getsize(file_path)
                    stats["total_size_mb"] += file_size

                    # Check if valid
                    if self._is_cache_valid(file_path):
                        stats["valid_files"] += 1
                    else:
                        stats["expired_files"] += 1

            # Convert bytes to MB
            stats["total_size_mb"] = round(stats["total_size_mb"] / (1024 * 1024), 2)

        except Exception as e:
            print(f"Cache stats error: {e}")

        return stats


# Global cache instance
cache = CacheManager()
