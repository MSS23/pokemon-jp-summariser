"""
Enhanced cache management for Pokemon VGC Analysis application with performance optimizations
"""

import json
import os
import gzip
import pickle
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Set
from .config import Config
from .utils import create_content_hash, ensure_cache_directory


class CacheManager:
    """Enhanced caching system with memory cache, compression, and performance optimizations"""

    def __init__(self, ttl_hours: int = None, enable_memory_cache: bool = True, enable_compression: bool = True):
        self.ttl_hours = ttl_hours or Config.CACHE_TTL_HOURS
        self.cache_dir = ensure_cache_directory()
        self.enable_memory_cache = enable_memory_cache
        self.enable_compression = enable_compression
        
        # In-memory cache for frequently accessed items
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        self._memory_cache_timestamps: Dict[str, datetime] = {}
        self._memory_cache_access_count: Dict[str, int] = {}
        
        # Cache metadata for performance optimization
        self._cache_metadata: Dict[str, Dict[str, Any]] = {}
        self._load_cache_metadata()
        
        # Maximum memory cache size (number of items)
        self.max_memory_cache_size = 50
        self.memory_cache_ttl_minutes = 30

    def _load_cache_metadata(self):
        """Load cache metadata for performance optimization"""
        metadata_file = os.path.join(self.cache_dir, "_cache_metadata.json")
        try:
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    self._cache_metadata = json.load(f)
        except Exception:
            self._cache_metadata = {}
    
    def _save_cache_metadata(self):
        """Save cache metadata"""
        metadata_file = os.path.join(self.cache_dir, "_cache_metadata.json")
        try:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self._cache_metadata, f, indent=2)
        except Exception:
            pass
    
    def _get_cache_file_path(self, content_hash: str) -> str:
        """Get cache file path for given hash"""
        extension = ".pkl.gz" if self.enable_compression else ".json"
        return os.path.join(self.cache_dir, f"{content_hash}{extension}")

    def _is_cache_valid(self, cache_file: str) -> bool:
        """Enhanced cache validity check with metadata optimization"""
        if not os.path.exists(cache_file):
            return False

        try:
            # Use metadata for faster validation when available
            file_basename = os.path.basename(cache_file)
            content_hash = file_basename.split('.')[0]
            
            if content_hash in self._cache_metadata:
                metadata = self._cache_metadata[content_hash]
                expiry_timestamp = metadata.get('expiry_timestamp')
                if expiry_timestamp:
                    return datetime.now().timestamp() < expiry_timestamp
            
            # Fallback to file modification time
            mod_time = os.path.getmtime(cache_file)
            cache_time = datetime.fromtimestamp(mod_time)
            expiry_time = cache_time + timedelta(hours=self.ttl_hours)
            return datetime.now() < expiry_time
        except Exception:
            return False
    
    def _is_memory_cache_valid(self, content_hash: str) -> bool:
        """Check if memory cache entry is still valid"""
        if content_hash not in self._memory_cache_timestamps:
            return False
            
        timestamp = self._memory_cache_timestamps[content_hash]
        expiry_time = timestamp + timedelta(minutes=self.memory_cache_ttl_minutes)
        return datetime.now() < expiry_time
    
    def _cleanup_memory_cache(self):
        """Clean up expired and least used memory cache entries"""
        now = datetime.now()
        
        # Remove expired entries
        expired_keys = []
        for content_hash, timestamp in self._memory_cache_timestamps.items():
            expiry_time = timestamp + timedelta(minutes=self.memory_cache_ttl_minutes)
            if now >= expiry_time:
                expired_keys.append(content_hash)
        
        for key in expired_keys:
            self._remove_from_memory_cache(key)
        
        # Remove least used entries if over limit
        if len(self._memory_cache) > self.max_memory_cache_size:
            # Sort by access count (ascending) to remove least used
            sorted_items = sorted(
                self._memory_cache_access_count.items(),
                key=lambda x: x[1]
            )
            
            num_to_remove = len(self._memory_cache) - self.max_memory_cache_size
            for content_hash, _ in sorted_items[:num_to_remove]:
                self._remove_from_memory_cache(content_hash)
    
    def _remove_from_memory_cache(self, content_hash: str):
        """Remove entry from all memory cache structures"""
        self._memory_cache.pop(content_hash, None)
        self._memory_cache_timestamps.pop(content_hash, None)
        self._memory_cache_access_count.pop(content_hash, None)
    
    def _add_to_memory_cache(self, content_hash: str, result: Dict[str, Any]):
        """Add entry to memory cache with cleanup if necessary"""
        if not self.enable_memory_cache:
            return
            
        self._cleanup_memory_cache()
        
        self._memory_cache[content_hash] = result
        self._memory_cache_timestamps[content_hash] = datetime.now()
        self._memory_cache_access_count[content_hash] = 1

    def get(self, content: str, url: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Enhanced cache retrieval with memory cache and compression support

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
            
            # Check memory cache first (fastest)
            if self.enable_memory_cache and content_hash in self._memory_cache:
                if self._is_memory_cache_valid(content_hash):
                    # Update access count for LRU
                    self._memory_cache_access_count[content_hash] += 1
                    return self._memory_cache[content_hash].copy()
                else:
                    # Remove expired memory cache entry
                    self._remove_from_memory_cache(content_hash)
            
            # Check disk cache
            cache_file = self._get_cache_file_path(content_hash)
            if not self._is_cache_valid(cache_file):
                return None
            
            # Load from disk with compression support
            cached_data = self._load_from_disk(cache_file, content_hash)
            if not cached_data:
                return None
                
            # Verify the cached data structure
            if all(key in cached_data for key in ["result", "timestamp", "content_hash"]):
                result = cached_data["result"]
                
                # Add to memory cache for faster future access
                self._add_to_memory_cache(content_hash, result)
                
                return result

        except Exception as e:
            # Silent error handling - don't interrupt user experience
            pass

        return None
    
    def _load_from_disk(self, cache_file: str, content_hash: str) -> Optional[Dict[str, Any]]:
        """Load cache data from disk with compression support"""
        try:
            if self.enable_compression and cache_file.endswith('.pkl.gz'):
                # Load compressed pickle
                with gzip.open(cache_file, 'rb') as f:
                    return pickle.load(f)
            else:
                # Load JSON
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            # Clean up corrupted cache file
            try:
                os.remove(cache_file)
                if content_hash in self._cache_metadata:
                    del self._cache_metadata[content_hash]
            except:
                pass
            return None

    def set(
        self, content: str, result: Dict[str, Any], url: Optional[str] = None
    ) -> bool:
        """
        Enhanced cache storage with memory cache and compression support

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
            current_time = datetime.now()

            cache_data = {
                "result": result,
                "timestamp": current_time.isoformat(),
                "content_hash": content_hash,
                "url": url,
                "ttl_hours": self.ttl_hours,
                "cached_at": current_time.timestamp(),
                "format_version": "2.0"
            }

            # Save to disk with compression if enabled
            success = self._save_to_disk(cache_file, cache_data, content_hash)
            
            if success:
                # Add to memory cache for immediate access
                self._add_to_memory_cache(content_hash, result)
                
                # Update metadata for faster validation
                expiry_timestamp = current_time.timestamp() + (self.ttl_hours * 3600)
                self._cache_metadata[content_hash] = {
                    'expiry_timestamp': expiry_timestamp,
                    'file_path': cache_file,
                    'created_at': current_time.isoformat(),
                    'url': url,
                    'compressed': self.enable_compression
                }
                
                # Save metadata (async in production, sync here for simplicity)
                self._save_cache_metadata()
                
            return success

        except Exception as e:
            # Silent error handling
            return False
    
    def _save_to_disk(self, cache_file: str, cache_data: Dict[str, Any], content_hash: str) -> bool:
        """Save cache data to disk with compression support"""
        try:
            if self.enable_compression:
                # Save as compressed pickle for better performance
                with gzip.open(cache_file, 'wb') as f:
                    pickle.dump(cache_data, f, protocol=pickle.HIGHEST_PROTOCOL)
            else:
                # Save as JSON for compatibility
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(cache_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    def clear_expired(self) -> int:
        """
        Enhanced expired cache cleanup with memory cache support

        Returns:
            Number of files cleared
        """
        cleared_count = 0

        try:
            # Clean memory cache first
            self._cleanup_memory_cache()
            
            # Clean disk cache
            cache_extensions = [".json", ".pkl.gz"] if self.enable_compression else [".json"]
            
            for filename in os.listdir(self.cache_dir):
                if any(filename.endswith(ext) for ext in cache_extensions) and not filename.startswith('_'):
                    file_path = os.path.join(self.cache_dir, filename)
                    if not self._is_cache_valid(file_path):
                        os.remove(file_path)
                        cleared_count += 1
                        
                        # Remove from metadata
                        content_hash = filename.split('.')[0]
                        if content_hash in self._cache_metadata:
                            del self._cache_metadata[content_hash]
            
            # Save updated metadata
            if cleared_count > 0:
                self._save_cache_metadata()
                
        except Exception:
            pass

        return cleared_count

    def clear_all(self) -> bool:
        """
        Enhanced cache clearing with memory cache support

        Returns:
            True if successful
        """
        try:
            # Clear memory cache
            self._memory_cache.clear()
            self._memory_cache_timestamps.clear()
            self._memory_cache_access_count.clear()
            
            # Clear disk cache
            cache_extensions = [".json", ".pkl.gz"] if self.enable_compression else [".json"]
            
            for filename in os.listdir(self.cache_dir):
                if any(filename.endswith(ext) for ext in cache_extensions) and not filename.startswith('_'):
                    file_path = os.path.join(self.cache_dir, filename)
                    os.remove(file_path)
            
            # Clear metadata
            self._cache_metadata.clear()
            self._save_cache_metadata()
            
            return True
        except Exception:
            return False

    def get_stats(self) -> Dict[str, Any]:
        """
        Enhanced cache statistics with memory cache info

        Returns:
            Dictionary with comprehensive cache stats
        """
        stats = {
            "total_files": 0,
            "valid_files": 0,
            "expired_files": 0,
            "total_size_mb": 0,
            "compressed_files": 0,
            "memory_cache_entries": len(self._memory_cache),
            "memory_cache_hit_rate": 0,
            "compression_enabled": self.enable_compression,
            "memory_cache_enabled": self.enable_memory_cache,
        }

        try:
            cache_extensions = [".json", ".pkl.gz"] if self.enable_compression else [".json"]
            
            for filename in os.listdir(self.cache_dir):
                if any(filename.endswith(ext) for ext in cache_extensions) and not filename.startswith('_'):
                    file_path = os.path.join(self.cache_dir, filename)
                    stats["total_files"] += 1
                    
                    if filename.endswith('.pkl.gz'):
                        stats["compressed_files"] += 1

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
            
            # Calculate memory cache hit rate
            if self._memory_cache_access_count:
                total_accesses = sum(self._memory_cache_access_count.values())
                memory_hits = len([count for count in self._memory_cache_access_count.values() if count > 1])
                if total_accesses > 0:
                    stats["memory_cache_hit_rate"] = round((memory_hits / total_accesses) * 100, 1)

        except Exception:
            pass

        return stats
    
    def preload_frequent_items(self, limit: int = 20):
        """
        Preload frequently accessed items into memory cache
        
        Args:
            limit: Maximum number of items to preload
        """
        if not self.enable_memory_cache:
            return
            
        try:
            # Sort cache files by access time (most recent first)
            cache_files = []
            for filename in os.listdir(self.cache_dir):
                if (filename.endswith('.json') or filename.endswith('.pkl.gz')) and not filename.startswith('_'):
                    file_path = os.path.join(self.cache_dir, filename)
                    if self._is_cache_valid(file_path):
                        mod_time = os.path.getmtime(file_path)
                        cache_files.append((file_path, mod_time, filename))
            
            # Sort by modification time (newest first)
            cache_files.sort(key=lambda x: x[1], reverse=True)
            
            # Load top items into memory cache
            loaded_count = 0
            for file_path, _, filename in cache_files[:limit]:
                if loaded_count >= limit:
                    break
                    
                content_hash = filename.split('.')[0]
                if content_hash not in self._memory_cache:
                    try:
                        cached_data = self._load_from_disk(file_path, content_hash)
                        if cached_data and "result" in cached_data:
                            self._add_to_memory_cache(content_hash, cached_data["result"])
                            loaded_count += 1
                    except:
                        continue
                        
        except Exception:
            pass


# Global cache instance
cache = CacheManager()
