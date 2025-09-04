"""
Article scraper for VGC content with robust multi-strategy approach.
"""

import re
import requests
from bs4 import BeautifulSoup
from typing import Optional
import time
import logging

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArticleScraper:
    """Enhanced article content scraper with robust dynamic content handling"""

    def __init__(self):
        """Initialize the scraper"""
        pass

    def validate_url(self, url: str) -> bool:
        """
        Validate if URL is accessible and potentially contains VGC content

        Args:
            url: URL to validate

        Returns:
            True if URL appears accessible, False otherwise
        """
        try:
            response = requests.head(url, timeout=10)
            return response.status_code == 200
        except Exception:
            return False

    def scrape_article(self, url: str) -> Optional[str]:
        """
        Enhanced article content scraper with robust dynamic content handling

        Args:
            url: URL to scrape

        Returns:
            Article content as string or None if failed
        """
        if not self.validate_url(url):
            raise ValueError("Invalid or inaccessible URL")

        # Try multiple scraping strategies with increasing aggressiveness
        strategies = [
            self._scrape_with_standard_headers,
            self._scrape_with_mobile_headers,
            self._scrape_with_japanese_headers,
            self._scrape_with_session_retry
        ]
        
        for strategy_func in strategies:
            try:
                logger.info(f"Trying scraping strategy: {strategy_func.__name__}")
                content = strategy_func(url)
                if content and len(content.strip()) > 50:  # Lower minimum for better fallback
                    logger.info(f"Success with {strategy_func.__name__}: extracted {len(content)} characters")
                    logger.debug(f"Content preview: {content[:200]}...")
                    return content
                else:
                    logger.warning(f"Strategy {strategy_func.__name__} returned insufficient content: {len(content) if content else 0} chars")
            except Exception as e:
                # Log the error but continue to next strategy
                logger.error(f"Scraping strategy failed: {strategy_func.__name__}: {str(e)}")
                continue
        
        raise ValueError("All scraping strategies failed to extract meaningful content")

    def _scrape_with_standard_headers(self, url: str) -> Optional[str]:
        """Standard scraping approach with comprehensive headers"""
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }

        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        return self._process_response_content(response)
    
    def _scrape_with_mobile_headers(self, url: str) -> Optional[str]:
        """Mobile user agent approach for sites that serve different content to mobile"""
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                "Version/16.0 Mobile/15E148 Safari/604.1"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        return self._process_response_content(response)
    
    def _scrape_with_japanese_headers(self, url: str) -> Optional[str]:
        """Japanese-specific headers for better compatibility with Japanese sites"""
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ja-JP,ja;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Charset": "utf-8",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Referer": "https://www.google.com/"
        }

        response = requests.get(url, headers=headers, timeout=25)
        response.raise_for_status()
        return self._process_response_content(response)
    
    def _scrape_with_session_retry(self, url: str) -> Optional[str]:
        """Session-based approach with retry logic for stubborn sites"""
        session = requests.Session()
        
        # First request to establish session
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ja-JP,ja;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        
        try:
            # Sometimes note.com requires a session establishment
            session.get(url, headers=headers, timeout=15)
            
            # Second request for actual content
            time.sleep(2)  # Brief delay for dynamic content
            
            response = session.get(url, headers=headers, timeout=25)
            response.raise_for_status()
            return self._process_response_content(response)
        finally:
            session.close()
    
    def _process_response_content(self, response) -> Optional[str]:
        """Enhanced content processing from HTTP response with note.com specialization"""
        try:
            
            # Enhanced encoding detection and handling with special Hatenablog support
            if response.encoding is None or response.encoding.lower() in ['iso-8859-1', 'ascii']:
                # Force UTF-8 for Japanese content
                response.encoding = 'utf-8'
            
            # Enhanced Japanese text handling - especially critical for Hatenablog
            try:
                # First attempt: Direct UTF-8 decoding
                html_content = response.content.decode('utf-8', errors='ignore')
            except UnicodeDecodeError:
                try:
                    # Second attempt: Try with different encodings common in Japanese sites
                    html_content = response.content.decode('shift_jis', errors='ignore')
                except UnicodeDecodeError:
                    try:
                        # Third attempt: EUC-JP encoding
                        html_content = response.content.decode('euc-jp', errors='ignore')
                    except UnicodeDecodeError:
                        # Final fallback to response.text with encoding set
                        html_content = response.text
            
            # Additional encoding fix for Hatenablog domains
            if any(domain in response.url for domain in ["hatenablog.com", "hatenablog.jp", "hatenadiary.jp"]):
                # Ensure proper Unicode normalization for Japanese content
                import unicodedata
                html_content = unicodedata.normalize('NFKC', html_content)

            soup = BeautifulSoup(html_content, "html.parser")
            
            # Special handling for note.com articles (critical improvement)
            if "note.com" in response.url:
                logger.info("Detected note.com URL, using specialized extraction")
                note_content = self._extract_note_com_content_specialized(soup)
                if note_content:
                    logger.info(f"Note.com specialized extraction successful: {len(note_content)} characters")
                    logger.debug(f"Note.com content preview: {note_content[:300]}...")
                    return note_content
                else:
                    logger.warning("Note.com specialized extraction failed, falling back to generic extraction")

            # Special handling for Hatenablog articles (NEW - addresses missing Hatenablog support)
            if any(domain in response.url for domain in ["hatenablog.com", "hatenablog.jp", "hatenadiary.jp"]):
                logger.info("Detected Hatenablog URL, using specialized extraction")
                hatenablog_content = self._extract_hatenablog_content_specialized(soup)
                if hatenablog_content:
                    logger.info(f"Hatenablog specialized extraction successful: {len(hatenablog_content)} characters")
                    logger.debug(f"Hatenablog content preview: {hatenablog_content[:300]}...")
                    return hatenablog_content
                else:
                    logger.warning("Hatenablog specialized extraction failed, falling back to generic extraction")

            # Remove unwanted elements but be more selective for dynamic content
            for element in soup(
                ["script", "style", "nav", "header", "footer", "aside", "noscript", "iframe", 
                 "advertisement", "ads", "social-share", "cookie-banner"]
            ):
                element.decompose()

            # ENHANCED CONTENT EXTRACTION with more aggressive strategies
            main_content = self._extract_main_content_enhanced(soup)
            
            if main_content:
                # Enhanced text extraction with better Japanese handling
                text = main_content.get_text(separator=" ", strip=True)
                
                # Remove common boilerplate content
                text = self._clean_note_com_boilerplate(text)
                
                # Normalize Unicode text (important for Japanese)
                import unicodedata
                text = unicodedata.normalize('NFKC', text)
                
                # Clean up excessive whitespace while preserving Japanese spacing
                text = re.sub(r'\s+', ' ', text)
                text = re.sub(r'\n\s*\n', '\n', text)
                
                # Enhanced content filtering - remove obvious non-content
                text = self._filter_content_lines(text)
                
                # Limit content length but be smarter about Japanese text
                text = self._truncate_content_smartly(text)
                
                return text

        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch article: {str(e)}")
        except UnicodeDecodeError as e:
            raise ValueError(f"Failed to decode article text (encoding issue): {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to parse article: {str(e)}")

        return None
    
    def _extract_main_content_enhanced(self, soup) -> Optional[any]:
        """Enhanced content extraction with multiple fallback strategies"""
        main_content = None
        
        # PHASE 1: Note.com-specific selectors with ULTRA-ENHANCED detection (2025 update)
        note_selectors = [
            # PRIORITY 1: Latest note.com content selectors (most reliable)
            "div[data-note-type='TextNote'] .note-common-styles__textnote-body",
            ".note-common-styles__textnote-body",
            ".o-noteContentText",
            
            # PRIORITY 2: Modern note.com article structure
            "article[data-testid='note-article'] .note-common-styles",
            "section[data-testid='article-body']",
            "div[data-module='TextModule']",  # Note.com text module
            ".note-post__body",
            ".js-textBody",
            
            # PRIORITY 3: Content-specific selectors for Pokemon articles
            ".note-common-styles__textnote",
            ".p-article__body",
            "main .note-common-styles", 
            "article .note-common-styles",
            
            # PRIORITY 4: Fallback note.com patterns
            ".note__body",
            ".article__body", 
            ".post__content",
            ".note-body",
            ".note-content",
            ".textnote-body",
            
            # PRIORITY 5: Generic note.com content containers
            "[data-testid*='note']",
            "[data-note-type*='Text']",
            ".note-article__content",
            ".note-article__body",
            
            # PRIORITY 6: Deep content extraction for problematic articles
            "div.note-common-styles div:not([class*='header']):not([class*='footer']):not([class*='nav'])",
            "main > div > div:not([class*='sidebar']):not([class*='menu'])",
            "[role='main'] .note-common-styles"
        ]
        
        # Enhanced note.com detection with better content validation
        for selector in note_selectors:
            try:
                elements = soup.select(selector)
                if elements:
                    # Try to find the one with the most meaningful content
                    for element in elements:
                        text_content = element.get_text(strip=True)
                        # Enhanced validation - check for Pokemon/VGC content indicators
                        content_score = self._calculate_content_score(text_content)
                        if content_score > 50:  # Higher threshold for better content
                            main_content = element
                            break
                    if main_content:
                        break
            except Exception:
                continue
        
        # PHASE 2: Generic content selectors with enhanced scoring
        if not main_content:
            generic_selectors = [
                "main", "article", ".content", ".post-content", ".entry-content",
                "#content", ".main-content", ".article-body", ".post-body",
                ".entry-body", "#main-content", ".main", ".post", ".entry",
                "#post", "#entry", ".container", ".wrapper", ".page-content"
            ]
            
            for selector in generic_selectors:
                try:
                    candidate = soup.select_one(selector)
                    if candidate:
                        text_preview = candidate.get_text(strip=True)
                        content_score = self._calculate_content_score(text_preview)
                        if content_score > 15:  # Even lower threshold for generic selectors
                            main_content = candidate
                            break
                except Exception:
                    continue
        
        # PHASE 3: Advanced div scanning with enhanced scoring
        if not main_content:
            all_divs = soup.find_all('div')
            best_candidate = None
            best_score = 0
            
            for div in all_divs:
                try:
                    text = div.get_text(strip=True)
                    if len(text) > 300:  # Require substantial content
                        content_score = self._calculate_content_score(text)
                        if content_score > best_score:
                            best_score = content_score
                            best_candidate = div
                except Exception:
                    continue
                    
            if best_candidate and best_score > 20:
                main_content = best_candidate

        # Final fallback
        if not main_content:
            main_content = soup.find("body")

        return main_content
    
    def _calculate_content_score(self, text: str) -> int:
        """Calculate content quality score for article text"""
        if not text or len(text) < 50:
            return 0
            
        score = 0
        
        # Length bonus (up to 1000 chars = 10 points)
        score += min(len(text) // 100, 10)
        
        # ULTRA-ENHANCED VGC/Pokemon content indicators (2025 comprehensive)
        vgc_indicators = {
            # ULTRA HIGH VALUE - Core VGC terms
            'vgc': 20, 'ポケモン': 18, '構築': 15, 'チーム': 12, 'ダブル': 12,
            'regulation': 15, 'pokemon': 12, 
            
            # HIGH VALUE - Competitive terms
            '努力値': 10, '調整': 10, 'ランクマ': 10, 'バトル': 8, 'tournament': 10,
            'ev': 10, 'battle': 8, 'double': 8, 'team': 8,
            
            # MEDIUM-HIGH VALUE - Stat/build terms
            'とくこう': 8, 'すばやさ': 8, 'こうげき': 8, 'ぼうぎょ': 8, 'とくぼう': 8,
            'nature': 6, 'ability': 6, '特性': 8, '性格': 8, '持ち物': 8,
            
            # MEDIUM VALUE - Game mechanics
            'item': 5, 'move': 5, 'tera': 8, 'テラス': 8, 'dynamax': 6, 'ダイマックス': 6,
            
            # NOTE.COM SPECIFIC - Common article patterns
            '最終': 8, '順位': 6, 'シーズン': 8, '使用': 6, '採用': 6,
            'final': 6, 'season': 6, 'ranking': 6,
            
            # POKEMON NAMES - Ultra high value (popular VGC Pokemon)
            'ガブリアス': 12, 'ランドロス': 12, 'ガオガエン': 12, 'エルフーン': 10,
            'パオジアン': 12, 'チオンジェン': 12, 'ディンルー': 10, 'イーユイ': 10,
            'テツノ': 10, 'ハバタクカミ': 10, 'サーフゴー': 10, 'コライドン': 12,
            'ミライドン': 12, 'ザマゼンタ': 12, 'ザシアン': 12, 'モロバレル': 8,
            
            # ENGLISH POKEMON NAMES
            'garchomp': 10, 'landorus': 10, 'incineroar': 10, 'whimsicott': 8,
            'chien-pao': 10, 'chi-yu': 10, 'gholdengo': 10, 'flutter mane': 10,
            'koraidon': 10, 'miraidon': 10, 'zamazenta': 10, 'zacian': 10
        }
        
        text_lower = text.lower()
        for indicator, value in vgc_indicators.items():
            count = text_lower.count(indicator.lower())
            score += count * value
        
        # Japanese character bonus (indicates Japanese content)
        japanese_chars = sum(1 for char in text[:1000] if ord(char) > 127)
        score += japanese_chars // 10
        
        # Penalty for likely UI/navigation content
        ui_indicators = ['login', 'signup', 'follow', 'share', 'menu', 'navigation', 'footer', 'header']
        for indicator in ui_indicators:
            if indicator in text_lower:
                score -= 10
        
        # Penalty for very repetitive content
        words = text_lower.split()
        if len(words) > 10:
            unique_words = len(set(words))
            repetition_ratio = unique_words / len(words)
            if repetition_ratio < 0.3:  # Very repetitive
                score -= 20
        
        return max(0, score)
    
    def _filter_content_lines(self, text: str) -> str:
        """Enhanced content filtering to remove UI elements and boilerplate"""
        if not text:
            return text
            
        lines = text.split('\n')
        filtered_lines = []
        prev_line = ""
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Skip repetitive lines (common in scraped content)
            if line == prev_line and len(line) < 50:
                continue
                
            # Skip lines that are likely UI elements
            ui_patterns = [
                r'^(login|signup|follow|share|menu|home|profile|settings)',
                r'^[\d\s\-\/\(\)]*$',  # Only numbers/symbols
                r'^(.*?)?\s*(フォロー|いいね|シェア|ログイン).*?$',
                r'^(.*?)?\s*(follow|like|share|login).*?$',
            ]
            
            is_ui = False
            for pattern in ui_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    is_ui = True
                    break
            
            if is_ui:
                continue
                
            # Keep lines that seem to be actual content - balanced approach  
            if (len(line) > 3 and  # Very low threshold - keep most content
                not (len(line) < 20 and any(ui_word in line.lower() for ui_word in 
                    ['copyright', '©', 'all rights', 'powered by', 'twitter.com']))):
                filtered_lines.append(line)
                prev_line = line
        
        return '\n'.join(filtered_lines)
    
    def _truncate_content_smartly(self, text: str) -> str:
        """Smart content truncation preserving sentence boundaries"""
        if len(text) <= 8000:
            return text
            
        # Try to cut at sentence boundaries for Japanese text
        sentences = text.split('。')  # Japanese sentence marker
        if len(sentences) > 1:
            result = ""
            for sentence in sentences:
                if len(result + sentence + '。') > 8000:
                    break
                result += sentence + '。'
            if result:
                return result
        
        # Fallback to paragraph boundaries
        paragraphs = text.split('\n\n')
        if len(paragraphs) > 1:
            result = ""
            for paragraph in paragraphs:
                if len(result + paragraph + '\n\n') > 8000:
                    break
                result += paragraph + '\n\n'
            if result:
                return result.strip()
        
        # Final fallback - simple truncation
        return text[:8000]

    def _clean_note_com_boilerplate(self, text: str) -> str:
        """
        Clean common note.com boilerplate text and navigation elements
        """
        if not text:
            return text

        # Common note.com patterns to remove
        patterns_to_remove = [
            r"note\.com.*?",
            r"フォロー.*?する",
            r"いいね.*?する", 
            r"シェア.*?する",
            r"コメント.*?する",
            r"購読.*?する",
            r"記事を読む.*?",
            r"もっと見る.*?",
            r"続きをみる.*?",
            r"ログイン.*?",
            r"会員登録.*?",
            # Remove common UI elements
            r"\d+\s*年\d+\s*月\d+\s*日.*?更新",
            r"更新.*?\d+\s*年",
            # Remove social sharing elements
            r"Twitter.*?共有",
            r"Facebook.*?共有",
            r"LINE.*?共有",
        ]
        
        cleaned_lines = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line matches any removal pattern
            should_remove = False
            for pattern in patterns_to_remove:
                if re.search(pattern, line, re.IGNORECASE):
                    should_remove = True
                    break
                    
            # Skip very short lines that are likely navigation
            if len(line) < 5:
                should_remove = True
                
            if not should_remove:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def calculate_ui_content_ratio(self, content: str) -> float:
        """Calculate the ratio of UI/navigation content to actual content"""
        if not content:
            return 1.0
            
        lines = content.split('\n')
        ui_lines = 0
        
        ui_indicators = [
            'login', 'signup', 'follow', 'share', 'menu', 'navigation', 
            'footer', 'header', 'フォロー', 'ログイン', 'メニュー', 'ナビ'
        ]
        
        for line in lines:
            line_lower = line.lower().strip()
            if (len(line_lower) < 100 and  # Short lines more likely to be UI
                any(indicator in line_lower for indicator in ui_indicators)):
                ui_lines += 1
        
        return ui_lines / max(1, len(lines))
    
    def _extract_note_com_content_specialized(self, soup) -> Optional[str]:
        """
        ULTRA-SPECIALIZED note.com content extraction optimized for Pokemon VGC articles
        This method specifically targets the unique DOM structure of note.com articles
        """
        try:
            # STRATEGY 1: Direct content extraction using ultra-specific note.com patterns
            ultra_specific_selectors = [
                # Most recent note.com article structure (high priority)
                "div.note-common-styles__textnote-body",
                "div[data-testid='article-body'] .note-common-styles",
                ".o-noteContentText",
                
                # Content within article containers
                "article .note-common-styles__textnote-body",
                "main .note-common-styles__textnote-body",
                
                # Text modules (note.com uses modular content)
                "div[data-module='TextModule'] .note-common-styles",
                ".js-textBody .note-common-styles",
                
                # Fallback patterns
                ".note-common-styles:not([class*='header']):not([class*='nav'])",
            ]
            
            best_content = None
            best_score = 0
            
            for selector in ultra_specific_selectors:
                try:
                    elements = soup.select(selector)
                    logger.info(f"Trying note.com selector: {selector} - found {len(elements)} elements")
                    for element in elements:
                        text_content = element.get_text(separator=" ", strip=True)
                        if len(text_content) > 100:  # Minimum length threshold
                            # Score this content for VGC relevance
                            content_score = self._calculate_content_score(text_content)
                            logger.debug(f"Element content score: {content_score} for {len(text_content)} chars")
                            if content_score > best_score:
                                best_score = content_score
                                best_content = element
                                logger.info(f"New best content found with score {best_score}")
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            if best_content:
                # Extract and clean the content
                text = best_content.get_text(separator=" ", strip=True)
                
                # Advanced note.com text cleaning
                text = self._clean_note_com_content_specialized(text)
                
                # Validate that we got meaningful content
                if self._validate_note_com_content(text):
                    return text
            
            # STRATEGY 2: If direct extraction failed, try broader content search
            # Look for any element with substantial Japanese VGC content
            all_potential_elements = soup.find_all(['div', 'section', 'article'])
            
            for element in all_potential_elements:
                try:
                    text = element.get_text(separator=" ", strip=True)
                    if len(text) > 200:  # Longer content for broader search
                        content_score = self._calculate_content_score(text)
                        if content_score > 50:  # High threshold for VGC content
                            cleaned_text = self._clean_note_com_content_specialized(text)
                            if self._validate_note_com_content(cleaned_text):
                                return cleaned_text
                except Exception:
                    continue
                    
            return None
            
        except Exception as e:
            print(f"Note.com specialized extraction failed: {e}")
            return None
    
    def _clean_note_com_content_specialized(self, text: str) -> str:
        """Ultra-specialized cleaning for note.com Pokemon VGC content"""
        if not text:
            return text
        
        # Remove note.com specific boilerplate with enhanced patterns
        note_com_removal_patterns = [
            r"note\.com.*?",
            r"記事を読む.*?",
            r"続きを読む.*?",
            r"もっと見る.*?",
            r"フォロー.*?する.*?",
            r"いいね.*?",
            r"コメント.*?",
            r"シェア.*?",
            r"購読.*?",
            r"ログイン.*?",
            r"会員登録.*?",
            r"有料記事.*?",
            r"プレミアム.*?",
            r"\d+年\d+月\d+日.*?更新",
            r"更新日時.*?",
            r"投稿日.*?",
            r"著者.*?",
            r"タグ.*?",
            r"カテゴリ.*?",
        ]
        
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip lines matching removal patterns
            should_skip = False
            for pattern in note_com_removal_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    should_skip = True
                    break
            
            # Skip very short lines that are likely navigation
            if len(line) < 3:
                should_skip = True
            
            # Skip lines that are just numbers or symbols
            if re.match(r'^[\d\s\-\/\(\)\.]+$', line):
                should_skip = True
                
            if not should_skip:
                cleaned_lines.append(line)
        
        # Join and normalize whitespace
        result = '\n'.join(cleaned_lines)
        
        # Final cleanup
        import unicodedata
        result = unicodedata.normalize('NFKC', result)
        result = re.sub(r'\s+', ' ', result)
        result = re.sub(r'\n\s*\n', '\n', result)
        
        return result.strip()
    
    def _validate_note_com_content(self, text: str) -> bool:
        """Validate that extracted note.com content exists and is not empty"""
        # Simple validation: just check that we have actual content
        # All the complex thresholds were unnecessary for large VGC articles
        return bool(text and text.strip())

    def _extract_hatenablog_content_specialized(self, soup) -> Optional[str]:
        """
        SPECIALIZED Hatenablog content extraction optimized for Pokemon VGC articles
        Addresses the missing Hatenablog support that was causing scraping failures
        """
        try:
            # STRATEGY 1: Hatenablog-specific article content selectors
            hatenablog_specific_selectors = [
                # Primary Hatenablog article content selectors
                ".entry-content",  # Main article content container
                ".entry-body",     # Article body content
                ".entry-inner",    # Inner content wrapper
                
                # Alternative Hatenablog patterns
                ".hatena-body",    # Hatena blog body
                ".entry-content-container",  # Content container
                "#main-content .entry-content",  # Main content area
                
                # More specific Hatenablog selectors
                "article .entry-content",
                "main .entry-content", 
                ".hentry .entry-content",  # hentry is common in Hatenablog
                ".post-content",
                ".blog-entry-content",
                
                # Fallback selectors for various Hatenablog themes
                ".entry",
                ".post-body",
                ".article-body",
                "#content .entry-content"
            ]
            
            best_content = None
            best_score = 0
            
            for selector in hatenablog_specific_selectors:
                try:
                    elements = soup.select(selector)
                    logger.info(f"Trying Hatenablog selector: {selector} - found {len(elements)} elements")
                    for element in elements:
                        text_content = element.get_text(separator=" ", strip=True)
                        if len(text_content) > 200:  # Minimum length threshold
                            # Score this content for VGC relevance
                            content_score = self._calculate_content_score(text_content)
                            logger.debug(f"Hatenablog element content score: {content_score} for {len(text_content)} chars")
                            if content_score > best_score:
                                best_score = content_score
                                best_content = element
                                logger.info(f"New best Hatenablog content found with score {best_score}")
                except Exception as e:
                    logger.debug(f"Hatenablog selector {selector} failed: {e}")
                    continue
            
            if best_content and best_score > 20:  # FIXED: Reduced from 30 to 20 for better compatibility
                # Extract and clean the content
                text = best_content.get_text(separator=" ", strip=True)
                
                # Specialized Hatenablog text cleaning
                text = self._clean_hatenablog_content_specialized(text)
                
                # Validate that we got meaningful VGC content
                if self._validate_hatenablog_content(text):
                    return text
            
            # STRATEGY 2: If direct extraction failed, try broader content search
            # Look for any element with substantial Japanese VGC content
            all_potential_elements = soup.find_all(['div', 'section', 'article', 'main'])
            
            for element in all_potential_elements:
                try:
                    text = element.get_text(separator=" ", strip=True)
                    if len(text) > 250:  # FIXED: Reduced from 300 to 250 for better compatibility
                        content_score = self._calculate_content_score(text)
                        if content_score > 40:  # FIXED: Reduced from 60 to 40 for broader compatibility
                            cleaned_text = self._clean_hatenablog_content_specialized(text)
                            if self._validate_hatenablog_content(cleaned_text):
                                logger.info(f"Hatenablog broad search successful with score {content_score}")
                                return cleaned_text
                except Exception:
                    continue
                    
            return None
            
        except Exception as e:
            logger.error(f"Hatenablog specialized extraction failed: {e}")
            return None
    
    def _clean_hatenablog_content_specialized(self, text: str) -> str:
        """Ultra-specialized cleaning for Hatenablog Pokemon VGC content"""
        if not text:
            return text
        
        # Remove Hatenablog specific boilerplate and UI elements
        hatenablog_removal_patterns = [
            # Hatenablog-specific UI elements
            r"はてなブログ.*?",
            r"hatena.*?blog.*?",
            r"ブログトップ.*?",
            r"記事一覧.*?",
            r"プロフィール.*?",
            r"読者になる.*?",
            r"購読する.*?",
            r"スター.*?",
            r"ブックマーク.*?",
            r"コメント.*?を書く",
            r"シェア.*?",
            r"ツイート.*?",
            r"はてブ.*?",
            
            # Date and metadata patterns
            r"\d{4}-\d{2}-\d{2}.*?\d{2}:\d{2}.*?",
            r"投稿日.*?",
            r"更新日.*?",
            r"カテゴリ.*?",
            r"タグ.*?",
            
            # Navigation and sidebar elements
            r"前の記事.*?",
            r"次の記事.*?",
            r"関連記事.*?",
            r"おすすめ記事.*?",
            r"人気記事.*?",
            r"最新記事.*?",
            r"アーカイブ.*?",
            
            # Common Hatenablog widgets and ads
            r"サイドバー.*?",
            r"フッター.*?",
            r"ヘッダー.*?",
            r"広告.*?",
            r"スポンサー.*?",
        ]
        
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip lines matching removal patterns
            should_skip = False
            for pattern in hatenablog_removal_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    should_skip = True
                    break
            
            # Skip very short lines that are likely navigation/UI
            if len(line) < 5:
                should_skip = True
            
            # Skip lines that are just dates, numbers, or symbols
            if re.match(r'^[\d\s\-\/\(\)\.:\→←]+$', line):
                should_skip = True
                
            if not should_skip:
                cleaned_lines.append(line)
        
        # Join and normalize whitespace
        result = '\n'.join(cleaned_lines)
        
        # Final cleanup
        import unicodedata
        result = unicodedata.normalize('NFKC', result)
        result = re.sub(r'\s+', ' ', result)
        result = re.sub(r'\n\s*\n', '\n', result)
        
        return result.strip()
    
    def _validate_hatenablog_content(self, text: str) -> bool:
        """Validate that extracted Hatenablog content exists and is not empty"""
        # Simple validation: just check that we have actual content
        # All the complex thresholds were unnecessary for large VGC articles
        return bool(text and text.strip())