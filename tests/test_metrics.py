"""
test_metrics.py
Unit tests for metrics calculation and scoring logic.
"""

import unittest
from analysis.metrics import MetricsCalculator, PerformanceTier, ReliabilityTier


class TestMetricsCalculator(unittest.TestCase):
    """Test suite for metrics calculation."""
    
    def test_score_load_time_excellent(self):
        """Test scoring for excellent load time (<1000ms)."""
        score = MetricsCalculator.score_load_time(500)
        self.assertEqual(score, 100.0)
    
    def test_score_load_time_good(self):
        """Test scoring for good load time (1000-2000ms)."""
        score = MetricsCalculator.score_load_time(1500)
        self.assertGreater(score, 50)
        self.assertLess(score, 100)
    
    def test_score_load_time_fair(self):
        """Test scoring for fair load time (2000-4000ms)."""
        score = MetricsCalculator.score_load_time(3000)
        self.assertGreater(score, 25)
        self.assertLess(score, 76)
    
    def test_score_load_time_poor(self):
        """Test scoring for poor load time (4000+ms)."""
        score = MetricsCalculator.score_load_time(5000)
        self.assertLess(score, 25)
        self.assertGreaterEqual(score, 0)
    
    def test_performance_tier_excellent(self):
        """Test tier classification for excellent score."""
        tier = MetricsCalculator.get_performance_tier(95)
        self.assertEqual(tier, PerformanceTier.EXCELLENT.value)
    
    def test_performance_tier_good(self):
        """Test tier classification for good score."""
        tier = MetricsCalculator.get_performance_tier(75)
        self.assertEqual(tier, PerformanceTier.GOOD.value)
    
    def test_performance_tier_fair(self):
        """Test tier classification for fair score."""
        tier = MetricsCalculator.get_performance_tier(55)
        self.assertEqual(tier, PerformanceTier.FAIR.value)
    
    def test_performance_tier_poor(self):
        """Test tier classification for poor score."""
        tier = MetricsCalculator.get_performance_tier(25)
        self.assertEqual(tier, PerformanceTier.POOR.value)
    
    def test_consistency_score_perfect(self):
        """Test consistency scoring for identical load times."""
        load_times = [1000, 1000, 1000]
        score = MetricsCalculator.calculate_consistency_score(load_times)
        self.assertEqual(score, 100.0)
    
    def test_consistency_score_variable(self):
        """Test consistency scoring for variable load times."""
        load_times = [500, 1000, 1500, 2000]
        score = MetricsCalculator.calculate_consistency_score(load_times)
        self.assertGreater(score, 0)
        self.assertLess(score, 100)
    
    def test_consistency_score_single_measurement(self):
        """Test consistency scoring with single measurement."""
        load_times = [1000]
        score = MetricsCalculator.calculate_consistency_score(load_times)
        self.assertEqual(score, 100.0)
    
    def test_reliability_tier_highly_reliable(self):
        """Test reliability tier for high success rate."""
        tier = MetricsCalculator.get_reliability_tier(0.98)
        self.assertEqual(tier, ReliabilityTier.HIGHLY_RELIABLE.value)
    
    def test_reliability_tier_reliable(self):
        """Test reliability tier for good success rate."""
        tier = MetricsCalculator.get_reliability_tier(0.92)
        self.assertEqual(tier, ReliabilityTier.RELIABLE.value)
    
    def test_reliability_tier_adequate(self):
        """Test reliability tier for adequate success rate."""
        tier = MetricsCalculator.get_reliability_tier(0.80)
        self.assertEqual(tier, ReliabilityTier.ADEQUATE.value)
    
    def test_reliability_tier_unreliable(self):
        """Test reliability tier for low success rate."""
        tier = MetricsCalculator.get_reliability_tier(0.60)
        self.assertEqual(tier, ReliabilityTier.UNRELIABLE.value)
    
    def test_calculate_performance_score(self):
        """Test comprehensive performance score calculation."""
        load_times = [800, 1000, 1200, 950, 1100]
        score_data = MetricsCalculator.calculate_performance_score(
            load_times,
            successful_count=5,
            total_count=5
        )
        
        self.assertIsNotNone(score_data)
        self.assertIn("mean_load_time", score_data)
        self.assertIn("median_load_time", score_data)
        self.assertIn("p95_load_time", score_data)
        self.assertIn("p99_load_time", score_data)
        self.assertIn("overall_score", score_data)
    
    def test_calculate_performance_score_with_failures(self):
        """Test performance score with partial failures."""
        load_times = [800, 1000, 1200]
        score_data = MetricsCalculator.calculate_performance_score(
            load_times,
            successful_count=3,
            total_count=5
        )
        
        self.assertEqual(score_data["success_rate"], 0.6)
    
    def test_percentile_calculation(self):
        """Test percentile calculations."""
        load_times = list(range(1, 101))  # 1-100
        score_data = MetricsCalculator.calculate_performance_score(
            load_times,
            successful_count=100,
            total_count=100
        )
        
        # p95 should be around 95-96
        self.assertGreater(score_data["p95_load_time"], 90)
        self.assertLess(score_data["p95_load_time"], 100)
        
        # p99 should be around 99-100
        self.assertGreater(score_data["p99_load_time"], 95)
if __name__ == '__main__':
    unittest.main()
