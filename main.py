"""
main.py
Main entry point for the Web Intelligence Monitor pipeline.
Orchestrates: data collection → analysis → report generation.
"""

import asyncio
import json
import csv
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging

from crawler import BrowserAutomation, WebsiteSession
from analysis.statistics import StatisticsAnalyzer
from report.generator import ReportGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WebIntelligenceMonitor:
    """Main application controller."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.data_dir = self.project_root / "data"
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        self.websites_file = self.data_dir / "websites.json"
        
        # Create directories if they don't exist
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        self.timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    def load_websites(self) -> list:
        """Load predefined website list from JSON."""
        try:
            with open(self.websites_file, 'r') as f:
                data = json.load(f)
            websites = data.get("websites", [])
            logger.info(f"Loaded {len(websites)} websites")
            return websites
        except Exception as e:
            logger.error(f"Failed to load websites: {e}")
            return []
    
    async def collect_measurements(
        self,
        websites: list,
        timeout_ms: int = 30000
    ) -> list:
        """
        Collect measurements from all websites.
        
        Args:
            websites: List of website configurations
            timeout_ms: Page load timeout in milliseconds
            
        Returns:
            List of measured sessions
        """
        browser = BrowserAutomation(timeout_ms=timeout_ms, headless=True)
        
        try:
            await browser.initialize()
            
            # Create sessions
            sessions = [
                WebsiteSession(
                    url=site["url"],
                    name=site.get("name", site["url"]),
                    category=site.get("category", "unknown")
                )
                for site in websites
            ]
            
            # Measure all
            logger.info(f"Starting measurements ({len(sessions)} sites)...")
            measured_sessions = await browser.measure_batch(sessions)
            
            logger.info(f"Measurement complete. Success: {sum(1 for s in measured_sessions if s.metrics.is_success)}/{len(measured_sessions)}")
            
            return measured_sessions
        
        finally:
            await browser.close()
    
    def save_raw_measurements(self, sessions: list) -> str:
        """
        Save raw measurements to CSV.
        
        Args:
            sessions: List of measured WebsiteSession objects
            
        Returns:
            Path to saved CSV file
        """
        # Convert to dictionaries
        metrics_list = [s.metrics.to_dict() for s in sessions]
        
        # Create DataFrame
        df = pd.DataFrame(metrics_list)
        
        # Save to CSV
        csv_path = self.raw_dir / f"raw_measurements_{self.timestamp}.csv"
        df.to_csv(csv_path, index=False)
        
        # Also save as JSON for reference
        json_path = self.raw_dir / f"raw_measurements_{self.timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(metrics_list, f, indent=2)
        
        logger.info(f"Raw measurements saved: {csv_path}")
        logger.info(f"Raw measurements saved: {json_path}")
        
        return str(csv_path)
    
    def analyze_measurements(self, metrics_list: list) -> dict:
        """Perform analysis on measurements."""
        
        logger.info("Running analysis...")
        
        # Get aggregations
        by_category = StatisticsAnalyzer.aggregate_by_category(metrics_list)
        by_site = StatisticsAnalyzer.aggregate_by_site(metrics_list)
        
        # Get category comparison
        category_comparison = StatisticsAnalyzer.compare_categories(by_category)
        
        # Get site rankings
        site_rankings = StatisticsAnalyzer.get_performance_ranking(by_site)
        
        # Find outliers
        outliers = StatisticsAnalyzer.find_outliers(metrics_list)
        
        analysis_results = {
            "by_category": by_category,
            "by_site": by_site,
            "category_comparison": category_comparison,
            "site_rankings": [
                {
                    "name": name,
                    "url": url,
                    "stats": stats
                }
                for name, url, stats in site_rankings
            ],
            "outliers": outliers
        }
        
        logger.info("Analysis complete")
        return analysis_results
    
    def save_analysis_results(self, analysis: dict) -> str:
        """Save analysis results."""
        analysis_path = self.processed_dir / f"analysis_{self.timestamp}.json"
        
        # Make stats serializable (convert numpy types if any)
        sanitized_analysis = self._make_serializable(analysis)
        
        with open(analysis_path, 'w') as f:
            json.dump(sanitized_analysis, f, indent=2)
        
        logger.info(f"Analysis results saved: {analysis_path}")
        return str(analysis_path)
    
    def generate_report(self, metrics_list: list) -> str:
        """
        Generate automated text report.
        
        Args:
            metrics_list: List of metrics dictionaries
            
        Returns:
            Report text
        """
        logger.info("Generating report...")
        
        generator = ReportGenerator(
            title="Web Intelligence Monitor - Measurement Report"
        )
        generator.load_metrics(metrics_list)
        report_text = generator.generate_report()
        
        logger.info("Report generated")
        return report_text
    
    def save_report(self, report_text: str) -> str:
        """Save report to file."""
        report_path = self.processed_dir / f"report_{self.timestamp}.txt"
        
        with open(report_path, 'w') as f:
            f.write(report_text)
        
        logger.info(f"Report saved: {report_path}")
        
        # Also print to console
        print("\n" + "=" * 80)
        print(report_text)
        print("=" * 80 + "\n")
        
        return str(report_path)
    
    @staticmethod
    def _make_serializable(obj):
        """Convert numpy types to native Python types for JSON serialization."""
        if isinstance(obj, dict):
            return {k: WebIntelligenceMonitor._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [WebIntelligenceMonitor._make_serializable(item) for item in obj]
        elif isinstance(obj, (int, float, str, bool, type(None))):
            return obj
        elif hasattr(obj, 'item'):  # numpy types
            return obj.item()
        else:
            return str(obj)
    
    async def run_full_pipeline(self, timeout_ms: int = 30000) -> dict:
        """
        Run complete measurement and analysis pipeline.
        
        Args:
            timeout_ms: Page load timeout in milliseconds
            
        Returns:
            Dictionary with paths to output files
        """
        logger.info("=" * 80)
        logger.info("Web Intelligence Monitor - Full Pipeline")
        logger.info(f"Timestamp: {self.timestamp}")
        logger.info("=" * 80)
        
        # Step 1: Load websites
        websites = self.load_websites()
        if not websites:
            logger.error("No websites to measure. Exiting.")
            return {}
        
        # Step 2: Collect measurements
        sessions = await self.collect_measurements(websites, timeout_ms)
        
        # Step 3: Save raw measurements
        csv_path = self.save_raw_measurements(sessions)
        
        # Step 4: Load metrics for analysis
        metrics_list = [s.metrics.to_dict() for s in sessions]
        
        # Step 5: Analyze measurements
        analysis = self.analyze_measurements(metrics_list)
        
        # Step 6: Save analysis
        analysis_path = self.save_analysis_results(analysis)
        
        # Step 7: Generate report
        report_text = self.generate_report(metrics_list)
        
        # Step 8: Save report
        report_path = self.save_report(report_text)
        
        logger.info("=" * 80)
        logger.info("Pipeline Complete!")
        logger.info("=" * 80)
        
        return {
            "raw_measurements": csv_path,
            "analysis": analysis_path,
            "report": report_path,
            "session_count": len(sessions),
            "success_count": sum(1 for s in sessions if s.metrics.is_success)
        }


async def main():
    """Main entry point."""
    monitor = WebIntelligenceMonitor()
    
    try:
        results = await monitor.run_full_pipeline(timeout_ms=30000)
        
        if results:
            print("\n✓ Pipeline executed successfully!")
            print(f"  Processed {results['session_count']} websites")
            print(f"  Successful: {results['success_count']} / {results['session_count']}")
            print(f"\nOutput files:")
            print(f"  Raw data: {results['raw_measurements']}")
            print(f"  Analysis: {results['analysis']}")
            print(f"  Report: {results['report']}")
    
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
