"""Django-integrated web scraper using Playwright and BeautifulSoup."""

import asyncio
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
import time

from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from bs4 import BeautifulSoup
from django.conf import settings

# Configure logging
logger = logging.getLogger(__name__)


class WebScrapingError(Exception):
    """Custom exception for web scraping errors"""
    pass


class JavaScriptRenderingError(WebScrapingError):
    """Specific exception for JavaScript rendering failures"""
    pass


class DjangoWebScraper:
    """Django-integrated web scraper using Playwright and BeautifulSoup."""

    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 2.0,
        custom_headers: Optional[Dict[str, str]] = None,
        agent_context: Optional[str] = None
    ):
        """Initialize the Django web scraper.

        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            custom_headers: Optional custom headers to add
            agent_context: Optional agent name for logging context
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.agent_context = agent_context or "WebScraper"
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.headers = self._get_default_headers()

        # Update with custom headers if provided
        if custom_headers:
            self.headers.update(custom_headers)

    def _log_with_context(self, level: str, message: str) -> None:
        """Log message with agent context."""
        formatted_message = f"[{self.agent_context}] {message}"
        getattr(logger, level)(formatted_message)

    def _get_default_headers(self) -> Dict[str, str]:
        """Get realistic browser headers to avoid detection."""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Cache-Control': 'max-age=0',
            'Pragma': 'no-cache'
        }

    @staticmethod
    def get_user_agent_options() -> Dict[str, str]:
        """Get different user agent options for various browsers/OS combinations."""
        return {
            'chrome_windows': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'chrome_mac': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'firefox_windows': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'firefox_mac': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0',
            'safari_mac': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15',
            'edge_windows': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0'
        }

    def add_referer_from_url(self, url: str) -> None:
        """Add a referer header based on the target URL domain."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = f"{parsed.scheme}://{parsed.netloc}"
            self.headers['Referer'] = domain
            logger.info(f"Added referer: {domain}")
        except Exception as e:
            logger.warning(f"Could not set referer for {url}: {e}")

    def enhance_headers_for_site(self, url: str) -> None:
        """Add site-specific headers that might help bypass detection."""
        try:
            # Add referer
            self.add_referer_from_url(url)

            # Add some randomization
            import random
            cache_control_options = [
                'max-age=0', 'no-cache', 'no-cache, no-store, must-revalidate'
            ]
            self.headers['Cache-Control'] = random.choice(
                cache_control_options)
        except Exception as e:
            logger.warning(f"Could not enhance headers for {url}: {e}")

    def update_headers(self, new_headers: Dict[str, str]) -> None:
        """Update existing headers with new values."""
        self.headers.update(new_headers)
        logger.info(f"Headers updated: {list(new_headers.keys())}")

    def set_user_agent(
        self,
        user_agent_key: Optional[str] = None,
        custom_user_agent: Optional[str] = None
    ) -> None:
        """Set user agent from predefined options or custom string."""
        if custom_user_agent:
            self.headers['User-Agent'] = custom_user_agent
            logger.info(f"Custom user agent set")
        elif user_agent_key:
            options = self.get_user_agent_options()
            if user_agent_key in options:
                self.headers['User-Agent'] = options[user_agent_key]
                logger.info(f"User agent set to: {user_agent_key}")
            else:
                logger.warning(
                    f"Unknown user agent key: {user_agent_key}. "
                    f"Available: {list(options.keys())}"
                )

    async def __aenter__(self):
        """Async context manager entry."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.firefox.launch(headless=True)
        self.context = await self.browser.new_context(
            user_agent=self.headers['User-Agent']
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with proper cleanup."""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")

    async def _detect_captcha(self, html_content: str) -> bool:
        """Detect common Captcha providers in the HTML content."""
        soup = BeautifulSoup(html_content, 'html.parser')
        text_content = soup.get_text().lower()

        # Check page title for common interstitial patterns
        title = soup.title.string.lower() if soup.title and soup.title.string else ''
        if 'just a moment...' in title or 'checking your browser' in title:
            logger.warning(
                f"Captcha/challenge detected by page title: '{
                    soup.title.string}'"
            )
            return True

        captcha_keywords = [
            "captcha", "are you a robot", "verify you are human",
            "verifying you are human", "checking your browser",
            "review the security of your connection",
            "site connection is secure", "enable javascript and cookies"
        ]
        if any(keyword in text_content for keyword in captcha_keywords):
            logger.warning(
                "Captcha/challenge detected by keyword in page text.")
            return True

        if soup.select_one('iframe[src*="recaptcha"], iframe[src*="hcaptcha"]'):
            logger.warning(
                "Captcha detected: reCAPTCHA or hCaptcha iframe found.")
            return True

        return False

    async def _render_with_playwright(
        self,
        url: str,
        wait_time: int = 2,
        timeout: int = 60
    ) -> str:
        """Render page with Playwright."""
        page = None
        try:
            page = await self.context.new_page()
            page.set_default_timeout(timeout * 1000)

            # Capture console messages for debugging
            def handle_console(msg):
                logger.debug(f"CONSOLE {msg.type}: {msg.text}")

            page.on('console', handle_console)

            # Navigate and wait for content
            await page.goto(url, wait_until='domcontentloaded', timeout=timeout * 1000)
            await page.wait_for_timeout(wait_time * 1000)
            html_content = await page.content()
            return html_content
        finally:
            if page:
                await page.close()

    async def fetch_and_render(
        self,
        url: str,
        wait_time: int = 2,
        timeout: int = 60
    ) -> BeautifulSoup:
        """Fetch URL and render JavaScript."""
        if not self.context:
            raise WebScrapingError(
                "Scraper not properly initialized. Use as async context manager."
            )

        self._log_with_context("info", f"Fetching URL: {url}")
        html_content = await self._render_with_playwright(url, wait_time, timeout)

        if not html_content or len(html_content.strip()) < 100:
            raise JavaScriptRenderingError("Rendered content appears empty")

        logger.info(f"Content length: {len(html_content)}")
        soup = BeautifulSoup(html_content, 'html.parser')

        if not soup or not soup.find():
            raise WebScrapingError("Failed to parse HTML content")

        return soup

    def clean_html(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Remove junk elements and clean HTML."""
        try:
            logger.info("Starting HTML cleanup")

            # Remove junk tags - preserve important interactive elements
            junk_tags = [
                'script', 'style', 'meta', 'link', 'noscript', 'svg', 'path',
                'nav', 'aside', 'form', 'input',
                'select', 'textarea', 'embed', 'object'
            ]

            removed_count = 0
            for tag_name in junk_tags:
                tags = soup.find_all(tag_name)
                for tag in tags:
                    tag.decompose()
                    removed_count += 1

            # Handle buttons separately - keep functional buttons
            buttons = soup.find_all('button')
            for button in buttons:
                classes = button.get('class', [])
                has_data_attrs = any(
                    attr.startswith('data-') for attr in button.attrs.keys()
                )
                is_functional = (
                    'btn' in classes or
                    'primary' in classes or
                    'secondary' in classes or
                    has_data_attrs or
                    button.get('type') in ['submit', 'button']
                )

                if not is_functional:
                    button.decompose()
                    removed_count += 1

            logger.info(f"Removed {removed_count} junk tags")

            # Remove elements with junk classes/ids
            junk_selectors = [
                '[class*="cookie"]', '[class*="popup"]',
                '[class*="ad"]', '[class*="advertisement"]', '[class*="banner"]',
                '[class*="navigation"]', '[class*="menu"]', '[class*="sidebar"]',
                '[class*="nav"]',
                '[id*="cookie"]', '[id*="popup"]', '[id*="ad"]',
                '[id*="navigation"]', '[id*="menu"]', '[id*="sidebar"]'
            ]

            modal_container_selectors = [
                '.modal-backdrop', '.modal-overlay', '[class*="modal-container"]',
                '[class*="modal-dialog"]', '[id*="modal-"]'
            ]

            removed_count = 0
            for selector in junk_selectors + modal_container_selectors:
                try:
                    elements = soup.select(selector)
                    for element in elements:
                        # Don't remove interactive elements
                        if element.name in ['a', 'button'] and (
                            'btn' in element.get('class', []) or
                            element.get('data-url') or
                            element.get('href')
                        ):
                            continue
                        element.decompose()
                        removed_count += 1
                except Exception as e:
                    logger.warning(f"Error with selector '{selector}': {e}")

            logger.info(
                f"Removed {removed_count} elements with junk selectors")

            # Clean attributes - preserve essential and functional attributes
            essential_attrs = [
                'href', 'src', 'alt', 'title',  # Core attributes
                'role', 'tabindex',  # Accessibility
                'aria-label', 'aria-haspopup', 'aria-expanded',  # ARIA attributes
            ]

            def should_preserve_attr(attr_name):
                return (
                    attr_name in essential_attrs or
                    attr_name.startswith('data-') or
                    attr_name.startswith('aria-')
                )

            cleaned_attrs = 0
            for element in soup.find_all():
                if element.attrs:
                    attrs_to_remove = [
                        attr for attr in element.attrs
                        if not should_preserve_attr(attr)
                    ]
                    for attr in attrs_to_remove:
                        del element.attrs[attr]
                        cleaned_attrs += 1

            logger.info(f"Cleaned {cleaned_attrs} attributes")
            return soup

        except Exception as e:
            logger.error(f"Error during HTML cleanup: {e}")
            raise WebScrapingError(f"HTML cleanup failed: {e}")

    def extract_meaningful_elements(self, soup: BeautifulSoup) -> List[Any]:
        """Extract meaningful elements and remove nested duplicates."""
        try:
            all_elements = soup.find_all()
            logger.info(f"Total elements in soup: {len(all_elements)}")

            # Find target elements
            target_tags = [
                'a', 'div', 'section', 'article', 'main', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                'p', 'span', 'table', 'tr', 'td', 'th', 'ul', 'ol', 'li', 'blockquote',
                'pre', 'code', 'strong', 'em', 'b', 'i', 'img'
            ]

            elements = soup.find_all(target_tags)
            logger.info(f'Total target elements found: {len(elements)}')

            # Fallback if no elements found
            if not elements:
                logger.warning(
                    "No target elements found, trying all elements with text...")
                elements = []
                for elem in all_elements:
                    if (elem.name and
                            elem.name not in ['html', 'head', 'body', 'script', 'style', 'meta', 'link']):
                        text = elem.get_text(strip=True)
                        if text and len(text) > 0:
                            elements.append(elem)
                logger.info(
                    f'Found {len(elements)} elements with any text content')

            # Filter meaningful content
            meaningful_elements = []
            for element in elements:
                try:
                    # Include img tags even without text content if they have src
                    if element.name == 'img' and element.get('src'):
                        meaningful_elements.append(element)
                    else:
                        text = element.get_text(strip=True)
                        if text and len(text.strip()) > 1:
                            meaningful_elements.append(element)
                except Exception as e:
                    logger.warning(f"Error processing element: {e}")
                    continue

            logger.info(f'Found {len(meaningful_elements)
                                 } meaningful elements before deduplication')

            # Remove nested elements
            unique_elements = self._remove_nested_elements(meaningful_elements)
            logger.info(f'After removing nested elements: {
                        len(unique_elements)} unique elements')

            return unique_elements

        except Exception as e:
            logger.error(f"Error extracting meaningful elements: {e}")
            raise WebScrapingError(f"Element extraction failed: {e}")

    def _remove_nested_elements(self, elements_list: List[Any]) -> List[Any]:
        """Remove elements that are children of other elements in the list.

        Special handling for img tags - always preserve them even if nested.
        """
        unique_elements = []

        for element in elements_list:
            try:
                # Always preserve img tags regardless of nesting
                if element.name == 'img':
                    unique_elements.append(element)
                    continue

                # Check if this element is a child of any other element in the list
                is_child = False
                for other_element in elements_list:
                    if element != other_element and other_element in element.parents:
                        is_child = True
                        break

                if not is_child:
                    unique_elements.append(element)

            except Exception as e:
                logger.warning(f"Error checking element nesting: {e}")
                unique_elements.append(element)

        return unique_elements

    def create_document(self, elements: List[Any]) -> str:
        """Create a single HTML document from extracted elements."""
        if not elements:
            raise WebScrapingError(
                "No elements provided for document creation")

        try:
            document_parts = []
            document_parts.append(
                '<html><head><meta charset="utf-8"><title>Scraped Content</title></head><body>'
            )

            for i, element in enumerate(elements):
                try:
                    # Add comment with element info
                    text_preview = element.get_text(strip=True)
                    preview = (
                        text_preview[:100] + "..."
                    ) if len(text_preview) > 100 else text_preview
                    document_parts.append(
                        f'<!-- Element {i +
                                        1}: {element.name} - "{preview}" -->'
                    )
                    document_parts.append(str(element))
                    document_parts.append('')  # Add spacing
                except Exception as e:
                    logger.warning(f"Error processing element {i}: {e}")
                    continue

            document_parts.append('</body></html>')
            single_document = '\n'.join(document_parts)

            logger.info(
                f'Created document with {len(elements)} elements '
                f'({len(single_document)} characters)'
            )
            return single_document

        except Exception as e:
            logger.error(f"Error creating document: {e}")
            raise WebScrapingError(f"Document creation failed: {e}")

    async def validate_url(self, url: str) -> bool:
        """Validate that a URL is accessible using the same Playwright approach as scraping.

        Args:
            url: The URL to validate

        Returns:
            True if URL is accessible, False otherwise
        """
        try:
            # Use the same approach as the scraper - try to render the page
            page = await self.context.new_page()
            page.set_default_timeout(10000)  # Shorter timeout for validation

            await page.goto(url, wait_until='domcontentloaded', timeout=10000)
            html_content = await page.content()

            await page.close()

            # If we got content, consider it valid
            if html_content and len(html_content.strip()) > 100:
                logger.info(f"URL validation successful: {url}")
                return True
            else:
                logger.warning(
                    f"URL validation failed - minimal content: {url}")
                return False

        except Exception as e:
            logger.warning(f"URL validation failed for {url}: {e}")
            return False

    async def extract_navigation_links(self, url: str) -> List[Dict[str, str]]:
        """Extract all navigation and content links from a website, including modern JavaScript-based navigation.

        Args:
            url: The URL to extract links from

        Returns:
            List of dictionaries with 'text', 'url', 'description', and 'selector_type' keys
        """
        try:
            # First scrape the main page
            soup = await self.fetch_and_render(url, wait_time=3, timeout=30)

            # Extract all links with context
            navigation_links = []
            base_domain = self._get_base_domain(url)
            found_links = set()  # To avoid duplicates

            # Extract traditional href-based links
            traditional_links = self._extract_traditional_links(soup, url, base_domain, found_links)
            navigation_links.extend(traditional_links)

            # Extract modern JavaScript/clickable navigation elements
            modern_links = self._extract_modern_navigation(soup, url, base_domain, found_links)
            navigation_links.extend(modern_links)

            # Extract navigation from JavaScript if present
            js_links = self._extract_js_navigation(soup, url, base_domain, found_links)
            navigation_links.extend(js_links)

            # Sort by navigation links first, then by text
            navigation_links.sort(key=lambda x: (
                x['selector_type'] != 'navigation', x['text']))

            logger.info(f"Found {len(navigation_links)} potential navigation links from {url}")
            return navigation_links

        except Exception as e:
            logger.error(f"Failed to extract navigation links from {url}: {e}")
            return []

    def _extract_traditional_links(self, soup: BeautifulSoup, base_url: str, base_domain: str, found_links: set) -> List[Dict[str, str]]:
        """Extract traditional <a href=""> navigation links."""
        navigation_links = []
        
        # Look for navigation-specific elements first
        nav_selectors = [
            'nav a', 'header a', '.navigation a', '.nav a', '.menu a',
            '.navbar a', '.main-nav a', '.primary-nav a', '.site-nav a',
            '.header-nav a', '.top-nav a', '[role="navigation"] a'
        ]

        # Also look for content links that might be important pages
        content_selectors = [
            'main a', '.content a', '.main-content a', '.page-content a',
            '.footer a', 'footer a', '.site-footer a'
        ]

        all_selectors = nav_selectors + content_selectors

        for selector in all_selectors:
            try:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    if not href:
                        continue

                    # Convert relative URLs to absolute
                    absolute_url = self._resolve_url(href, base_url)
                    if not absolute_url or absolute_url in found_links:
                        continue

                    # Only include links from the same domain
                    if not self._is_same_domain(absolute_url, base_domain):
                        continue

                    # Get link text and context
                    link_text = link.get_text(strip=True)
                    # Skip very long text
                    if not link_text or len(link_text) > 100:
                        continue

                    # Skip common non-content links
                    if self._should_skip_link(absolute_url, link_text):
                        continue

                    context = self._get_element_context(link)
                    
                    navigation_links.append({
                        'text': link_text,
                        'url': absolute_url,
                        'description': context,
                        'selector_type': 'navigation' if selector in nav_selectors else 'content'
                    })
                    found_links.add(absolute_url)

            except Exception as e:
                logger.warning(f"Error processing traditional selector '{selector}': {e}")
                continue

        return navigation_links

    def _extract_modern_navigation(self, soup: BeautifulSoup, base_url: str, base_domain: str, found_links: set) -> List[Dict[str, str]]:
        """Extract modern JavaScript-based navigation elements without href attributes."""
        navigation_links = []
        
        # Modern navigation selectors for clickable elements
        modern_nav_selectors = [
            'nav div.nav-link', 'nav .nav-item div', 'nav .nav-item span',
            'header div.nav-link', 'header .nav-item div', 'header .nav-item span',
            '.navigation div[class*="nav"]', '.menu div[class*="nav"]',
            '.navbar div[class*="nav"]', '.header-menu div[class*="nav"]',
            '[class*="cursor-pointer"]', 'div[role="button"]',
            'nav button', 'header button[class*="nav"]'
        ]

        for selector in modern_nav_selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    # Skip if this element contains an <a> tag (already handled)
                    if element.find('a'):
                        continue
                    
                    # Get element text
                    element_text = element.get_text(strip=True)
                    if not element_text or len(element_text) > 100:
                        continue

                    # Skip non-navigation text
                    if self._should_skip_navigation_text(element_text):
                        continue

                    # Try to extract URL from data attributes
                    nav_url = self._extract_data_attributes(element, base_url)
                    
                    # If no data attribute URL, try to infer from text
                    if not nav_url:
                        nav_url = self._infer_url_from_text(element_text, base_url)

                    if nav_url and nav_url not in found_links:
                        # Only include links from the same domain
                        if self._is_same_domain(nav_url, base_domain):
                            context = self._get_element_context(element)
                            
                            navigation_links.append({
                                'text': element_text,
                                'url': nav_url,
                                'description': context,
                                'selector_type': 'navigation',
                                'extraction_method': 'modern_navigation'
                            })
                            found_links.add(nav_url)

            except Exception as e:
                logger.warning(f"Error processing modern navigation selector '{selector}': {e}")
                continue

        return navigation_links

    def _extract_js_navigation(self, soup: BeautifulSoup, base_url: str, base_domain: str, found_links: set) -> List[Dict[str, str]]:
        """Extract navigation URLs from JavaScript code and data structures."""
        navigation_links = []
        
        try:
            # Look for script tags with navigation data
            script_tags = soup.find_all('script')
            
            for script in script_tags:
                script_content = script.string
                if not script_content:
                    continue

                # Look for common navigation patterns in JavaScript
                import re
                
                # Pattern for router configurations
                route_patterns = [
                    r'["\']([^"\']*(?:floor-plans|amenities|contact|tour|photos|neighborhood|pet)[^"\']*)["\']',
                    r'path:\s*["\']([^"\']+)["\']',
                    r'route:\s*["\']([^"\']+)["\']',
                    r'href:\s*["\']([^"\']+)["\']'
                ]
                
                for pattern in route_patterns:
                    matches = re.findall(pattern, script_content, re.IGNORECASE)
                    for match in matches:
                        if match and match.startswith('/'):
                            absolute_url = self._resolve_url(match, base_url)
                            if (absolute_url and 
                                absolute_url not in found_links and 
                                self._is_same_domain(absolute_url, base_domain)):
                                
                                # Extract meaningful name from URL
                                url_parts = match.strip('/').split('/')
                                nav_text = url_parts[-1].replace('-', ' ').title() if url_parts else 'Page'
                                
                                navigation_links.append({
                                    'text': nav_text,
                                    'url': absolute_url,
                                    'description': f'Found in JavaScript: {match}',
                                    'selector_type': 'navigation',
                                    'extraction_method': 'javascript'
                                })
                                found_links.add(absolute_url)

        except Exception as e:
            logger.warning(f"Error extracting JavaScript navigation: {e}")

        return navigation_links

    def _extract_data_attributes(self, element, base_url: str) -> Optional[str]:
        """Extract navigation URL from element data attributes."""
        data_attrs = ['data-url', 'data-href', 'data-target', 'data-route', 'data-link', 'data-path']
        
        for attr in data_attrs:
            value = element.get(attr)
            if value:
                return self._resolve_url(value, base_url)
        
        return None

    def _infer_url_from_text(self, text: str, base_url: str) -> Optional[str]:
        """Infer likely URL from navigation text based on common patterns."""
        if not text:
            return None
            
        # Clean and normalize text
        clean_text = text.lower().strip()
        
        # Common navigation text to URL mappings
        url_mappings = {
            'floor plans': '/floor-plans/',
            'floorplans': '/floor-plans/',
            'amenities': '/amenities/',
            'contact': '/contact/',
            'contact us': '/contact/',
            'tour': '/tour/',
            'virtual tour': '/tour/',
            'schedule tour': '/tour/',
            'photos': '/photos/',
            'gallery': '/photos/',
            'neighborhood': '/neighborhood/',
            'location': '/location/',
            'pet friendly': '/pet-friendly/',
            'pets': '/pet-friendly/',
            'pet policy': '/pet-friendly/',
            'apply': '/apply/',
            'application': '/apply/',
            'residents': '/residents/',
            'resident portal': '/residents/',
            'about': '/about/',
            'specials': '/specials/',
            'pricing': '/pricing/',
            'availability': '/availability/'
        }
        
        # Check direct mappings first
        if clean_text in url_mappings:
            return self._resolve_url(url_mappings[clean_text], base_url)
        
        # Try partial matches
        for key, url_path in url_mappings.items():
            if key in clean_text:
                return self._resolve_url(url_path, base_url)
        
        # Fallback: convert text to URL-like format
        url_text = clean_text.replace(' ', '-').replace('_', '-')
        # Remove special characters except hyphens
        import re
        url_text = re.sub(r'[^a-z0-9-]', '', url_text)
        
        if url_text and len(url_text) > 2:
            return self._resolve_url(f'/{url_text}/', base_url)
        
        return None

    def _should_skip_navigation_text(self, text: str) -> bool:
        """Check if navigation text should be skipped."""
        if not text:
            return True
            
        skip_patterns = [
            'share on', 'facebook', 'twitter', 'linkedin', 'copy link',
            'sign in', 'login', 'logout', 'register', 'privacy', 'terms',
            'cookies', 'sitemap', 'search', 'menu', 'toggle', 'close',
            'skip to', 'accessibility'
        ]
        
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in skip_patterns)

    def _should_skip_link(self, url: str, text: str) -> bool:
        """Check if a link should be skipped based on URL and text patterns."""
        skip_patterns = [
            'javascript:', 'mailto:', 'tel:', '#',
            'login', 'sign in', 'register', 'logout',
            'privacy', 'terms', 'cookies', 'sitemap'
        ]

        return any(pattern in url.lower() or pattern in text.lower() for pattern in skip_patterns)

    def _get_element_context(self, element) -> str:
        """Get contextual information from an element's parent."""
        context = ''
        parent = element.parent
        if parent:
            context = parent.get_text(strip=True)
            # Limit context length
            if len(context) > 200:
                context = context[:200] + '...'
        return context

    def _get_base_domain(self, url: str) -> str:
        """Extract base domain from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return f"{parsed.scheme}://{parsed.netloc}"
        except Exception:
            return ""

    def _resolve_url(self, href: str, base_url: str) -> Optional[str]:
        """Resolve relative URLs to absolute URLs."""
        try:
            from urllib.parse import urljoin, urlparse

            # Skip invalid hrefs
            if not href or href.startswith(('javascript:', 'mailto:', 'tel:')):
                return None

            # Handle fragment-only links
            if href.startswith('#'):
                return None

            # Resolve relative URLs
            absolute_url = urljoin(base_url, href)

            # Basic URL validation
            parsed = urlparse(absolute_url)
            if not parsed.scheme or not parsed.netloc:
                return None

            return absolute_url
        except Exception:
            return None

    def _is_same_domain(self, url: str, base_domain: str) -> bool:
        """Check if URL belongs to the same domain."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            url_domain = f"{parsed.scheme}://{parsed.netloc}"
            return url_domain == base_domain
        except Exception:
            return False

    async def scrape_multiple_pages(
        self,
        main_url: str,
        max_pages: int = 10,
        wait_time: int = 2,
        timeout: int = 30
    ) -> Dict[str, str]:
        """Scrape multiple pages from a website, starting with navigation discovery.

        Args:
            main_url: The main website URL to start from
            max_pages: Maximum number of pages to scrape
            wait_time: Seconds to wait for dynamic content
            timeout: Timeout for page loading

        Returns:
            Dictionary mapping URLs to their scraped content
        """
        scraped_content = {}

        try:
            # First, scrape the main page
            logger.info(f"Starting multi-page scrape from {main_url}")
            main_content = await self.scrape_url_to_content(
                main_url, wait_time=wait_time, timeout=timeout,
                return_format='markdown', validate_first=True
            )

            if main_content:
                scraped_content[main_url] = main_content
                logger.info(f"Successfully scraped main page: {main_url}")
            else:
                logger.warning(f"Failed to scrape main page: {main_url}")
                return scraped_content

            # Extract navigation links
            nav_links = await self.extract_navigation_links(main_url)
            logger.info(f"Found {len(nav_links)} navigation links to explore")

            # Scrape additional pages (up to max_pages)
            pages_scraped = 1  # Already scraped main page

            for link_info in nav_links:
                if pages_scraped >= max_pages:
                    logger.info(f"Reached maximum page limit of {max_pages}")
                    break

                link_url = link_info['url']

                # Skip if already scraped
                if link_url in scraped_content:
                    continue

                logger.info(f"Attempting to scrape: {
                            link_info['text']} ({link_url})")

                # Scrape the page with validation
                page_content = await self.scrape_url_to_content(
                    link_url, wait_time=wait_time, timeout=timeout,
                    return_format='markdown', validate_first=True
                )

                if page_content:
                    scraped_content[link_url] = page_content
                    pages_scraped += 1
                    logger.info(f"Successfully scraped: {link_info['text']}")
                else:
                    logger.warning(f"Failed to scrape: {
                                   link_info['text']} ({link_url})")

            logger.info(
                f"Multi-page scrape completed. Scraped {pages_scraped} pages total.")
            return scraped_content

        except Exception as e:
            logger.error(f"Multi-page scraping failed: {e}")
            return scraped_content

    async def scrape_url_to_content(
        self,
        url: str,
        wait_time: int = 2,
        timeout: int = 60,
        return_format: str = 'markdown',
        validate_first: bool = True
    ) -> Optional[str]:
        """Scrape URL and return content in specified format (markdown or html).

        This method is designed to replace Firecrawl API calls.

        Args:
            url: The URL to scrape
            wait_time: Seconds to wait for dynamic content
            timeout: Timeout for page loading
            return_format: 'markdown' or 'html'
            validate_first: Whether to validate URL accessibility before scraping

        Returns:
            Scraped content as markdown or HTML string
        """
        try:
            start_time = time.time()
            self._log_with_context("info", f"Starting scrape of {url}")

            # Validate URL if requested
            if validate_first:
                logger.info(f"Validating URL accessibility: {url}")
                if not await self.validate_url(url):
                    logger.warning(f"URL validation failed for {
                                   url} - skipping scrape")
                    return None

            # Fetch and render the page
            soup = await self.fetch_and_render(url, wait_time, timeout)

            # Clean HTML
            cleaned_soup = self.clean_html(soup)

            # Extract meaningful elements
            unique_elements = self.extract_meaningful_elements(cleaned_soup)

            if not unique_elements:
                logger.warning('No unique elements found after processing')
                # Fallback to raw text
                text_content = cleaned_soup.get_text(
                    separator='\n', strip=True)
                if text_content and len(text_content) > 100:
                    if return_format == 'markdown':
                        return f"# Extracted Content from {url}\n\n{text_content}"
                    else:
                        return f"<html><body><h1>Extracted Content</h1><pre>{text_content}</pre></body></html>"
                return None

            # Create final document
            if return_format == 'markdown':
                # Convert HTML elements to markdown-like format
                content_parts = []
                content_parts.append(f"# Content from {url}\n")

                for element in unique_elements:
                    # Handle img tags specially
                    if element.name == 'img':
                        src = element.get('src')
                        alt = element.get('alt', '')
                        if src:
                            # Convert relative URLs to absolute
                            img_url = self._resolve_url(src, url)
                            img_text = f"IMAGE: {img_url}"
                            if alt:
                                img_text += f" (alt: {alt})"
                            content_parts.append(img_text)
                            content_parts.append("")
                    else:
                        text = element.get_text(strip=True)
                        if text:
                            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                                level = int(element.name[1])
                                content_parts.append(f"{'#' * level} {text}\n")
                            elif element.name == 'a' and element.get('href'):
                                content_parts.append(
                                    f"[{text}]({element.get('href')})")
                            elif element.name in ['li']:
                                content_parts.append(f"- {text}")
                            else:
                                content_parts.append(text)
                            content_parts.append("")

                final_content = '\n'.join(content_parts)
            else:
                # Return as HTML document
                final_content = self.create_document(unique_elements)

            # Log summary
            processing_time = time.time() - start_time
            self._log_with_context("info",
                                   f"Scraping completed in {
                                       processing_time:.2f}s. "
                                   f"Content length: {
                                       len(final_content)} characters"
                                   )

            return final_content

        except Exception as e:
            logger.error(f"Scraping failed for {url}: {e}")
            return None

    async def scrape_url(
        self,
        url: str,
        output_file: Optional[str] = None,
        wait_time: int = 2,
        timeout: int = 60
    ) -> Optional[str]:
        """Main scraping method that orchestrates the entire process.

        This method maintains compatibility with the original scraper interface.
        """
        content = await self.scrape_url_to_content(url, wait_time, timeout, 'html')

        if content and output_file:
            try:
                output_path = Path(output_file)
                output_path.write_text(content, encoding='utf-8')
                logger.info(f"Document saved to '{output_file}'")
            except Exception as e:
                logger.error(f"Failed to save document: {e}")

        return content
