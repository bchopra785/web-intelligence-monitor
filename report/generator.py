"""
generator.py
Automated report generation from collected measurement data.
"""

from typing import List, Dict, Any
from datetime import datetime
from analysis.statistics import StatisticsAnalyzer
from analysis.metrics import MetricsCalculator


class ReportGenerator:
    """Generate text-based research-style reports from measurement data."""
    
    def __init__(self, title: str = "Web Intelligence Monitor - Measurement Report"):
        self.title = title
        self.timestamp = datetime.utcnow()
        self.metrics_list: List[Dict[str, Any]] = []
    
    def load_metrics(self, metrics_list: List[Dict[str, Any]]):
        """Load metrics data for report generation."""
        self.metrics_list = metrics_list
    
    def generate_report(self) -> str:
        """Generate complete report."""
        sections = []
        
        # Header
        sections.append(self._generate_header())
        
        # Executive summary
        sections.append(self._generate_executive_summary())
        
        # Overall statistics
        sections.append(self._generate_overall_statistics())
        
        # Category analysis
        sections.append(self._generate_category_analysis())
        
        # Top performers
        sections.append(self._generate_top_performers())
        
        # Bottom performers
        sections.append(self._generate_bottom_performers())
        
        # Anomalies and risk flags
        sections.append(self._generate_anomalies())
        
        # Reliability analysis
        sections.append(self._generate_reliability_analysis())

        # Blocked or failed access cases
        sections.append(self._generate_access_issues())
        
        # Conclusions and recommendations
        sections.append(self._generate_conclusions())
        
        # Footer
        sections.append(self._generate_footer())
        
        return "\n\n".join(sections)
    
    def _generate_header(self) -> str:
        """Generate report header."""
        lines = [
            "=" * 80,
            self.title.center(80),
            "=" * 80,
            f"Generated: {self.timestamp.isoformat()}",
            f"Total Websites Measured: {len(set(m['url'] for m in self.metrics_list))}",
            f"Total Measurements: {len(self.metrics_list)}",
            "=" * 80,
        ]
        return "\n".join(lines)
    
    def _generate_executive_summary(self) -> str:
        """Generate executive summary."""
        if not self.metrics_list:
            return "No data available for analysis."
        
        total_measurements = len(self.metrics_list)
        successful_measurements = sum(1 for m in self.metrics_list if m.get("is_success", False))
        success_rate = (successful_measurements / total_measurements * 100) if total_measurements > 0 else 0
        
        # Get load times
        load_times = [
            m.get("page_load_time_ms")
            for m in self.metrics_list
            if m.get("is_success") and m.get("page_load_time_ms") is not None
        ]
        
        avg_load_time = sum(load_times) / len(load_times) if load_times else 0
        
        lines = [
            "EXECUTIVE SUMMARY",
            "-" * 80,
            f"Overall Success Rate:        {success_rate:.1f}%",
            f"Average Load Time:           {avg_load_time:.0f}ms",
            f"Total Successful Measures:   {successful_measurements}/{total_measurements}",
            f"Failed Measurements:         {total_measurements - successful_measurements}",
        ]
        
        # Error summary
        timeouts = sum(1 for m in self.metrics_list if m.get("is_timeout", False))
        ssl_errors = sum(1 for m in self.metrics_list if m.get("is_ssl_error", False))
        http_errors = sum(1 for m in self.metrics_list if m.get("is_http_error", False))
        
        if timeouts > 0:
            lines.append(f"Timeouts:                    {timeouts}")
        if ssl_errors > 0:
            lines.append(f"SSL/TLS Errors:              {ssl_errors}")
        if http_errors > 0:
            lines.append(f"HTTP Errors:                 {http_errors}")
        
        return "\n".join(lines)
    
    def _generate_overall_statistics(self) -> str:
        """Generate overall statistics."""
        stats = StatisticsAnalyzer.get_category_stats(self.metrics_list)
        
        if not stats:
            return "No statistics available."
        
        lines = [
            "OVERALL STATISTICS",
            "-" * 80,
            f"Mean Load Time:              {stats.get('mean_load_time_ms', 0):.0f}ms",
            f"Median Load Time:            {stats.get('median_load_time_ms', 0):.0f}ms",
            f"Min Load Time:               {stats.get('min_load_time_ms', 0):.0f}ms",
            f"Max Load Time:               {stats.get('max_load_time_ms', 0):.0f}ms",
            f"Standard Deviation:          {stats.get('stdev_load_time_ms', 0):.0f}ms",
            f"95th Percentile (p95):       {stats.get('p95_load_time_ms', 0):.0f}ms",
            f"99th Percentile (p99):       {stats.get('p99_load_time_ms', 0):.0f}ms",
        ]
        
        return "\n".join(lines)
    
    def _generate_category_analysis(self) -> str:
        """Generate analysis by category."""
        aggregated = StatisticsAnalyzer.aggregate_by_category(self.metrics_list)
        comparison = StatisticsAnalyzer.compare_categories(aggregated)
        
        if not comparison:
            return "No category data available."
        
        lines = [
            "ANALYSIS BY CATEGORY",
            "-" * 80,
            ""
        ]
        
        for category_stats in comparison:
            category = category_stats.get("category", "unknown")
            success = category_stats.get("success_rate", 0) * 100
            mean_load = category_stats.get("mean_load_time_ms", 0)
            
            lines.append(f"{category.upper()}")
            lines.append(f"  Success Rate: {success:.1f}%")
            lines.append(f"  Mean Load Time: {mean_load:.0f}ms")
            lines.append(f"  Measurements: {category_stats.get('total_measurements', 0)}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_top_performers(self) -> str:
        """Generate list of top performing websites."""
        site_aggregated = StatisticsAnalyzer.aggregate_by_site(self.metrics_list)
        rankings = StatisticsAnalyzer.get_performance_ranking(site_aggregated)
        
        if not rankings:
            return "No ranking data available."
        
        # Top 10
        top_10 = rankings[:10]
        
        lines = [
            "TOP 10 PERFORMING WEBSITES",
            "-" * 80,
        ]
        
        for i, (name, url, stats) in enumerate(top_10, 1):
            perf_score = stats.get("performance_score", 0)
            success_rate = stats.get("success_rate", 0) * 100
            mean_load = stats.get("mean_load_time_ms", 0)
            
            lines.append(f"{i:2d}. {name}")
            lines.append(f"    URL: {url}")
            lines.append(f"    Performance Score: {perf_score:.1f}/100")
            lines.append(f"    Success Rate: {success_rate:.1f}%")
            lines.append(f"    Mean Load Time: {mean_load:.0f}ms")
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_bottom_performers(self) -> str:
        """Generate list of bottom performing websites."""
        site_aggregated = StatisticsAnalyzer.aggregate_by_site(self.metrics_list)
        rankings = StatisticsAnalyzer.get_performance_ranking(site_aggregated)
        
        if not rankings:
            return "No ranking data available."
        
        # Bottom 10
        bottom_10 = rankings[-10:][::-1]  # Reverse to show worst first
        
        lines = [
            "BOTTOM 10 PERFORMING WEBSITES (REQUIRES ATTENTION)",
            "-" * 80,
        ]
        
        for i, (name, url, stats) in enumerate(bottom_10, 1):
            perf_score = stats.get("performance_score", 0)
            success_rate = stats.get("success_rate", 0) * 100
            mean_load = stats.get("mean_load_time_ms", 0)
            
            lines.append(f"{i:2d}. {name} ⚠️ ")
            lines.append(f"    URL: {url}")
            lines.append(f"    Performance Score: {perf_score:.1f}/100")
            lines.append(f"    Success Rate: {success_rate:.1f}%")
            lines.append(f"    Mean Load Time: {mean_load:.0f}ms")
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_anomalies(self) -> str:
        """Generate anomalies and risk flags."""
        outliers = StatisticsAnalyzer.find_outliers(self.metrics_list, z_score_threshold=2.0)
        
        lines = [
            "ANOMALIES & RISK FLAGS",
            "-" * 80,
        ]
        
        if outliers:
            lines.append(f"Found {len(outliers)} statistical outliers (load time > 2 std deviations):\n")
            for outlier in outliers[:10]:  # Show top 10
                name = outlier.get("name", outlier.get("url"))
                lines.append(f"  ⚠️  {name}")
                lines.append(f"      Load Time: {outlier['load_time_ms']:.0f}ms")
                lines.append(f"      Z-Score: {outlier['z_score']:.2f}")
                lines.append(f"      Above Mean By: {outlier['deviation']:.0f}ms")
                lines.append("")
        else:
            lines.append("No significant outliers detected.\n")
        
        return "\n".join(lines)
    
    def _generate_reliability_analysis(self) -> str:
        """Generate reliability analysis."""
        aggregated = StatisticsAnalyzer.aggregate_by_category(self.metrics_list)
        
        lines = [
            "RELIABILITY ANALYSIS BY CATEGORY",
            "-" * 80,
            ""
        ]
        
        for category in sorted(aggregated.keys()):
            metrics = aggregated[category]
            breakdown = StatisticsAnalyzer.get_reliability_breakdown(metrics)
            
            lines.append(f"{category.upper()}")
            lines.append(f"  Timeouts: {breakdown['timeouts']}")
            lines.append(f"  SSL/TLS Errors: {breakdown['ssl_errors']}")
            lines.append(f"  HTTP Errors: {breakdown['http_errors']}")
            lines.append(f"  Other Errors: {breakdown['unknown_errors']}")
            lines.append("")
        
        return "\n".join(lines)

    def _generate_access_issues(self) -> str:
        """Generate a focused summary of websites that failed to load or were blocked."""
        blocked_sites = [
            m for m in self.metrics_list
            if not m.get("is_success", False)
        ]

        lines = [
            "BLOCKED / FAILED ACCESS CASES",
            "-" * 80,
        ]

        if not blocked_sites:
            lines.append("No blocked or failed access cases were observed.")
            return "\n".join(lines)

        lines.append(
            "These sites are kept in the dataset on purpose to document access restrictions, "
            "security controls, or automation-blocking behavior."
        )
        lines.append("")

        for site in blocked_sites:
            name = site.get("name", site.get("url", "unknown"))
            url = site.get("url", "unknown")
            error_type = site.get("error_type") or "unknown"
            error_message = site.get("error_message") or "No additional error message captured."

            lines.append(f"• {name}")
            lines.append(f"  URL: {url}")
            lines.append(f"  Error Type: {error_type}")
            lines.append(f"  Details: {error_message}")
            lines.append("")

        return "\n".join(lines)
    
    def _generate_conclusions(self) -> str:
        """Generate conclusions and recommendations."""
        site_aggregated = StatisticsAnalyzer.aggregate_by_site(self.metrics_list)
        rankings = StatisticsAnalyzer.get_performance_ranking(site_aggregated)
        
        lines = [
            "CONCLUSIONS & RECOMMENDATIONS",
            "-" * 80,
            ""
        ]
        
        # Overall health
        total_measurements = len(self.metrics_list)
        successful = sum(1 for m in self.metrics_list if m.get("is_success", False))
        success_rate = (successful / total_measurements * 100) if total_measurements > 0 else 0
        
        if success_rate >= 95:
            lines.append("✓ Web Ecosystem Shows Strong Overall Reliability (≥95% success rate)")
        elif success_rate >= 90:
            lines.append("✓ Web Ecosystem Shows Good Overall Reliability (≥90% success rate)")
        elif success_rate >= 75:
            lines.append("⚠️  Web Ecosystem Shows Adequate Reliability (≥75% success rate)")
        else:
            lines.append("✗ Web Ecosystem Shows Poor Overall Reliability (<75% success rate)")
        
        lines.append("")
        lines.append("Key Findings:")
        
        # Load time insights
        load_times = [
            m.get("page_load_time_ms")
            for m in self.metrics_list
            if m.get("is_success") and m.get("page_load_time_ms") is not None
        ]
        avg_load = sum(load_times) / len(load_times) if load_times else 0
        
        if avg_load < 2000:
            lines.append("  • Most websites load quickly (<2s average)")
        elif avg_load < 4000:
            lines.append("  • Average websites load in 2-4 seconds")
        else:
            lines.append("  • Website performance is degraded (>4s average)")
        
        # Top performers
        if rankings:
            top_site = rankings[0]
            lines.append(f"  • Top performer: {top_site[0]} ({top_site[2].get('performance_score', 0):.0f}/100)")
        
        # Bottom performers
        if rankings and len(rankings) > 1:
            bottom_site = rankings[-1]
            lines.append(f"  • Requires attention: {bottom_site[0]} ({bottom_site[2].get('performance_score', 0):.0f}/100)")

        blocked_sites = [m for m in self.metrics_list if not m.get("is_success", False)]
        if blocked_sites:
            lines.append(
                f"  • Blocked or failed access cases documented separately: {len(blocked_sites)} site(s)"
            )
        
        lines.append("")
        lines.append("Recommendations:")
        lines.append("  1. Monitor websites with performance_score < 50")
        lines.append("  2. Investigate SSL/TLS failures")
        lines.append("  3. Consider caching strategies for slow-loading sites")
        lines.append("  4. Re-test high-latency outliers")
        
        return "\n".join(lines)
    
    def _generate_footer(self) -> str:
        """Generate report footer."""
        lines = [
            "=" * 80,
            "End of Report",
            "=" * 80,
            "This report was automatically generated by Web Intelligence Monitor.",
            "For more information, visit the project repository.",
        ]
        return "\n".join(lines)
