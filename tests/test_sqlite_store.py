"""
test_sqlite_store.py
Unit tests for SQLite persistence.
"""

import tempfile
import unittest
from pathlib import Path

from storage.sqlite_store import SQLiteStore


class TestSQLiteStore(unittest.TestCase):
    """Test SQLite persistence and SQL queries."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "web_intelligence_monitor.db"
        self.store = SQLiteStore(self.db_path)

        self.metrics = [
            {
                "url": "https://example.com/a",
                "name": "A",
                "category": "cat-1",
                "page_load_time_ms": 120,
                "dom_content_loaded_ms": 45,
                "time_to_first_byte_ms": 30,
                "http_status_code": 200,
                "response_size_bytes": 1234,
                "redirect_count": 0,
                "total_requests": 10,
                "failed_requests": 0,
                "blocked_requests": 0,
                "error_type": None,
                "error_message": None,
                "is_success": True,
                "is_timeout": False,
                "is_ssl_error": False,
                "is_http_error": False,
                "timestamp": "2026-05-20T12:00:00",
            },
            {
                "url": "https://example.com/b",
                "name": "B",
                "category": "cat-2",
                "page_load_time_ms": None,
                "dom_content_loaded_ms": None,
                "time_to_first_byte_ms": None,
                "http_status_code": None,
                "response_size_bytes": None,
                "redirect_count": 0,
                "total_requests": 0,
                "failed_requests": 0,
                "blocked_requests": 0,
                "error_type": "timeout",
                "error_message": "Page load timeout",
                "is_success": False,
                "is_timeout": True,
                "is_ssl_error": False,
                "is_http_error": False,
                "timestamp": "2026-05-20T12:00:01",
            },
        ]
        self.analysis = {
            "category_comparison": [
                {
                    "category": "cat-1",
                    "total_measurements": 1,
                    "successful_measurements": 1,
                    "failed_measurements": 0,
                    "success_rate": 1.0,
                    "mean_load_time_ms": 120,
                    "median_load_time_ms": 120,
                    "min_load_time_ms": 120,
                    "max_load_time_ms": 120,
                    "stdev_load_time_ms": 0.0,
                    "p95_load_time_ms": 120,
                    "p99_load_time_ms": 120,
                },
                {
                    "category": "cat-2",
                    "total_measurements": 1,
                    "successful_measurements": 0,
                    "failed_measurements": 1,
                    "success_rate": 0.0,
                    "mean_load_time_ms": None,
                    "median_load_time_ms": None,
                    "min_load_time_ms": None,
                    "max_load_time_ms": None,
                    "stdev_load_time_ms": None,
                    "p95_load_time_ms": None,
                    "p99_load_time_ms": None,
                },
            ]
        }

    def tearDown(self):
        self.store.close()
        self.temp_dir.cleanup()

    def test_save_pipeline_run_creates_rows(self):
        run_id = self.store.save_pipeline_run(
            run_timestamp="2026-05-20T12:00:00",
            metrics_list=self.metrics,
            analysis_results=self.analysis,
            analysis_path="data/processed/analysis.json",
            report_path="data/processed/report.txt",
        )

        self.assertIsInstance(run_id, int)

        summary = self.store.fetch_latest_run_summary()
        self.assertIsNotNone(summary)
        self.assertEqual(summary["website_count"], 2)
        self.assertEqual(summary["success_count"], 1)
        self.assertEqual(summary["failure_count"], 1)

    def test_sql_queries_return_results(self):
        self.store.save_pipeline_run(
            run_timestamp="2026-05-20T12:00:00",
            metrics_list=self.metrics,
            analysis_results=self.analysis,
            analysis_path="data/processed/analysis.json",
            report_path="data/processed/report.txt",
        )

        top_performers = self.store.fetch_top_performers(limit=5)
        self.assertEqual(len(top_performers), 2)
        self.assertEqual(top_performers[0]["url"], "https://example.com/a")

        category_summary = self.store.fetch_category_summary()
        self.assertEqual(len(category_summary), 2)
        self.assertEqual(category_summary[0]["category"], "cat-1")


if __name__ == '__main__':
    unittest.main()
