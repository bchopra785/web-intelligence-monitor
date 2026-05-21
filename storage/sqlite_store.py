"""
sqlite_store.py
SQLite persistence for pipeline runs, measurements, and summary analytics.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional


class SQLiteStore:
    """Persist pipeline runs and derived analytics into a SQLite database."""

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(self.db_path))
        self.connection.row_factory = sqlite3.Row
        self.ensure_schema()

    def close(self) -> None:
        """Close the database connection."""
        if self.connection:
            self.connection.close()

    def ensure_schema(self) -> None:
        """Create tables if they do not already exist."""
        cursor = self.connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS runs (
                run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_timestamp TEXT NOT NULL,
                website_count INTEGER NOT NULL,
                success_count INTEGER NOT NULL,
                failure_count INTEGER NOT NULL,
                average_load_time_ms REAL,
                median_load_time_ms REAL,
                min_load_time_ms REAL,
                max_load_time_ms REAL,
                analysis_path TEXT,
                report_path TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS measurements (
                measurement_id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL,
                url TEXT NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                page_load_time_ms REAL,
                dom_content_loaded_ms REAL,
                time_to_first_byte_ms REAL,
                http_status_code INTEGER,
                response_size_bytes INTEGER,
                redirect_count INTEGER,
                total_requests INTEGER,
                failed_requests INTEGER,
                blocked_requests INTEGER,
                error_type TEXT,
                error_message TEXT,
                is_success INTEGER,
                is_timeout INTEGER,
                is_ssl_error INTEGER,
                is_http_error INTEGER,
                timestamp TEXT,
                FOREIGN KEY (run_id) REFERENCES runs (run_id)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS category_summary (
                category_summary_id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                total_measurements INTEGER NOT NULL,
                successful_measurements INTEGER NOT NULL,
                failed_measurements INTEGER NOT NULL,
                success_rate REAL NOT NULL,
                mean_load_time_ms REAL,
                median_load_time_ms REAL,
                min_load_time_ms REAL,
                max_load_time_ms REAL,
                stdev_load_time_ms REAL,
                p95_load_time_ms REAL,
                p99_load_time_ms REAL,
                FOREIGN KEY (run_id) REFERENCES runs (run_id)
            )
            """
        )
        self.connection.commit()

    def save_pipeline_run(
        self,
        run_timestamp: str,
        metrics_list: List[Dict[str, Any]],
        analysis_results: Dict[str, Any],
        analysis_path: Optional[str] = None,
        report_path: Optional[str] = None,
    ) -> int:
        """Persist a complete pipeline run and return the SQLite run id."""
        summary = self._build_run_summary(metrics_list)
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO runs (
                run_timestamp,
                website_count,
                success_count,
                failure_count,
                average_load_time_ms,
                median_load_time_ms,
                min_load_time_ms,
                max_load_time_ms,
                analysis_path,
                report_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_timestamp,
                summary["website_count"],
                summary["success_count"],
                summary["failure_count"],
                summary["average_load_time_ms"],
                summary["median_load_time_ms"],
                summary["min_load_time_ms"],
                summary["max_load_time_ms"],
                analysis_path,
                report_path,
            ),
        )
        run_id = cursor.lastrowid

        for metric in metrics_list:
            cursor.execute(
                """
                INSERT INTO measurements (
                    run_id,
                    url,
                    name,
                    category,
                    page_load_time_ms,
                    dom_content_loaded_ms,
                    time_to_first_byte_ms,
                    http_status_code,
                    response_size_bytes,
                    redirect_count,
                    total_requests,
                    failed_requests,
                    blocked_requests,
                    error_type,
                    error_message,
                    is_success,
                    is_timeout,
                    is_ssl_error,
                    is_http_error,
                    timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    metric.get("url"),
                    metric.get("name"),
                    metric.get("category"),
                    metric.get("page_load_time_ms"),
                    metric.get("dom_content_loaded_ms"),
                    metric.get("time_to_first_byte_ms"),
                    metric.get("http_status_code"),
                    metric.get("response_size_bytes"),
                    metric.get("redirect_count"),
                    metric.get("total_requests"),
                    metric.get("failed_requests"),
                    metric.get("blocked_requests"),
                    metric.get("error_type"),
                    metric.get("error_message"),
                    1 if metric.get("is_success") else 0,
                    1 if metric.get("is_timeout") else 0,
                    1 if metric.get("is_ssl_error") else 0,
                    1 if metric.get("is_http_error") else 0,
                    metric.get("timestamp"),
                ),
            )

        for category_stats in analysis_results.get("category_comparison", []):
            cursor.execute(
                """
                INSERT INTO category_summary (
                    run_id,
                    category,
                    total_measurements,
                    successful_measurements,
                    failed_measurements,
                    success_rate,
                    mean_load_time_ms,
                    median_load_time_ms,
                    min_load_time_ms,
                    max_load_time_ms,
                    stdev_load_time_ms,
                    p95_load_time_ms,
                    p99_load_time_ms
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    category_stats.get("category"),
                    category_stats.get("total_measurements", 0),
                    category_stats.get("successful_measurements", 0),
                    category_stats.get("failed_measurements", 0),
                    category_stats.get("success_rate", 0.0),
                    category_stats.get("mean_load_time_ms"),
                    category_stats.get("median_load_time_ms"),
                    category_stats.get("min_load_time_ms"),
                    category_stats.get("max_load_time_ms"),
                    category_stats.get("stdev_load_time_ms"),
                    category_stats.get("p95_load_time_ms"),
                    category_stats.get("p99_load_time_ms"),
                ),
            )

        self.connection.commit()
        return int(run_id)

    def fetch_latest_run_summary(self) -> Optional[Dict[str, Any]]:
        """Return the most recent pipeline run summary."""
        cursor = self.connection.cursor()
        row = cursor.execute(
            """
            SELECT run_id, run_timestamp, website_count, success_count, failure_count,
                   average_load_time_ms, median_load_time_ms, min_load_time_ms,
                   max_load_time_ms, analysis_path, report_path, created_at
            FROM runs
            ORDER BY run_id DESC
            LIMIT 1
            """
        ).fetchone()
        return dict(row) if row else None

    def fetch_top_performers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Return top performers using SQL aggregation."""
        cursor = self.connection.cursor()
        rows = cursor.execute(
            """
            SELECT
                url,
                MAX(name) AS name,
                MAX(category) AS category,
                ROUND(AVG(page_load_time_ms), 2) AS mean_load_time_ms,
                ROUND(AVG(CASE WHEN is_success = 1 THEN 100.0 ELSE 0.0 END), 2) AS success_rate,
                COUNT(*) AS measurement_count
            FROM measurements
            GROUP BY url
            HAVING COUNT(*) > 0
            ORDER BY success_rate DESC, mean_load_time_ms ASC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]

    def fetch_category_summary(self, run_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return category summary rows for the latest or specified run."""
        cursor = self.connection.cursor()
        if run_id is None:
            row = cursor.execute(
                "SELECT run_id FROM runs ORDER BY run_id DESC LIMIT 1"
            ).fetchone()
            if row is None:
                return []
            run_id = row[0]

        rows = cursor.execute(
            """
            SELECT category, total_measurements, successful_measurements, failed_measurements,
                   success_rate, mean_load_time_ms, median_load_time_ms, min_load_time_ms,
                   max_load_time_ms, stdev_load_time_ms, p95_load_time_ms, p99_load_time_ms
            FROM category_summary
            WHERE run_id = ?
            ORDER BY success_rate DESC, mean_load_time_ms ASC
            """,
            (run_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def _build_run_summary(metrics_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build a compact summary for storage."""
        website_count = len(metrics_list)
        success_count = sum(1 for metric in metrics_list if metric.get("is_success", False))
        failure_count = website_count - success_count
        load_times = [
            metric.get("page_load_time_ms")
            for metric in metrics_list
            if metric.get("is_success") and metric.get("page_load_time_ms") is not None
        ]

        if load_times:
            load_times_sorted = sorted(load_times)
            median_index = len(load_times_sorted) // 2
            if len(load_times_sorted) % 2 == 0:
                median_value = (load_times_sorted[median_index - 1] + load_times_sorted[median_index]) / 2
            else:
                median_value = load_times_sorted[median_index]
            average_load_time_ms = sum(load_times) / len(load_times)
            min_load_time_ms = min(load_times)
            max_load_time_ms = max(load_times)
        else:
            median_value = None
            average_load_time_ms = None
            min_load_time_ms = None
            max_load_time_ms = None

        return {
            "website_count": website_count,
            "success_count": success_count,
            "failure_count": failure_count,
            "average_load_time_ms": average_load_time_ms,
            "median_load_time_ms": median_value,
            "min_load_time_ms": min_load_time_ms,
            "max_load_time_ms": max_load_time_ms,
        }
