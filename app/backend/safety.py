"""
Content safety and moderation system
Implements pre-moderation for scope validation and prohibited content filtering
"""

import re
import logging
from typing import List, Tuple, Set
import hashlib

# Import shared models
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from shared.models import SafetyDecision, RedactionStats

class SafetyFilter:
    """
    Content safety filter that enforces scope limitations and blocks prohibited content
    Ensures only Pokemon VGC content is processed and removes PII
    """

    def __init__(self):
        """Initialize the safety filter with keyword lists and patterns"""
        self.logger = logging.getLogger(__name__)

        # Pokemon/VGC scope keywords (must have some of these)
        self.scope_keywords = self._get_scope_keywords()

        # Prohibited content categories
        self.blocked_keywords = self._get_blocked_keywords()

        # PII patterns for redaction
        self.pii_patterns = self._get_pii_patterns()

        # Maximum content length to process (500KB)
        self.max_content_length = 500000

        self.logger.info("SafetyFilter initialized")

    def _get_scope_keywords(self) -> Set[str]:
        """
        Get keywords that indicate Pokemon VGC content
        Content must contain some of these to be considered in scope
        """
        return {
            # Pokemon names (common competitive ones)
            "ポケモン", "pokemon", "ポケットモンスター",
            "ガブリアス", "garchomp", "ガオガエン", "incineroar",
            "ランドロス", "landorus", "カイリュー", "dragonite",
            "ミライドン", "miraidon", "コライドン", "koraidon",
            "パオジアン", "chien-pao", "イーユイ", "wo-chien",

            # VGC/competitive terms
            "vgc", "video game championships", "ビデオゲームチャンピオンシップ",
            "ダブルバトル", "double battle", "doubles",
            "公式大会", "official tournament", "世界大会", "worlds",
            "レギュレーション", "regulation", "series",
            "構築", "team", "チーム", "パーティ", "party",

            # Game mechanics
            "努力値", "ev", "individual values", "個体値", "iv",
            "とくせい", "ability", "わざ", "move", "アイテム", "item",
            "せいかく", "nature", "テラスタル", "terastal", "tera",
            "ダイマックス", "dynamax", "メガシンカ", "mega evolution",

            # Battle terms
            "対戦", "battle", "バトル", "勝率", "win rate",
            "選出", "team selection", "立ち回り", "strategy",
            "相性", "matchup", "メタ", "meta", "環境", "environment",

            # Tournament terms
            "予選", "qualifier", "本戦", "main event",
            "決勝", "finals", "準決勝", "semifinals",
            "上位", "top cut", "結果", "results"
        }

    def _get_blocked_keywords(self) -> Set[str]:
        """
        Get keywords that indicate prohibited content categories
        Content containing these will be blocked
        """
        return {
            # Harassment keywords
            "harassment", "bullying", "cyberbullying", "stalking", "doxxing",
            "いじめ", "嫌がらせ", "ストーカー", "晒し",

            # Sexual content
            "nsfw", "adult content", "sexual", "explicit", "pornography",
            "porn", "sex", "nude", "naked", "erotic", "18+",
            "成人向け", "アダルト", "エッチ", "セックス", "ヌード",

            # Violence/harmful content
            "self-harm", "suicide", "cutting", "violence", "murder",
            "kill yourself", "kys", "die", "death threat",
            "自殺", "自傷", "暴力", "殺害", "殺す", "死ね",

            # Medical/financial advice
            "medical advice", "financial advice", "investment advice",
            "legal advice", "tax advice", "prescription", "diagnosis",
            "医療アドバイス", "金融アドバイス", "投資アドバイス", "処方箋",

            # Political/election content
            "election", "voting", "candidate", "political campaign",
            "vote for", "political persuasion", "propaganda",
            "選挙", "投票", "候補者", "政治キャンペーン", "政治的説得",

            # Malware/hacking
            "malware", "virus", "hack", "exploit", "trojan",
            "phishing", "scam", "fraud", "cheat", "bot",
            "マルウェア", "ウイルス", "ハック", "詐欺", "チート",

            # Hate speech
            "hate speech", "racism", "homophobia", "transphobia",
            "discrimination", "slur", "offensive language",
            "ヘイトスピーチ", "差別", "中傷",

            # Spam indicators
            "click here", "buy now", "limited time offer",
            "make money fast", "work from home", "casino",
            "ここをクリック", "今すぐ購入", "お金を稼ぐ", "カジノ"
        }

    def _get_pii_patterns(self) -> List[Tuple[str, str]]:
        """
        Get regex patterns for PII detection and redaction
        Returns list of (pattern, replacement) tuples
        """
        return [
            # Email addresses
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]'),

            # Phone numbers (various formats)
            (r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b', '[PHONE_REDACTED]'),
            (r'\b0\d{1,4}[-\s]?\d{1,4}[-\s]?\d{4}\b', '[PHONE_REDACTED]'),  # Japanese phones

            # URLs with personal info (keep domain but redact paths)
            (r'https?://[^\s/$.?#].[^\s]*\/users?\/[^\s]*', '[URL_WITH_USER_INFO_REDACTED]'),

            # IP addresses
            (r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', '[IP_ADDRESS_REDACTED]'),

            # Social security-like numbers
            (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN_LIKE_NUMBER_REDACTED]'),

            # Credit card-like numbers (4 groups of 4 digits)
            (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD_LIKE_NUMBER_REDACTED]'),

            # Addresses (simple patterns)
            (r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln)\b', '[ADDRESS_REDACTED]'),

            # Japanese addresses (prefecture + city patterns)
            (r'[都道府県市区町村]\s*[^\s\n]{2,}', '[ADDRESS_REDACTED]'),

            # Personal names in context (Mr./Ms./Dr. + Name)
            (r'\b(?:Mr|Ms|Mrs|Dr|Professor)\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b', '[NAME_REDACTED]'),
        ]

    def precheck_text_for_scope(self, text: str) -> SafetyDecision:
        """
        Check if text content is within allowed scope (Pokemon VGC)
        and doesn't contain prohibited content

        Args:
            text: Text content to check

        Returns:
            SafetyDecision with allow/block decision and reason
        """
        if not text or len(text.strip()) == 0:
            return SafetyDecision(
                allowed=False,
                reason="Empty content",
                blocked_categories=["empty_content"],
                confidence=1.0
            )

        # Check content length
        if len(text) > self.max_content_length:
            return SafetyDecision(
                allowed=False,
                reason=f"Content too long ({len(text)} chars, max {self.max_content_length})",
                blocked_categories=["content_too_long"],
                confidence=1.0
            )

        text_lower = text.lower()
        blocked_categories = []

        # Check for prohibited content
        for blocked_keyword in self.blocked_keywords:
            if blocked_keyword in text_lower:
                blocked_categories.append(f"prohibited_keyword_{blocked_keyword.replace(' ', '_')}")

        if blocked_categories:
            return SafetyDecision(
                allowed=False,
                reason=f"Content contains prohibited keywords: {', '.join(blocked_categories[:3])}",
                blocked_categories=blocked_categories,
                confidence=0.9
            )

        # Check for Pokemon/VGC scope
        scope_matches = 0
        for scope_keyword in self.scope_keywords:
            if scope_keyword in text_lower:
                scope_matches += 1

        # Require at least 2 scope keyword matches for stronger confidence
        if scope_matches < 2:
            return SafetyDecision(
                allowed=False,
                reason="Content does not appear to be Pokemon VGC related (insufficient scope keywords)",
                blocked_categories=["out_of_scope"],
                confidence=0.8 if scope_matches == 1 else 0.95
            )

        # Additional heuristics for non-Pokemon content
        non_pokemon_indicators = {
            "recipe", "cooking", "food", "restaurant",
            "news", "politics", "sports", "football", "soccer",
            "movie", "music", "celebrity", "entertainment",
            "shopping", "sale", "discount", "price",
            "travel", "vacation", "hotel", "flight"
        }

        non_pokemon_matches = sum(1 for indicator in non_pokemon_indicators if indicator in text_lower)
        if non_pokemon_matches > scope_matches:
            return SafetyDecision(
                allowed=False,
                reason="Content appears to be unrelated to Pokemon (more non-Pokemon indicators than Pokemon keywords)",
                blocked_categories=["likely_off_topic"],
                confidence=0.7
            )

        # Content passed all checks
        return SafetyDecision(
            allowed=True,
            reason=f"Content appears to be Pokemon VGC related ({scope_matches} scope matches)",
            blocked_categories=[],
            confidence=min(0.95, 0.6 + (scope_matches * 0.1))
        )

    def redact_pii(self, text: str) -> Tuple[str, RedactionStats]:
        """
        Remove personally identifiable information from text

        Args:
            text: Text to redact PII from

        Returns:
            Tuple of (redacted_text, redaction_statistics)
        """
        if not text:
            return text, RedactionStats()

        redacted_text = text
        stats = RedactionStats()

        try:
            # Apply PII redaction patterns
            for pattern, replacement in self.pii_patterns:
                matches = re.findall(pattern, redacted_text, re.IGNORECASE)
                if matches:
                    redacted_text = re.sub(pattern, replacement, redacted_text, flags=re.IGNORECASE)

                    # Update statistics based on replacement type
                    if 'EMAIL' in replacement:
                        stats.emails_redacted += len(matches)
                    elif 'PHONE' in replacement:
                        stats.phone_numbers_redacted += len(matches)
                    elif 'ADDRESS' in replacement:
                        stats.addresses_redacted += len(matches)
                    else:
                        stats.other_pii_redacted += len(matches)

            # Calculate total redactions
            stats.total_redactions = (
                stats.emails_redacted +
                stats.phone_numbers_redacted +
                stats.addresses_redacted +
                stats.other_pii_redacted
            )

            if stats.total_redactions > 0:
                self.logger.info(f"Redacted {stats.total_redactions} PII items from content")

            return redacted_text, stats

        except Exception as e:
            self.logger.error(f"Error during PII redaction: {e}")
            # Return original text if redaction fails
            return text, RedactionStats()

    def get_content_hash(self, text: str) -> str:
        """
        Generate a hash of content for tracking (without storing actual content)

        Args:
            text: Content to hash

        Returns:
            SHA-256 hash (first 16 chars)
        """
        return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]

    def analyze_content_safety(self, text: str) -> dict:
        """
        Comprehensive content safety analysis

        Args:
            text: Text to analyze

        Returns:
            Dictionary with detailed safety analysis
        """
        safety_decision = self.precheck_text_for_scope(text)
        _, redaction_stats = self.redact_pii(text)

        return {
            "content_hash": self.get_content_hash(text),
            "content_length": len(text),
            "safety_decision": safety_decision.dict(),
            "pii_found": redaction_stats.total_redactions > 0,
            "redaction_stats": redaction_stats.dict(),
            "scope_analysis": {
                "pokemon_indicators": sum(1 for kw in self.scope_keywords if kw in text.lower()),
                "prohibited_indicators": sum(1 for kw in self.blocked_keywords if kw in text.lower())
            }
        }

    def update_keyword_lists(self, scope_keywords: List[str] = None, blocked_keywords: List[str] = None):
        """
        Update keyword lists (for runtime configuration)

        Args:
            scope_keywords: New scope keywords to add
            blocked_keywords: New blocked keywords to add
        """
        if scope_keywords:
            self.scope_keywords.update(kw.lower() for kw in scope_keywords)
            self.logger.info(f"Added {len(scope_keywords)} scope keywords")

        if blocked_keywords:
            self.blocked_keywords.update(kw.lower() for kw in blocked_keywords)
            self.logger.info(f"Added {len(blocked_keywords)} blocked keywords")

    def get_filter_stats(self) -> dict:
        """
        Get statistics about the safety filter configuration

        Returns:
            Dictionary with filter statistics
        """
        return {
            "scope_keywords_count": len(self.scope_keywords),
            "blocked_keywords_count": len(self.blocked_keywords),
            "pii_patterns_count": len(self.pii_patterns),
            "max_content_length": self.max_content_length
        }