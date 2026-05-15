"""
browser_automation.py
Playwright-based browser automation and measurement collection.
"""

import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
import logging

from .website_session import WebsiteSession, WebsiteMetrics
from .error_handling import classify_error, ErrorType, MeasurementError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BrowserAutomation:
    """
    Manages Playwright browser automation for web measurement.
    Handles measurement collection with robust error handling and timeout management.
    """
    
    def __init__(
        self,
        timeout_ms: int = 30000,
        headless: bool = True,
        browser_type: str = "chromium"
    ):
        """
        Initialize browser automation.
        
        Args:
            timeout_ms: Page load timeout in milliseconds
            headless: Run browser in headless mode
            browser_type: Browser type (chromium, firefox, webkit)
        """
        self.timeout_ms = timeout_ms
        self.headless = headless
        self.browser_type = browser_type
        self.browser: Optional[Browser] = None
        self.playwright = None
        self.sessions: List[WebsiteSession] = []
    
    async def initialize(self):
        """Start Playwright and browser instance."""
        try:
            self.playwright = await async_playwright().start()
            
            # Select browser
            if self.browser_type == "firefox":
                browser_launcher = self.playwright.firefox
            elif self.browser_type == "webkit":
                browser_launcher = self.playwright.webkit
            else:
                browser_launcher = self.playwright.chromium
            
            self.browser = await browser_launcher.launch(headless=self.headless)
            logger.info(f"Browser initialized: {self.browser_type}")
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise
    
    async def close(self):
        """Close browser and Playwright."""
        if self.browser:
            await self.browser.close()
            logger.info("Browser closed")
        if self.playwright:
            await self.playwright.stop()
            logger.info("Playwright stopped")
    
    async def measure_website(self, session: WebsiteSession) -> WebsiteSession:
        """
        Measure a single website and collect metrics.
        
        Args:
            session: WebsiteSession to populate with metrics
            
        Returns:
            Session with collected metrics
        """
        context: Optional[BrowserContext] = None
        page: Optional[Page] = None
        
        try:
            # Create browser context with performance monitoring
            context = await self.browser.new_context()
            page = await context.new_page()
            
            # Set timeout
            page.set_default_timeout(self.timeout_ms)
            
            # Collect network metrics
            request_stats = {
                "total": 0,
                "failed": 0,
                "blocked": 0
            }
            response_size = 0
            
            def on_request(request):
                request_stats["total"] += 1
                # Track blocked requests (e.g., ad-blockers)
                if request.resource_type in ["image", "stylesheet", "font", "media"]:
                    pass  # Could track these separately
            
            def on_response(response):
                nonlocal response_size
                try:
                    if response.status >= 400:
                        request_stats["failed"] += 1
                    # Approximate response size
                    if response.ok:
                        response_size += len(response.url)
                except:
                    pass
            
            # Register event listeners
            page.on("request", on_request)
            page.on("response", on_response)
            
            # Navigate and measure
            start_time = datetime.utcnow()
            response = await page.goto(session.url, wait_until="domcontentloaded")
            navigation_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Get timing metrics via JavaScript
            timing_data = await page.evaluate("""
                () => {
                    const navigation = performance.getEntriesByType('navigation')[0];
                    const paint = performance.getEntriesByType('paint');
                    
                    return {
                        domContentLoaded: navigation ? navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart : null,
                        loadComplete: navigation ? navigation.loadEventEnd - navigation.loadEventStart : null,
                        timeToFirstByte: navigation ? navigation.responseStart - navigation.fetchStart : null,
                        firstPaint: paint.length > 0 ? paint[0].startTime : null,
                        redirects: navigation ? navigation.redirectCount : 0
                    };
                }
            """)
            
            # Get page size
            page_content = await page.content()
            approximate_page_size = len(page_content.encode('utf-8'))
            
            # Populate metrics
            session.metrics.page_load_time_ms = navigation_time
            session.metrics.dom_content_loaded_ms = timing_data.get("domContentLoaded")
            session.metrics.time_to_first_byte_ms = timing_data.get("timeToFirstByte")
            session.metrics.http_status_code = response.status if response else None
            session.metrics.response_size_bytes = approximate_page_size
            session.metrics.redirect_count = timing_data.get("redirects", 0)
            session.metrics.total_requests = request_stats["total"]
            session.metrics.failed_requests = request_stats["failed"]
            session.metrics.blocked_requests = request_stats["blocked"]
            session.metrics.user_agent = await page.evaluate("() => navigator.userAgent")
            
            # Mark as successful
            session.record_success()
            logger.info(f"✓ Measured {session.name}: {navigation_time:.0f}ms")
            
        except asyncio.TimeoutError:
            session.record_timeout()
            session.metrics.error_type = ErrorType.TIMEOUT.value
            session.metrics.error_message = f"Page load timeout after {self.timeout_ms}ms"
            logger.warning(f"✗ Timeout: {session.name}")
            
        except Exception as e:
            # Classify the error
            error = classify_error(e, {"url": session.url})
            session.metrics.error_type = error.error_type.value
            session.metrics.error_message = error.message
            session.metrics.error_details = error.details
            
            # Set specific flags
            if error.error_type == ErrorType.SSL_ERROR:
                session.record_ssl_error()
            elif error.error_type == ErrorType.HTTP_ERROR:
                # Try to extract HTTP status
                if hasattr(e, 'status'):
                    session.record_http_error(e.status)
            
            logger.warning(f"✗ Error ({error.error_type.value}): {session.name} - {error.message}")
            
        finally:
            # Cleanup
            if page:
                await page.close()
            if context:
                await context.close()
        
        return session
    
    async def measure_batch(self, sessions: List[WebsiteSession]) -> List[WebsiteSession]:
        """
        Measure a batch of websites sequentially.
        
        Args:
            sessions: List of WebsiteSession objects to measure
            
        Returns:
            List of measured sessions
        """
        measured_sessions = []
        for i, session in enumerate(sessions, 1):
            logger.info(f"[{i}/{len(sessions)}] Measuring {session.name}...")
            measured_session = await self.measure_website(session)
            measured_sessions.append(measured_session)
        
        self.sessions.extend(measured_sessions)
        return measured_sessions
    
    def get_all_metrics(self) -> List[Dict[str, Any]]:
        """Get all collected metrics as list of dictionaries."""
        return [session.metrics.to_dict() for session in self.sessions]
