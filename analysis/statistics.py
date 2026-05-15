"""
statistics.py
Statistical analysis and aggregation of measurement data.
"""

from typing import List, Dict, Any, Tuple
import statistics
from collections import defaultdict


class StatisticsAnalyzer:
    """Analyze and aggregate measurement statistics."""
    
    @staticmethod
    def aggregate_by_category(
        metrics_list: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group metrics by category."""
        by_category = defaultdict(list)
        for metrics in metrics_list:
            category = metrics.get("category", "unknown")
            by_category[category].append(metrics)
        return dict(by_category)
    
    @staticmethod
    def aggregate_by_site(
        metrics_list: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group metrics by website URL."""
        by_site = defaultdict(list)
        for metrics in metrics_list:
            url = metrics.get("url", "unknown")
            by_site[url].append(metrics)
        return dict(by_site)
    
    @staticmethod
    def get_category_stats(
        category_metrics: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate statistics for a category."""
        if not category_metrics:
            return None
        
        # Get load times (only successful measurements)
        load_times = [
            m.get("page_load_time_ms")
            for m in category_metrics
            if m.get("is_success") and m.get("page_load_time_ms") is not None
        ]
        
        # Success statistics
        total = len(category_metrics)
        successful = sum(1 for m in category_metrics if m.get("is_success", False))
        success_rate = successful / total if total > 0 else 0.0
        
        stats = {
            "total_measurements": total,
            "successful_measurements": successful,
            "failed_measurements": total - successful,
            "success_rate": success_rate,
        }
        
        if load_times:
            stats.update({
                "mean_load_time_ms": statistics.mean(load_times),
                "median_load_time_ms": statistics.median(load_times),
                "min_load_time_ms": min(load_times),
                "max_load_time_ms": max(load_times),
                "stdev_load_time_ms": statistics.stdev(load_times) if len(load_times) > 1 else 0.0,
            })
            
            # Percentiles
            sorted_times = sorted(load_times)
            stats["p95_load_time_ms"] = sorted_times[int(len(sorted_times) * 0.95)]
            stats["p99_load_time_ms"] = sorted_times[int(len(sorted_times) * 0.99)]
        
        return stats
    
    @staticmethod
    def find_outliers(
        metrics_list: List[Dict[str, Any]],
        z_score_threshold: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Identify statistical outliers based on load time.
        Uses z-score method with configurable threshold.
        """
        load_times = [
            m.get("page_load_time_ms")
            for m in metrics_list
            if m.get("is_success") and m.get("page_load_time_ms") is not None
        ]
        
        if len(load_times) < 2:
            return []
        
        mean = statistics.mean(load_times)
        stdev = statistics.stdev(load_times)
        
        if stdev == 0:
            return []
        
        outliers = []
        for metrics in metrics_list:
            load_time = metrics.get("page_load_time_ms")
            if load_time is None or not metrics.get("is_success"):
                continue
            
            z_score = abs((load_time - mean) / stdev)
            if z_score > z_score_threshold:
                outliers.append({
                    "url": metrics.get("url"),
                    "name": metrics.get("name"),
                    "load_time_ms": load_time,
                    "z_score": z_score,
                    "deviation": load_time - mean
                })
        
        return sorted(outliers, key=lambda x: abs(x["z_score"]), reverse=True)
    
    @staticmethod
    def get_reliability_breakdown(
        category_metrics: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Count error types in a category."""
        breakdown = {
            "timeouts": sum(1 for m in category_metrics if m.get("is_timeout", False)),
            "ssl_errors": sum(1 for m in category_metrics if m.get("is_ssl_error", False)),
            "http_errors": sum(1 for m in category_metrics if m.get("is_http_error", False)),
            "unknown_errors": sum(
                1 for m in category_metrics
                if not m.get("is_success") and not any([
                    m.get("is_timeout"),
                    m.get("is_ssl_error"),
                    m.get("is_http_error")
                ])
            )
        }
        return breakdown
    
    @staticmethod
    def compare_categories(
        aggregated_by_category: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Compare performance across categories."""
        comparison = []
        
        for category, metrics_list in aggregated_by_category.items():
            stats = StatisticsAnalyzer.get_category_stats(metrics_list)
            if stats:
                stats["category"] = category
                comparison.append(stats)
        
        # Sort by success rate, then by mean load time
        return sorted(
            comparison,
            key=lambda x: (-x.get("success_rate", 0), x.get("mean_load_time_ms", float("inf")))
        )
    
    @staticmethod
    def get_performance_ranking(
        site_metrics_aggregated: Dict[str, List[Dict[str, Any]]]
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Rank websites by performance.
        Returns list of (url, stats) tuples sorted by performance.
        """
        rankings = []
        
        for url, metrics_list in site_metrics_aggregated.items():
            stats = StatisticsAnalyzer.get_category_stats(metrics_list)
            if stats:
                # Performance score: 70% success rate, 30% speed
                success_score = stats.get("success_rate", 0) * 100
                
                # Normalize load time to 0-100 (target: 1000ms = 100)
                mean_load = stats.get("mean_load_time_ms", 5000)
                speed_score = max(0, 100 - (mean_load / 1000 * 50))
                
                performance_score = (success_score * 0.7) + (speed_score * 0.3)
                stats["performance_score"] = performance_score
                
                # Get first site name from metrics
                site_name = metrics_list[0].get("name", url) if metrics_list else url
                
                rankings.append((site_name, url, stats))
        
        return sorted(rankings, key=lambda x: x[2].get("performance_score", 0), reverse=True)
