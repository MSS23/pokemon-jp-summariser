"""
Compliance checking system for URL validation
Ensures respect for robots.txt, domain allowlisting, and content policies
"""

import os
import re
import urllib.robotparser
from urllib.parse import urlparse
from typing import List, Set, Optional
import logging
import time
from pathlib import Path
import yaml

class ComplianceChecker:
    """
    Handles compliance checks for URL processing
    - Domain allowlist validation
    - robots.txt compliance checking
    - Paywall/login detection heuristics
    - Content type validation
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize compliance checker

        Args:
            config_path: Path to YAML config file for domain allowlist
        """
        self.logger = logging.getLogger(__name__)

        # Load domain allowlist from config or environment
        self.allowed_domains = self._load_domain_allowlist(config_path)
        self.robots_cache = {}  # Cache robots.txt parsers
        self.cache_expiry = 3600  # 1 hour cache for robots.txt

        self.logger.info(f"ComplianceChecker initialized with {len(self.allowed_domains)} allowed domains")

    def _load_domain_allowlist(self, config_path: Optional[str]) -> Set[str]:
        """
        Load domain allowlist from config file or environment variable

        Args:
            config_path: Path to YAML config file

        Returns:
            Set of allowed domains
        """
        # Default Pokemon community domains
        default_domains = {
            # Official Pokemon sites
            "pokemon.com",
            "pokemon-gl.com",

            # Major VGC community sites
            "smogon.com",
            "www.smogon.com",
            "bulbagarden.net",
            "www.bulbagarden.net",
            "pkmn.news",
            "www.pkmn.news",

            # Japanese Pokemon sites
            "note.com",
            "www.note.com",
            "liberty-note.com",
            "www.liberty-note.com",

            # Blog platforms commonly used for Pokemon content
            "hatenablog.com",
            "hatenablog.jp",
            "hateblo.jp",
            "yunu.hatenablog.jp",
            "cona5757.hatenablog.com",
            "tamii-poke.hateblo.jp",

            # Asset domains for note.com and similar
            "assets.st-note.com",

            # VGC tournament and community sites
            "victoryroadvgc.com",
            "www.victoryroadvgc.com",
            "trainertower.com",
            "www.trainertower.com",
            "nuggetbridge.com",
            "www.nuggetbridge.com",

            # YouTube (for team showcase videos)
            "youtube.com",
            "www.youtube.com",
            "youtu.be",

            # Twitter/X (for VGC team posts)
            "twitter.com",
            "www.twitter.com",
            "x.com",
            "www.x.com",

            # Reddit Pokemon communities
            "reddit.com",
            "www.reddit.com",
            "old.reddit.com",
        }

        try:
            # Try to load from config file first
            if config_path and Path(config_path).exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    if 'allowed_domains' in config:
                        configured_domains = set(config['allowed_domains'])
                        self.logger.info(f"Loaded {len(configured_domains)} domains from config file")
                        return configured_domains

            # Try environment variable
            env_domains = os.getenv('ALLOWED_DOMAINS')
            if env_domains:
                configured_domains = set(domain.strip() for domain in env_domains.split(','))
                self.logger.info(f"Loaded {len(configured_domains)} domains from environment")
                return configured_domains

            # Fall back to default
            self.logger.info(f"Using default domain allowlist with {len(default_domains)} domains")
            return default_domains

        except Exception as e:
            self.logger.error(f"Error loading domain config: {e}, using defaults")
            return default_domains

    def extract_domain(self, url: str) -> str:
        """
        Extract domain from URL

        Args:
            url: URL to extract domain from

        Returns:
            Domain string
        """
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except Exception:
            return "unknown"

    def is_domain_allowed(self, url: str) -> bool:
        """
        Check if domain is in the allowlist

        Args:
            url: URL to check

        Returns:
            True if domain is allowed, False otherwise
        """
        try:
            domain = self.extract_domain(url)

            # Direct match
            if domain in self.allowed_domains:
                return True

            # Check if any parent domains are allowed (for subdomains)
            for allowed_domain in self.allowed_domains:
                if domain.endswith(f".{allowed_domain}"):
                    return True

            return False

        except Exception as e:
            self.logger.error(f"Error checking domain allowlist for {url}: {e}")
            return False

    def _get_robots_parser(self, url: str) -> Optional[urllib.robotparser.RobotFileParser]:
        """
        Get robots.txt parser for a domain, with caching

        Args:
            url: URL to get robots parser for

        Returns:
            RobotFileParser instance or None if unavailable
        """
        try:
            domain = self.extract_domain(url)
            current_time = time.time()

            # Check cache
            if domain in self.robots_cache:
                cached_parser, cache_time = self.robots_cache[domain]
                if current_time - cache_time < self.cache_expiry:
                    return cached_parser

            # Create new parser
            robots_url = f"https://{domain}/robots.txt"
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robots_url)

            try:
                rp.read()
                # Cache the parser
                self.robots_cache[domain] = (rp, current_time)
                return rp
            except Exception as e:
                self.logger.debug(f"Could not read robots.txt for {domain}: {e}")
                # Cache negative result to avoid repeated failures
                self.robots_cache[domain] = (None, current_time)
                return None

        except Exception as e:
            self.logger.error(f"Error getting robots parser for {url}: {e}")
            return None

    def robots_allows(self, url: str, user_agent: str = "*") -> bool:
        """
        Check if robots.txt allows crawling this URL

        Args:
            url: URL to check
            user_agent: User agent string to check against

        Returns:
            True if robots.txt allows crawling, False otherwise
        """
        try:
            parser = self._get_robots_parser(url)

            if parser is None:
                # If no robots.txt found, assume allowed
                self.logger.debug(f"No robots.txt found for {url}, assuming allowed")
                return True

            # Check if crawling is allowed
            allowed = parser.can_fetch(user_agent, url)
            self.logger.debug(f"robots.txt check for {url}: {'allowed' if allowed else 'disallowed'}")

            return allowed

        except Exception as e:
            self.logger.error(f"Error checking robots.txt for {url}: {e}")
            # Err on the side of caution - if we can't check, assume disallowed
            return False

    def is_content_type_allowed(self, content_type: str) -> bool:
        """
        Check if content type is allowed for processing

        Args:
            content_type: Content-Type header value

        Returns:
            True if content type is allowed, False otherwise
        """
        if not content_type:
            return False

        # Normalize content type
        content_type_lower = content_type.lower()

        # Only allow HTML content
        allowed_types = [
            "text/html",
            "application/xhtml+xml",
        ]

        for allowed_type in allowed_types:
            if allowed_type in content_type_lower:
                return True

        return False

    def looks_paywalled_or_gated(self, html_head: str) -> bool:
        """
        Use heuristics to detect if content is behind paywall or login gate

        Args:
            html_head: First part of HTML content to analyze

        Returns:
            True if content appears to be gated, False otherwise
        """
        try:
            # Convert to lowercase for case-insensitive matching
            content_lower = html_head.lower()

            # Paywall indicators
            paywall_patterns = [
                # Common paywall text
                r"subscribe\s+to\s+continue\s+reading",
                r"this\s+content\s+is\s+for\s+subscribers",
                r"please\s+log\s+in\s+to\s+continue",
                r"create\s+a\s+free\s+account\s+to\s+continue",
                r"premium\s+content",
                r"members\s+only",

                # Subscription prompts
                r"subscription\s+required",
                r"become\s+a\s+member\s+to\s+read",
                r"join\s+now\s+to\s+access",
                r"upgrade\s+to\s+premium",

                # Login walls
                r"sign\s+in\s+to\s+view",
                r"register\s+to\s+continue",
                r"login\s+required",
                r"account\s+required",

                # CAPTCHA indicators
                r"prove\s+you\s+are\s+human",
                r"captcha\s+verification",
                r"security\s+check\s+required",

                # Japanese paywall patterns
                r"有料会員",  # Premium member
                r"ログインが必要",  # Login required
                r"会員登録",  # Member registration
                r"続きを読む",  # Continue reading (often behind paywall)
            ]

            for pattern in paywall_patterns:
                if re.search(pattern, content_lower):
                    return True

            # Check for common paywall class names and IDs
            paywall_selectors = [
                "paywall",
                "subscription-wall",
                "login-wall",
                "registration-required",
                "premium-content",
                "members-only",
                "subscriber-only",
            ]

            for selector in paywall_selectors:
                if selector in content_lower:
                    return True

            # Check for blocked content indicators
            blocked_indicators = [
                "access denied",
                "unauthorized",
                "forbidden",
                "content not available",
                "region blocked",
                "geo-restricted",
            ]

            for indicator in blocked_indicators:
                if indicator in content_lower:
                    return True

            return False

        except Exception as e:
            self.logger.error(f"Error in paywall detection: {e}")
            # Err on the side of caution
            return True

    def get_domain_allowlist(self) -> List[str]:
        """
        Get the current domain allowlist

        Returns:
            List of allowed domains
        """
        return sorted(list(self.allowed_domains))

    def add_allowed_domain(self, domain: str) -> bool:
        """
        Add a domain to the allowlist (runtime addition)

        Args:
            domain: Domain to add

        Returns:
            True if added successfully, False if already exists
        """
        domain_lower = domain.lower()
        if domain_lower not in self.allowed_domains:
            self.allowed_domains.add(domain_lower)
            self.logger.info(f"Added domain to allowlist: {domain_lower}")
            return True
        return False

    def remove_allowed_domain(self, domain: str) -> bool:
        """
        Remove a domain from the allowlist (runtime removal)

        Args:
            domain: Domain to remove

        Returns:
            True if removed successfully, False if not found
        """
        domain_lower = domain.lower()
        if domain_lower in self.allowed_domains:
            self.allowed_domains.remove(domain_lower)
            self.logger.info(f"Removed domain from allowlist: {domain_lower}")
            return True
        return False

    def clear_robots_cache(self) -> None:
        """Clear the robots.txt cache"""
        self.robots_cache.clear()
        self.logger.info("Cleared robots.txt cache")

    def get_compliance_summary(self) -> dict:
        """
        Get a summary of compliance configuration

        Returns:
            Dictionary with compliance settings
        """
        return {
            "allowed_domains_count": len(self.allowed_domains),
            "robots_cache_entries": len(self.robots_cache),
            "cache_expiry_seconds": self.cache_expiry,
            "sample_domains": sorted(list(self.allowed_domains))[:10]  # First 10 for reference
        }