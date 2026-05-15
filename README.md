# Web Intelligence Monitor

A production-grade Python-based web measurement and reliability analysis system designed for systems research. This project demonstrates browser automation, controlled data collection, error handling, and data analysis of web performance and reliability.

## Project Overview

Web Intelligence Monitor is a structured prototype that:

- **Automates web measurement** using Playwright browser automation for a predefined list of websites
- **Collects detailed performance metrics**: page load times, resource counts, HTTP status codes, error tracking
- **Handles multiple failure modes gracefully**: timeouts, SSL errors, DNS failures, redirects
- **Performs statistical analysis**: outlier detection, percentile calculations, category-based benchmarking
- **Generates research-style reports** automatically with insights, performance rankings, and risk flags

This is **not** a web scraper or crawler—it's a **controlled measurement system** that visits specific websites and collects reproducible performance data.

## Architecture

```
web-intelligence-monitor/
├── crawler/                 # Browser automation using Playwright
│   ├── browser_automation.py    # Main Playwright orchestration
│   ├── website_session.py       # Individual measurement sessions
│   └── error_handling.py        # Structured error classification
├── data/
│   ├── websites.json            # Predefined website dataset
│   ├── raw/                     # Raw measurements (CSV/JSON)
│   └── processed/               # Analysis results and reports
├── analysis/                # Data analysis and scoring
│   ├── metrics.py              # Performance scoring algorithms
│   └── statistics.py           # Statistical aggregation
├── report/                  # Automated report generation
│   └── generator.py            # Text-based report creation
├── tests/                   # Unit tests
│   └── test_metrics.py         # Test scoring logic
├── main.py                  # Pipeline orchestration
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Installation & Setup

### Prerequisites

- Python 3.8+
- macOS, Linux, or Windows

### 1. Clone and Install

```bash
cd web-intelligence-monitor
pip install -r requirements.txt
playwright install  # Download browser binaries
```

### 2. Run the Full Pipeline

```bash
python main.py
```

This executes the complete workflow:
1. Loads the predefined ecommerce-focused website dataset
2. Measures each website (collects metrics)
3. Saves raw measurements to CSV
4. Analyzes data and computes scores
5. Generates automated text report
6. Outputs results to `data/processed/`

For the GitHub portfolio version, one polished sample report is kept here:

- `examples/sample_report.txt`

### 3. Run with Docker (Optional)

Build and run the project in a containerized environment:

```bash
docker build -t web-intelligence-monitor .
docker run -v $(pwd)/data/processed:/app/data/processed web-intelligence-monitor
```

The Docker image includes all dependencies and Playwright browsers pre-installed.

### Output Locations

After running, check:

- **Raw measurements**: `data/raw/raw_measurements_YYYYMMDD_HHMMSS.csv`
- **Analysis results**: `data/processed/analysis_YYYYMMDD_HHMMSS.json`
- **Report**: `data/processed/report_YYYYMMDD_HHMMSS.txt` (also printed to console)

Note: `data/raw/` and `data/processed/` are generated outputs and are ignored by Git. The repo keeps one curated example report in `examples/sample_report.txt` for reviewers.

## Collected Metrics

Per website visit, the system collects:

### Timing Metrics (milliseconds)
- **Page Load Time**: Total time from navigation start to page fully loaded
- **DOM Content Loaded**: Time to DOMContentLoaded event
- **Time to First Byte**: Server response time
- **Redirect Count**: Number of HTTP redirects followed

### Response Metrics
- **HTTP Status Code**: Final response status (200, 404, 500, etc.)
- **Response Size**: Approximate page content size in bytes
- **Total Requests**: Number of network requests
- **Failed Requests**: Count of unsuccessful requests
- **Blocked Requests**: Count of blocked requests

### Error Classification
- **Timeout**: Page load exceeded timeout threshold
- **SSL/TLS Error**: Certificate or encryption issues
- **DNS Error**: Domain resolution failure
- **HTTP Error**: 4xx or 5xx responses
- **Connection Error**: Network connectivity issues

### Success/Failure Flags
- `is_success`: Boolean indicating successful measurement
- `is_timeout`, `is_ssl_error`, `is_http_error`: Error-specific flags

## Website Dataset

The system includes a curated dataset of 50 websites focused on ecommerce and web reliability research:

### Categories

- **General ecommerce**: Amazon, eBay, Walmart, Target, Costco, Alibaba
- **Fashion/apparel**: ASOS, Shein, H&M, Zara, Forever 21, Uniqlo, Gap
- **Luxury retail**: Nordstrom, Saks Fifth Avenue, SSENSE, Farfetch
- **Specialty retail**: Etsy, Wayfair, Wish, Zappos, Ulta, Sephora, GameStop, Newegg, Chewy, Best Buy, Home Depot, Lowe's
- **Resale/second-hand**: Depop, Vestiaire Collective, The RealReal
- **Electronics**: Apple Store, B&H Photo Video, Adorama
- **Furniture**: Article, West Elm, Castlery
- **International ecommerce**: AliExpress, Flipkart, Lazada, Shopee, Mercado Libre, Jumia, Noon, Souq, Ozon
- **Edge cases** (for error testing): httpstat.us/200, httpstat.us/404, httpstat.us/500

To modify the dataset, edit `data/websites.json`:

```json
{
  "websites": [
    {
      "url": "https://example.com",
      "name": "Example Site",
      "category": "custom"
    }
  ]
}
```

## Analysis & Scoring

### Performance Score (0-100)

Combines load time and consistency:

- **Load Time Score** (70%):
  - Excellent (100): < 1000ms
  - Good (70): 1000-2000ms
  - Fair (50): 2000-4000ms
  - Poor: 4000ms+ and trending down toward 0 as latency increases
  
- **Consistency Score** (30%): Based on variance (lower = better)

### Reliability Score (0-100)

Success rate percentage:
- **Highly Reliable**: ≥95% success
- **Reliable**: 90-95% success
- **Adequate**: 75-90% success
- **Unreliable**: <75% success

### Percentiles

- **p50 (Median)**: 50th percentile
- **p95**: 95th percentile (typical "good" performance)
- **p99**: 99th percentile (outliers)

### Outlier Detection

Uses z-score method (z > 2.0) to identify statistical anomalies in load times.

## Generated Reports

Automated text-based report includes:

1. **Executive Summary**: Overall success rate, average load time, error counts
2. **Overall Statistics**: Mean, median, min, max, standard deviation, percentiles
3. **Category Analysis**: Performance breakdowns by website category
4. **Top Performers**: Best 10 websites ranked by performance score
5. **Bottom Performers**: Worst 10 websites flagged for attention (⚠️)
6. **Anomalies**: Statistical outliers with z-scores
7. **Reliability Analysis**: Error breakdown by category (timeouts, SSL, HTTP, other)
8. **Conclusions**: Key findings and recommendations

Example report section:

```
TOP 10 PERFORMING WEBSITES
────────────────────────────────────────────────────────────────────────────────
 1. Google
    URL: https://www.google.com
    Performance Score: 98.5/100
    Success Rate: 100.0%
    Mean Load Time: 425ms
```

## Testing

Run unit tests for metrics and scoring logic:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

Tests are organized into focused modules:
- `test_metrics.py`: Load time scoring and performance tiers
- `test_error_handling.py`: Error classification logic
- `test_statistics.py`: Statistical aggregation and outlier detection
- `test_report_generator.py`: Report generation sections

Coverage includes:
- Load time scoring algorithms
- Performance tier classification
- Consistency calculations
- Percentile computations
- Reliability tier classification
- Error classification logic
- Statistical analysis and aggregation

### Continuous Integration

Tests run automatically on every push via GitHub Actions. Check the workflow status in the Actions tab.

## Portfolio Readiness

This repository is structured to be profile-ready:

- Source code is committed in modular packages
- Generated measurement outputs stay local and out of Git
- One curated sample report is included for reviewers
- The README matches the current ecommerce-focused dataset and workflow
- Docker support for reproducible containerized execution
- Automated test suite with GitHub Actions CI/CD pipeline

## Key Features

✅ **Modular Design**: Clean separation between crawler, analysis, and reporting  
✅ **Error Resilience**: Graceful handling of timeouts, SSL errors, DNS failures  
✅ **Structured Data**: All metrics stored in reproducible CSV/JSON formats  
✅ **Production-Grade**: Logging, type hints, error handling, tests  
✅ **Research-Oriented**: Statistical analysis, percentiles, anomaly detection  
✅ **Automated Reporting**: No manual report writing required  
✅ **Extensible**: Easy to add new websites or metrics  

## Example: Running a Custom Measurement

```python
import asyncio
from crawler import BrowserAutomation, WebsiteSession

async def measure_custom():
    browser = BrowserAutomation(timeout_ms=30000)
    await browser.initialize()
    
    session = WebsiteSession(
        url="https://example.com",
        name="Example",
        category="custom"
    )
    
    measured = await browser.measure_website(session)
    print(f"Load time: {measured.metrics.page_load_time_ms}ms")
    print(f"Success: {measured.metrics.is_success}")
    
    await browser.close()

asyncio.run(measure_custom())
```

## Performance Considerations

- **Timeout**: Default 30 seconds per website (configurable)
- **Sequential Measurement**: Websites measured one at a time for stability
- **Headless Mode**: Browser runs without UI to save resources
- **Memory**: Contexts cleaned up after each measurement

## Future Enhancements

- Parallel measurement with configurable concurrency
- Core Web Vitals collection (LCP, CLS, FID)
- Periodic scheduled runs with trend analysis
- Comparison against historical data
- Network throttling simulation
- Visual performance metrics via screenshots

## Project Context

Built as a portfolio project to demonstrate:
- Python programming and systems design
- Browser automation and web measurement techniques
- Data collection and analysis workflows
- Error handling and resilience patterns
- Production-grade code structure
- Statistical analysis and reporting

This project mimics real-world web measurement systems used in:
- Web performance research
- Security testing and monitoring
- CDN effectiveness analysis
- Infrastructure benchmarking

## License

This is a portfolio project. Feel free to use, modify, and build upon it.

## Questions?

For project details, see the source code comments and docstrings. The codebase is designed to be readable and well-documented for portfolio review.
