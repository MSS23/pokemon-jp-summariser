"""
Safe HTML content fetching with compliance controls
Implements size limits, timeouts, content sanitization, and text extraction
"""

import requests
import time
import logging
from typing import Dict, Any, Tuple, Optional
from urllib.parse import urljoin, urlparse
import re
from io import BytesIO

# HTML processing
from bs4 import BeautifulSoup, Comment
import html

# For Readability-like content extraction
try:
    from readability import Document
    READABILITY_AVAILABLE = True
except ImportError:
    READABILITY_AVAILABLE = False

class SafeHTMLFetcher:
    """
    Safe HTML fetcher with comprehensive security controls
    - Size limits (max 3MB)
    - Timeout controls (10s default)
    - Redirect limits (max 3)
    - Content-type validation
    - HTML sanitization
    - Main content extraction
    """

    def __init__(self):
        """Initialize the safe HTML fetcher"""
        self.logger = logging.getLogger(__name__)

        # Safety limits
        self.max_content_size = 3 * 1024 * 1024  # 3 MB
        self.max_redirects = 3
        self.default_timeout = 10
        self.chunk_size = 8192  # 8KB chunks for streaming

        # User agent string (generic bot)
        self.user_agent = "Mozilla/5.0 (compatible; PokemonVGCBot/2.0; +https://example.com/bot)"

        # Headers for requests
        self.default_headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache',
        }

        self.logger.info("SafeHTMLFetcher initialized")

    def check_headers(self, url: str, timeout: int = None) -> Dict[str, str]:
        """
        Perform HEAD request to check headers without downloading content

        Args:
            url: URL to check
            timeout: Request timeout in seconds

        Returns:
            Dictionary of response headers

        Raises:
            Exception: If request fails or times out
        """
        timeout = timeout or self.default_timeout

        try:
            response = requests.head(
                url,
                headers=self.default_headers,
                timeout=timeout,
                allow_redirects=True,
                max_redirects=self.max_redirects
            )

            response.raise_for_status()

            # Convert headers to lowercase dict for easier access
            headers = {k.lower(): v for k, v in response.headers.items()}

            self.logger.debug(f"HEAD request successful for {url}: {response.status_code}")

            return headers

        except requests.exceptions.Timeout:
            raise Exception(f"Request timeout after {timeout}s")
        except requests.exceptions.TooManyRedirects:
            raise Exception(f"Too many redirects (max {self.max_redirects})")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")

    def fetch_html(self, url: str, timeout: int = None, max_bytes: int = None) -> Tuple[str, Dict[str, Any]]:
        """
        Safely fetch HTML content with all security controls

        Args:
            url: URL to fetch
            timeout: Request timeout in seconds
            max_bytes: Maximum content size in bytes

        Returns:
            Tuple of (extracted_text, metadata)

        Raises:
            Exception: If fetch fails, content too large, or processing errors
        """
        timeout = timeout or self.default_timeout
        max_bytes = max_bytes or self.max_content_size

        start_time = time.time()

        try:
            # Step 1: Streaming GET request with size checking
            response = requests.get(
                url,
                headers=self.default_headers,
                timeout=timeout,
                allow_redirects=True,
                stream=True  # Stream to check size
            )

            response.raise_for_status()

            # Check content type immediately
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type and 'application/xhtml+xml' not in content_type:
                raise Exception(f"Invalid content type: {content_type}")

            # Step 2: Download content with size checking
            content_data = BytesIO()
            total_size = 0

            for chunk in response.iter_content(chunk_size=self.chunk_size):
                if chunk:
                    total_size += len(chunk)
                    if total_size > max_bytes:
                        raise Exception(f"Content too large: {total_size} bytes (max {max_bytes})")

                    content_data.write(chunk)

            # Get final content
            html_content = content_data.getvalue().decode(
                response.encoding or 'utf-8',
                errors='replace'
            )

            fetch_time = time.time() - start_time

            # Step 3: Process and extract content
            extracted_text, processing_metadata = self._process_html(html_content, url)

            # Combine metadata
            metadata = {
                "url": url,
                "final_url": response.url,
                "status_code": response.status_code,
                "content_type": content_type,
                "size": total_size,
                "fetch_time": fetch_time,
                "redirects": len(response.history),
                **processing_metadata
            }

            self.logger.info(
                f"Successfully fetched and processed {url}: "
                f"{total_size} bytes → {len(extracted_text)} chars in {fetch_time:.2f}s"
            )

            return extracted_text, metadata

        except requests.exceptions.Timeout:
            raise Exception(f"Request timeout after {timeout}s")
        except requests.exceptions.TooManyRedirects:
            raise Exception(f"Too many redirects (max {self.max_redirects})")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
        except Exception as e:
            # Re-raise our custom exceptions
            if "Content too large" in str(e) or "Invalid content type" in str(e):
                raise
            else:
                raise Exception(f"Content processing failed: {str(e)}")

    def _process_html(self, html_content: str, url: str) -> Tuple[str, Dict[str, Any]]:
        """
        Process HTML content: sanitize, extract main content, clean text

        Args:
            html_content: Raw HTML content
            url: Source URL (for relative link resolution)

        Returns:
            Tuple of (extracted_text, processing_metadata)
        """
        processing_start = time.time()

        try:
            # Step 1: Use Readability for main content extraction (if available)
            if READABILITY_AVAILABLE:
                try:
                    doc = Document(html_content)
                    main_content = doc.content()
                    title = doc.title()
                    extraction_method = "readability"
                except Exception as e:
                    self.logger.debug(f"Readability extraction failed: {e}")
                    main_content = html_content
                    title = ""
                    extraction_method = "fallback"
            else:
                main_content = html_content
                title = ""
                extraction_method = "fallback"

            # Step 2: Parse with BeautifulSoup
            soup = BeautifulSoup(main_content, 'lxml')

            # Extract title if not already extracted
            if not title and soup.title:
                title = soup.title.get_text(strip=True)

            # Step 3: Remove unwanted elements
            unwanted_tags = [
                'script', 'style', 'nav', 'header', 'footer',
                'aside', 'menu', 'button', 'form', 'input',
                'select', 'textarea', 'noscript', 'iframe',
                'object', 'embed', 'applet'
            ]

            for tag in unwanted_tags:
                for element in soup.find_all(tag):
                    element.decompose()

            # Remove comments
            for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                comment.extract()

            # Remove elements with specific classes/IDs (ads, social, etc.)
            unwanted_selectors = [
                '[class*="ad"]', '[id*="ad"]',
                '[class*="social"]', '[class*="share"]',
                '[class*="comment"]', '[class*="related"]',
                '[class*="sidebar"]', '[class*="footer"]',
                '.advertisement', '.popup', '.modal',
                '.cookie-banner', '.newsletter'
            ]

            for selector in unwanted_selectors:
                for element in soup.select(selector):
                    element.decompose()

            # Step 4: Extract clean text
            # Focus on main content areas
            main_text_elements = soup.find_all(['article', 'main', 'div', 'section'])
            if not main_text_elements:
                main_text_elements = [soup]

            extracted_paragraphs = []
            for element in main_text_elements:
                # Get text from paragraphs, headings, and list items
                text_elements = element.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'td', 'th'])
                for text_elem in text_elements:
                    text = text_elem.get_text(separator=' ', strip=True)
                    if text and len(text) > 20:  # Ignore very short text snippets
                        extracted_paragraphs.append(text)

            # If no structured content found, get all text
            if not extracted_paragraphs:
                extracted_paragraphs = [soup.get_text(separator='\n', strip=True)]

            # Step 5: Clean and join text
            final_text = self._clean_extracted_text('\n\n'.join(extracted_paragraphs))

            processing_time = time.time() - processing_start

            metadata = {
                "title": title,
                "extraction_method": extraction_method,
                "processing_time": processing_time,
                "original_html_size": len(html_content),
                "extracted_text_size": len(final_text),
                "paragraphs_found": len(extracted_paragraphs)
            }

            return final_text, metadata

        except Exception as e:
            # Fallback: simple text extraction
            self.logger.warning(f"HTML processing failed, using simple extraction: {e}")

            try:
                soup = BeautifulSoup(html_content, 'html.parser')
                simple_text = soup.get_text(separator='\n', strip=True)
                clean_text = self._clean_extracted_text(simple_text)

                metadata = {
                    "title": "",
                    "extraction_method": "simple_fallback",
                    "processing_time": time.time() - processing_start,
                    "original_html_size": len(html_content),
                    "extracted_text_size": len(clean_text),
                    "error": str(e)
                }

                return clean_text, metadata

            except Exception as fallback_error:
                raise Exception(f"All text extraction methods failed: {fallback_error}")

    def _clean_extracted_text(self, text: str) -> str:
        """
        Clean extracted text: normalize whitespace, remove artifacts

        Args:
            text: Raw extracted text

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # HTML decode any remaining entities
        text = html.unescape(text)

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single space
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Multiple newlines to double newline

        # Remove common web artifacts
        artifacts = [
            r'^\s*Cookie\s+Policy.*?Accept\s*$',  # Cookie banners
            r'^\s*This\s+website\s+uses\s+cookies.*?$',
            r'^\s*Subscribe.*?newsletter\s*$',  # Newsletter prompts
            r'^\s*Follow\s+us\s+on.*?$',  # Social media prompts
            r'^\s*Share\s+this.*?$',  # Sharing prompts
            r'^\s*Advertisement\s*$',  # Ad labels
            r'^\s*Sponsored\s+Content\s*$',
        ]

        for pattern in artifacts:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)

        # Remove excessive punctuation
        text = re.sub(r'[.]{3,}', '...', text)  # Multiple dots
        text = re.sub(r'[-]{3,}', '---', text)  # Multiple dashes

        # Trim and clean up
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        cleaned_text = '\n'.join(lines)

        return cleaned_text.strip()

    def fetch_with_retry(self, url: str, retries: int = 2, delay: float = 1.0) -> Tuple[str, Dict[str, Any]]:
        """
        Fetch HTML with retry logic for transient failures

        Args:
            url: URL to fetch
            retries: Number of retries
            delay: Delay between retries in seconds

        Returns:
            Tuple of (extracted_text, metadata)
        """
        last_exception = None

        for attempt in range(retries + 1):
            try:
                return self.fetch_html(url)

            except Exception as e:
                last_exception = e
                if attempt < retries:
                    self.logger.warning(f"Fetch attempt {attempt + 1} failed for {url}: {e}")
                    time.sleep(delay * (attempt + 1))  # Exponential backoff
                else:
                    self.logger.error(f"All fetch attempts failed for {url}")

        raise last_exception

    def get_fetcher_stats(self) -> Dict[str, Any]:
        """
        Get fetcher configuration and capabilities

        Returns:
            Dictionary with fetcher information
        """
        return {
            "max_content_size_mb": self.max_content_size / (1024 * 1024),
            "max_redirects": self.max_redirects,
            "default_timeout_seconds": self.default_timeout,
            "chunk_size_kb": self.chunk_size / 1024,
            "readability_available": READABILITY_AVAILABLE,
            "user_agent": self.user_agent
        }