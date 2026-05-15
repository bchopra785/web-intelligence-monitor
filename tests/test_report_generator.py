"""
test_report_generator.py
Unit tests for the automated report generator.
"""

import unittest

from report.generator import ReportGenerator


class TestReportGenerator(unittest.TestCase):
    """Test report generation sections and content."""

    def setUp(self):
        self.metrics = [
            {
                "url": "https://www.example.com",
                "name": "Example",
                "category": "ecommerce-general",
                "page_load_time_ms": 120,
                "is_success": True,
                "is_timeout": False,
                "is_ssl_error": False,
                "is_http_error": False,
                "error_type": None,
                "error_message": None,
            },
            {
                "url": "https://httpstat.us/500",
                "name": "HTTP 500",
                "category": "edge-case",
                "page_load_time_ms": None,
                "is_success": False,
                "is_timeout": False,
                "is_ssl_error": True,
                "is_http_error": False,
                "error_type": "ssl_error",
                "error_message": "SSL/TLS error: Page.goto: net::ERR_EMPTY_RESPONSE",
            },
        ]

    def test_generate_report_contains_key_sections(self):
        generator = ReportGenerator()
        generator.load_metrics(self.metrics)
        report = generator.generate_report()

        self.assertIn("EXECUTIVE SUMMARY", report)
        self.assertIn("TOP 10 PERFORMING WEBSITES", report)
        self.assertIn("BLOCKED / FAILED ACCESS CASES", report)
        self.assertIn("CONCLUSIONS & RECOMMENDATIONS", report)

    def test_generate_report_mentions_failed_access(self):
        generator = ReportGenerator()
        generator.load_metrics(self.metrics)
        report = generator.generate_report()

        self.assertIn("HTTP 500", report)
        self.assertIn("ssl_error", report)


if __name__ == '__main__':
    unittest.main()