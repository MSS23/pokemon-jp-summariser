"""
Article scraper for VGC content with robust multi-strategy approach.
"""

import re
import requests
from bs4 import BeautifulSoup
from typing import Optional
import time


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
                content = strategy_func(url)
                if content and len(content.strip()) > 50:  # Lower minimum for better fallback
                    return content
            except Exception as e:
                # Log the error but continue to next strategy
                print(f"Scraping strategy failed: {strategy_func.__name__}: {str(e)}")
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
        """Enhanced content processing from HTTP response"""
        try:
            
            # Enhanced encoding detection and handling
            if response.encoding is None or response.encoding.lower() in ['iso-8859-1', 'ascii']:
                # Force UTF-8 for Japanese content
                response.encoding = 'utf-8'
            
            # Use response.content with explicit UTF-8 decoding for better Japanese handling
            try:
                html_content = response.content.decode('utf-8', errors='ignore')
            except UnicodeDecodeError:
                # Fallback to response.text with encoding set
                html_content = response.text

            soup = BeautifulSoup(html_content, "html.parser")

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
        
        # PHASE 1: Note.com-specific selectors with enhanced detection
        note_selectors = [
            # ULTRA-ENHANCED note.com selectors (covers more variations)
            ".note-common-styles__textnote-body",
            ".o-noteContentText", 
            ".note-post__body",
            "div[data-module='TextModule']",  # Note.com text module
            ".note-common-styles__textnote",
            ".js-textBody", 
            ".p-article__body",
            "section[data-testid='article-body']",
            
            # More note.com patterns found in different layouts
            "article .note-common-styles",
            "main .note-common-styles", 
            ".note__body",
            ".article__body", 
            ".post__content",
            ".note-body",
            "[data-testid*='note']",
            ".note-content",
            ".textnote-body"
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
        
        # VGC/Pokemon content indicators (high value)
        vgc_indicators = {
            'ポケモン': 15, '構築': 12, 'チーム': 8, 'バトル': 8, 'ダブル': 10,
            'ランクマ': 8, '調整': 6, '努力値': 8, 'とくこう': 5, 'すばやさ': 5,
            'pokemon': 10, 'vgc': 15, 'team': 6, 'battle': 6, 'double': 8,
            'regulation': 10, 'tournament': 8, 'ev': 8, 'nature': 5, 'ability': 5
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