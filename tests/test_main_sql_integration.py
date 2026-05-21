"""
test_main_sql_integration.py
Unit tests for SQL persistence wiring in the main pipeline.
"""

import tempfile
import unittest
from pathlib import Path

from main import WebIntelligenceMonitor
from storage.sqlite_store import SQLiteStore


class TestMainSQLiteIntegration(unittest.TestCase):
    """Test that the main pipeline can persist results to SQLite."""

    def test_save_sqlite_results_wires_through_main(self):
        monitor = WebIntelligenceMonitor()

        with tempfile.TemporaryDirectory() as temp_dir:
            monitor.database_path = Path(temp_dir) / "integration.db"

            metrics_list = [
                {
                    "url": "https://example.com",
                    "name": "Example",
                    "category": "cat-1",
                    "page_load_time_ms": 100,
                    "dom_content_loaded_ms": 40,
                    "time_to_first_byte_ms": 20,
                    "http_status_code": 200,
                    "response_size_bytes": 1000,
                    "redirect_count": 0,
                    "total_requests": 5,
                    "failed_requests": 0,
                    "blocked_requests": 0,
                    "error_type": None,
                    "error_message": None,
                    "is_success": True,
                    "is_timeout": False,
                    "is_ssl_error": False,
                    "is_http_error": False,
                    "timestamp": "2026-05-20T12:00:00",
                }
            ]
            analysis = {
                "category_comparison": [
                    {
                        "category": "cat-1",
                        "total_measurements": 1,
                        "successful_measurements": 1,
                        "failed_measurements": 0,
                        "success_rate": 1.0,
                        "mean_load_time_ms": 100,
                        "median_load_time_ms": 100,
                        "min_load_time_ms": 100,
                        "max_load_time_ms": 100,
                        "stdev_load_time_ms": 0.0,
                        "p95_load_time_ms": 100,
                        "p99_load_time_ms": 100,
                    }
                ]
            }

            database_path = monitor.save_sqlite_results(
                metrics_list=metrics_list,
                analysis=analysis,
                analysis_path="data/processed/analysis.json",
                report_path="data/processed/report.txt",
            )

            self.assertEqual(Path(database_path), monitor.database_path)
            self.assertTrue(Path(database_path).exists())

            store = SQLiteStore(database_path)
            try:
                summary = store.fetch_latest_run_summary()
                self.assertIsNotNone(summary)
                self.assertEqual(summary["website_count"], 1)
                self.assertEqual(summary["success_count"], 1)
                self.assertEqual(summary["failure_count"], 0)
            finally:
                store.close()


if __name__ == '__main__':
    unittest.main()
