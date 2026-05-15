"""
metrics.py
Metrics calculation and scoring logic for web measurement data.
"""

from typing import List, Dict, Any, Optional
import statistics
from dataclasses import dataclass
from enum import Enum


class PerformanceTier(Enum):
    """Performance classification tiers."""
    EXCELLENT = "excellent"  # < 1000 ms
    GOOD = "good"             # 1000-2000 ms
    FAIR = "fair"             # 2000-4000 ms
    POOR = "poor"             # 4000+ ms
    FAILED = "failed"         # Any failure


class ReliabilityTier(Enum):
    """Reliability classification tiers."""
    HIGHLY_RELIABLE = "highly-reliable"     # 95-100% success
    RELIABLE = "reliable"                   # 90-95% success
    ADEQUATE = "adequate"                   # 75-90% success
    UNRELIABLE = "unreliable"               # < 75% success


@dataclass
class PerformanceScore:
    """Calculated performance score for a website."""
    url: str
    name: str
    category: str
    
    # Timing scores (0-100)
    load_time_score: float
    consistency_score: float
    overall_performance_score: float
    
    # Performance tier
    performance_tier: str
    
    # Statistics
    mean_load_time_ms: float
    median_load_time_ms: float
    p95_load_time_ms: float
    p99_load_time_ms: float
    stdev_load_time_ms: float


@dataclass
class ReliabilityScore:
    """Calculated reliability score for a website."""
    url: str
    name: str
    category: str
    
    # Success metrics
    success_rate: float
    total_measurements: int
    successful_measurements: int
    failed_measurements: int
    
    # Error breakdown
    timeout_count: int
    ssl_error_count: int
    http_error_count: int
    other_error_count: int
    
    # Reliability tier
    reliability_tier: str
    overall_reliability_score: float


class MetricsCalculator:
    """Calculate performance and reliability scores."""
    
    @staticmethod
    def score_load_time(load_time_ms: float) -> float:
        """
        Convert load time to 0-100 score.
        Excellent (100) = < 1000ms
        Good (75) = 1000-2000ms
        Fair (50) = 2000-4000ms
        Poor (0) = 4000+ms
        """
        if load_time_ms < 1000:
            return 100.0
        elif load_time_ms < 2000:
            return 75.0 - ((load_time_ms - 1000) / 1000) * 25
        elif load_time_ms < 4000:
            return 50.0 - ((load_time_ms - 2000) / 2000) * 25
        else:
            return max(0.0, 25.0 - ((load_time_ms - 4000) / 4000) * 25)
    
    @staticmethod
    def get_performance_tier(score: float) -> str:
        """Get performance tier from score."""
        if score >= 85:
            return PerformanceTier.EXCELLENT.value
        elif score >= 70:
            return PerformanceTier.GOOD.value
        elif score >= 50:
            return PerformanceTier.FAIR.value
        else:
            return PerformanceTier.POOR.value
    
    @staticmethod
    def calculate_consistency_score(load_times: List[float]) -> float:
        """
        Calculate consistency score based on variance.
        Lower variance = higher consistency (100 = perfect consistency)
        Based on coefficient of variation normalized to 0-100 scale.
        """
        if len(load_times) < 2:
            return 100.0
        
        mean = statistics.mean(load_times)
        if mean == 0:
            return 100.0
        
        try:
            stdev = statistics.stdev(load_times)
            cv = stdev / mean  # Coefficient of variation
            
            # Normalize CV to 0-100 scale
            # CV of 0 = 100 (perfect consistency)
            # CV of 1.0 (100% variance) = 0
            consistency = max(0.0, 100.0 - (cv * 100))
            return consistency
        except:
            return 100.0
    
    @staticmethod
    def get_reliability_tier(success_rate: float) -> str:
        """Get reliability tier from success rate."""
        if success_rate >= 0.95:
            return ReliabilityTier.HIGHLY_RELIABLE.value
        elif success_rate >= 0.90:
            return ReliabilityTier.RELIABLE.value
        elif success_rate >= 0.75:
            return ReliabilityTier.ADEQUATE.value
        else:
            return ReliabilityTier.UNRELIABLE.value
    
    @staticmethod
    def calculate_performance_score(
        load_times: List[float],
        successful_count: int,
        total_count: int
    ) -> PerformanceScore:
        """
        Calculate comprehensive performance score.
        Factors: mean/median load time, consistency, success rate.
        """
        if not load_times:
            return None
        
        mean_time = statistics.mean(load_times)
        median_time = statistics.median(load_times)
        
        # Percentiles
        sorted_times = sorted(load_times)
        p95_idx = int(len(sorted_times) * 0.95)
        p99_idx = int(len(sorted_times) * 0.99)
        p95_time = sorted_times[p95_idx] if p95_idx < len(sorted_times) else sorted_times[-1]
        p99_time = sorted_times[p99_idx] if p99_idx < len(sorted_times) else sorted_times[-1]
        
        stdev_time = statistics.stdev(load_times) if len(load_times) > 1 else 0.0
        
        # Calculate scores
        load_score = MetricsCalculator.score_load_time(mean_time)
        consistency = MetricsCalculator.calculate_consistency_score(load_times)
        
        # Combined performance score (70% load time, 30% consistency)
        overall_score = (load_score * 0.7) + (consistency * 0.3)
        
        return {
            "mean_load_time": mean_time,
            "median_load_time": median_time,
            "p95_load_time": p95_time,
            "p99_load_time": p99_time,
            "stdev_load_time": stdev_time,
            "load_score": load_score,
            "consistency_score": consistency,
            "overall_score": overall_score,
            "performance_tier": MetricsCalculator.get_performance_tier(overall_score),
            "success_rate": successful_count / total_count if total_count > 0 else 0.0
        }
    
    @staticmethod
    def calculate_reliability_score(
        metrics_list: List[Dict[str, Any]],
        url: str,
        name: str,
        category: str
    ) -> ReliabilityScore:
        """Calculate reliability score from metrics."""
        total = len(metrics_list)
        successful = sum(1 for m in metrics_list if m.get("is_success", False))
        failed = total - successful
        
        # Count error types
        timeout_count = sum(1 for m in metrics_list if m.get("is_timeout", False))
        ssl_error_count = sum(1 for m in metrics_list if m.get("is_ssl_error", False))
        http_error_count = sum(1 for m in metrics_list if m.get("is_http_error", False))
        other_error_count = failed - timeout_count - ssl_error_count - http_error_count
        
        success_rate = successful / total if total > 0 else 0.0
        reliability_score = success_rate * 100  # Convert to 0-100
        
        return ReliabilityScore(
            url=url,
            name=name,
            category=category,
            success_rate=success_rate,
            total_measurements=total,
            successful_measurements=successful,
            failed_measurements=failed,
            timeout_count=timeout_count,
            ssl_error_count=ssl_error_count,
            http_error_count=http_error_count,
            other_error_count=other_error_count,
            reliability_tier=MetricsCalculator.get_reliability_tier(success_rate),
            overall_reliability_score=reliability_score
        )
