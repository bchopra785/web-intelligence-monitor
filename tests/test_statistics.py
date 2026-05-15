"""
test_statistics.py
Unit tests for statistical aggregation and ranking.
"""

import unittest

from analysis.statistics import StatisticsAnalyzer


class TestStatisticsAnalyzer(unittest.TestCase):
    """Test statistical aggregation helpers."""

    def setUp(self):
        self.metrics = [
            {
                "url": "https://example.com/a",
                "name": "A",
                "category": "cat-1",
                "page_load_time_ms": 100,
                "is_success": True,
                "is_timeout": False,
                "is_ssl_error": False,
                "is_http_error": False,
            },
            {
                "url": "https://example.com/b",
                "name": "B",
                "category": "cat-1",
                "page_load_time_ms": 300,
                "is_success": True,
                "is_timeout": False,
                "is_ssl_error": False,
                "is_http_error": False,
            },
            {
                "url": "https://example.com/c",
                "name": "C",
                "category": "cat-2",
                "page_load_time_ms": None,
                "is_success": False,
                "is_timeout": False,
                "is_ssl_error": True,
                "is_http_error": False,
            },
        ]

    def test_aggregate_by_category(self):
        grouped = StatisticsAnalyzer.aggregate_by_category(self.metrics)

        self.assertIn("cat-1", grouped)
        self.assertIn("cat-2", grouped)
        self.assertEqual(len(grouped["cat-1"]), 2)
        self.assertEqual(len(grouped["cat-2"]), 1)

    def test_aggregate_by_site(self):
        grouped = StatisticsAnalyzer.aggregate_by_site(self.metrics)

        self.assertIn("https://example.com/a", grouped)
        self.assertIn("https://example.com/b", grouped)
        self.assertIn("https://example.com/c", grouped)

    def test_get_category_stats(self):
        grouped = StatisticsAnalyzer.aggregate_by_category(self.metrics)
        stats = StatisticsAnalyzer.get_category_stats(grouped["cat-1"])

        self.assertEqual(stats["total_measurements"], 2)
        self.assertEqual(stats["successful_measurements"], 2)
        self.assertAlmostEqual(stats["success_rate"], 1.0)
        self.assertIn("mean_load_time_ms", stats)

    def test_find_outliers(self):
        metrics = [
            {"url": "a", "name": "A", "category": "cat", "page_load_time_ms": 100, "is_success": True},
            {"url": "b", "name": "B", "category": "cat", "page_load_time_ms": 110, "is_success": True},
            {"url": "c", "name": "C", "category": "cat", "page_load_time_ms": 120, "is_success": True},
            {"url": "d", "name": "D", "category": "cat", "page_load_time_ms": 5000, "is_success": True},
        ]

        outliers = StatisticsAnalyzer.find_outliers(metrics, z_score_threshold=1.4)

        self.assertTrue(any(item["url"] == "d" for item in outliers))

    def test_compare_categories(self):
        grouped = StatisticsAnalyzer.aggregate_by_category(self.metrics)
        comparison = StatisticsAnalyzer.compare_categories(grouped)

        self.assertGreaterEqual(len(comparison), 2)
        self.assertEqual(comparison[0]["success_rate"], 1.0)


if __name__ == '__main__':
    unittest.main()