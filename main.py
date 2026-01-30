#!/usr/bin/env python3
"""
Neuralace Patient Voice Engine v2.0
===================================
A comprehensive Python tool to mine patient communities and validate
Blackrock Neurotech's Neuralace value proposition against legacy BCI technology.

Features:
- 8 pain point categories with sentiment analysis
- Statistical significance testing (chi-square, confidence intervals)
- Competitor tracking (Neuralink, Synchron, BrainGate, etc.)
- Temporal trend analysis
- LLM-powered deep analysis (optional, requires API key)

Usage:
    python main.py [--mode simulation|live] [--full]

Example:
    python main.py                    # Uses simulation mode (default)
    python main.py --mode live        # Uses Reddit API (requires credentials)
    python main.py --full             # Run full analysis with all modules
"""

import argparse
import sys

from neuralace_engine.ingestor import PatientDataIngestor
from neuralace_engine.analyzer import PainPointAnalyzer
from neuralace_engine.statistics import StatisticalAnalyzer
from neuralace_engine.competitors import CompetitorAnalyzer
from neuralace_engine.trends import TrendAnalyzer
from neuralace_engine.report import generate_strategic_report


def main(mode: str = "simulation", full_analysis: bool = True) -> None:
    """
    Run the Neuralace Patient Voice Engine v2.0.

    Args:
        mode: "simulation" for mock data, "live" for Reddit API
        full_analysis: Whether to run all analysis modules
    """
    print("\n" + "=" * 60)
    print("  NEURALACE PATIENT VOICE ENGINE v2.0")
    print("=" * 60)
    print(f"\n[*] Mode: {mode.upper()}")

    # Initialize data ingestor
    ingestor = PatientDataIngestor(mode=mode)

    # Target subreddits for BCI patient communities
    target_subreddits = ['ALS', 'spinalcordinjuries']
    print(f"[*] Target communities: r/{', r/'.join(target_subreddits)}")

    # Fetch patient discussion data
    print("[*] Fetching patient discussions...")
    data = ingestor.fetch_data(subreddits=target_subreddits, limit=100)
    print(f"[*] Retrieved {len(data)} patient comments/posts")

    # Core analysis - Pain points with sentiment
    print("[*] Analyzing pain points (8 categories, sentiment filtering)...")
    analyzer = PainPointAnalyzer(use_sentiment=True)
    analysis = analyzer.analyze(data)
    print(f"    - Top pain point: {analysis['top_pain_point']}")
    print(f"    - Filtered by sentiment: {analysis['filtered_by_sentiment']} positive comments")

    # Statistical analysis
    stats = None
    if full_analysis:
        print("[*] Running statistical analysis...")
        stats_analyzer = StatisticalAnalyzer()
        stats = stats_analyzer.full_statistical_report(analysis)
        print(f"    - Chi-square p-value: {stats['chi_square']['p_value']}")
        print(f"    - Significant: {'YES' if stats['chi_square']['significant'] else 'NO'}")

    # Competitor analysis
    competitors = None
    if full_analysis:
        print("[*] Analyzing competitor mentions...")
        comp_analyzer = CompetitorAnalyzer()
        comp_result = comp_analyzer.analyze(data)
        competitors = {
            'total_competitor_mentions': comp_result.total_competitor_mentions,
            'most_mentioned': comp_result.most_mentioned,
            'highest_switching_intent': comp_result.highest_switching_intent
        }
        print(f"    - Total competitor mentions: {competitors['total_competitor_mentions']}")
        if competitors['most_mentioned']:
            print(f"    - Most discussed: {competitors['most_mentioned']}")

    # Trend analysis
    trends = None
    if full_analysis:
        print("[*] Analyzing temporal trends (30-day)...")
        trend_analyzer = TrendAnalyzer()
        trend_result = trend_analyzer.analyze_trends(data, period='30d', analyzer=analyzer)
        trends = {
            'emerging_concerns': trend_result.emerging_concerns,
            'declining_concerns': trend_result.declining_concerns
        }
        if trend_result.emerging_concerns:
            print(f"    - Emerging: {', '.join(trend_result.emerging_concerns)}")
        else:
            print("    - No emerging concerns detected")

    # Generate comprehensive report
    print("\n[*] Generating strategic insight report...")
    report = generate_strategic_report(
        analysis,
        statistics=stats,
        trends=trends,
        competitors=competitors
    )
    print(report)

    print("[*] Analysis complete.\n")

    # Print quick start for other features
    print("-" * 60)
    print("  ADDITIONAL FEATURES:")
    print("-" * 60)
    print("  Run Streamlit Dashboard:")
    print("    streamlit run dashboard/app.py")
    print("")
    print("  Run REST API:")
    print("    uvicorn api.main:app --reload")
    print("    Then visit: http://localhost:8000/docs")
    print("-" * 60 + "\n")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Neuralace Patient Voice Engine v2.0 - BCI Pain Point Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py                    Run with simulation data (default)
    python main.py --mode live        Run with Reddit API (requires credentials)
    python main.py --full             Run full analysis with all modules
    python main.py --basic            Run basic analysis only (faster)

For live mode, set environment variables:
    REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET

For LLM analysis, set:
    ANTHROPIC_API_KEY

Dashboard:
    streamlit run dashboard/app.py

REST API:
    uvicorn api.main:app --reload
        """
    )
    parser.add_argument(
        '--mode',
        choices=['simulation', 'live'],
        default='simulation',
        help='Data source mode (default: simulation)'
    )
    parser.add_argument(
        '--full',
        action='store_true',
        default=True,
        help='Run full analysis with statistics, trends, competitors (default)'
    )
    parser.add_argument(
        '--basic',
        action='store_true',
        help='Run basic analysis only (faster, no stats/trends)'
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    full_analysis = not args.basic
    try:
        main(mode=args.mode, full_analysis=full_analysis)
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[!] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
