"""
test_error_handling.py
Unit tests for centralized error classification.
"""

import unittest

from crawler.error_handling import classify_error, ErrorType


class TestErrorClassification(unittest.TestCase):
    """Test error classification logic."""

    def test_timeout_detection(self):
        """Test timeout error detection."""
        timeout_error = TimeoutError("Connection timed out")
        classified = classify_error(timeout_error)

        self.assertEqual(classified.error_type, ErrorType.TIMEOUT)

    def test_ssl_error_detection(self):
        """Test SSL error detection."""
        ssl_error = Exception("SSL certificate verification failed")
        classified = classify_error(ssl_error)

        self.assertEqual(classified.error_type, ErrorType.SSL_ERROR)

    def test_dns_error_detection(self):
        """Test DNS error detection."""
        dns_error = Exception("Name resolution failed: getaddrinfo failed")
        classified = classify_error(dns_error)

        self.assertEqual(classified.error_type, ErrorType.DNS_ERROR)


if __name__ == '__main__':
    unittest.main()