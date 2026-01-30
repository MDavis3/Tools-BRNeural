"""
Strategic report generator for Neuralace Patient Voice Engine v2.0.

Enhanced with:
- Statistical significance indicators
- Confidence intervals
- Sentiment distribution
- Trend analysis
- Competitor mentions
"""

from typing import Dict, Optional
from datetime import datetime


def generate_strategic_report(
    analysis: Dict,
    statistics: Optional[Dict] = None,
    trends: Optional[Dict] = None,
    competitors: Optional[Dict] = None
) -> str:
    """
    Generate a comprehensive strategic insight report.

    Args:
        analysis: Results from PainPointAnalyzer
        statistics: Results from StatisticalAnalyzer (optional)
        trends: Results from TrendAnalyzer (optional)
        competitors: Results from CompetitorAnalyzer (optional)

    Returns:
        Formatted report string for console output
    """
    categories = analysis.get('categories', {})
    top_pain_point = analysis.get('top_pain_point')
    representative_quote = analysis.get('representative_quote', '')
    neuralace_advantage = analysis.get('neuralace_advantage', '')
    sentiment_dist = analysis.get('sentiment_distribution', {})
    total_analyzed = analysis.get('total_analyzed', 0)
    filtered = analysis.get('filtered_by_sentiment', 0)

    # Handle empty/no data case
    if not top_pain_point or all(cat['count'] == 0 for cat in categories.values()):
        return _generate_empty_report()

    # Get percentage and confidence for top pain point
    top_data = categories.get(top_pain_point, {})
    top_percentage = top_data.get('percentage', 0)
    top_confidence = top_data.get('confidence_avg', 0)

    # Build the report
    lines = [
        "",
        "=" * 75,
        "  NEURALACE PATIENT VOICE ENGINE v2.0 - STRATEGIC INSIGHT REPORT",
        "=" * 75,
        f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]

    # Sample info
    lines.extend([
        "  DATA SUMMARY:",
        f"    Total comments analyzed: {total_analyzed}",
        f"    Filtered (positive sentiment): {filtered}",
        f"    Sentiment: {sentiment_dist.get('negative', 0)} negative, "
        f"{sentiment_dist.get('neutral', 0)} neutral, "
        f"{sentiment_dist.get('positive', 0)} positive",
        "",
    ])

    # Statistical significance (if provided)
    if statistics:
        chi_sq = statistics.get('chi_square', {})
        sample = statistics.get('sample_assessment', {})
        p_value = chi_sq.get('p_value', 'N/A')
        significant = chi_sq.get('significant', False)
        sig_marker = "*" if significant else ""

        lines.extend([
            "-" * 75,
            "  STATISTICAL ANALYSIS:",
            f"    Chi-square p-value: {p_value}{sig_marker}",
            f"    Statistical significance: {'YES' if significant else 'NO'} (alpha=0.05)",
        ])

        if sample.get('warning'):
            lines.append(f"    {sample['warning']}")
        lines.append("")

    # Main finding
    lines.extend([
        "-" * 75,
        f"  TOP PATIENT PAIN POINT: {top_pain_point}",
        f"    Percentage: {top_percentage}%",
        f"    Confidence: {top_confidence:.2f}",
    ])

    # Add confidence interval if available
    if statistics:
        ci = statistics.get('confidence_intervals', {}).get(top_pain_point, {})
        if ci:
            lines.append(f"    95% CI: {ci.get('lower', 0)}% - {ci.get('upper', 0)}%")

    lines.extend([
        "",
        "  REPRESENTATIVE QUOTE:",
        f'    "{representative_quote}"',
        "",
        "  NEURALACE COMPETITIVE ADVANTAGE:",
        f"    {neuralace_advantage}",
        "",
    ])

    # Full breakdown
    lines.extend([
        "-" * 75,
        "  FULL PAIN POINT BREAKDOWN:",
    ])

    for category, data in sorted(categories.items(), key=lambda x: -x[1]['percentage']):
        count = data['count']
        percentage = data['percentage']
        confidence = data.get('confidence_avg', 0)

        # Add confidence interval if available
        ci_str = ""
        if statistics:
            ci = statistics.get('confidence_intervals', {}).get(category, {})
            if ci:
                ci_str = f" (CI: {ci.get('lower', 0)}-{ci.get('upper', 0)}%)"

        bar = "#" * int(percentage / 5) + "-" * (20 - int(percentage / 5))
        lines.append(f"    {category}:")
        lines.append(f"      [{bar}] {percentage}%{ci_str}")
        lines.append(f"      {count} mentions, confidence: {confidence:.2f}")

    # Trend analysis (if provided)
    if trends:
        lines.extend([
            "",
            "-" * 75,
            "  TREND ANALYSIS (30-day):",
        ])

        emerging = trends.get('emerging_concerns', [])
        declining = trends.get('declining_concerns', [])

        if emerging:
            lines.append("    Emerging concerns:")
            for cat in emerging:
                lines.append(f"      [UP] {cat}")

        if declining:
            lines.append("    Declining concerns:")
            for cat in declining:
                lines.append(f"      [DOWN] {cat}")

        if not emerging and not declining:
            lines.append("    All pain points stable")

    # Competitor analysis (if provided)
    if competitors and competitors.get('total_competitor_mentions', 0) > 0:
        lines.extend([
            "",
            "-" * 75,
            "  COMPETITOR INTELLIGENCE:",
            f"    Total competitor mentions: {competitors.get('total_competitor_mentions', 0)}",
            f"    Most discussed: {competitors.get('most_mentioned', 'N/A')}",
            f"    Highest switching intent: {competitors.get('highest_switching_intent', 'N/A')}",
        ])

    # Product-market fit assessment
    lines.extend([
        "",
        "-" * 75,
        "  PRODUCT-MARKET FIT ASSESSMENT:",
    ])

    # Calculate fit signal based on data
    fit_signal = _assess_product_market_fit(analysis, statistics)
    lines.append(f"    Signal Strength: {fit_signal['strength']}")
    lines.append(f"    {fit_signal['rationale']}")

    lines.extend([
        "",
        "=" * 75,
        ""
    ])

    return "\n".join(lines)


def _assess_product_market_fit(analysis: Dict, statistics: Optional[Dict]) -> Dict:
    """Assess product-market fit based on analysis results."""
    top_pp = analysis.get('top_pain_point')
    categories = analysis.get('categories', {})
    total = analysis.get('total_analyzed', 0)

    # Calculate strength
    if not top_pp or total < 10:
        return {
            'strength': 'INSUFFICIENT DATA',
            'rationale': 'Need more data to assess product-market fit.'
        }

    # Check if significant pain points align with Neuralace advantages
    top_pct = categories.get(top_pp, {}).get('percentage', 0)
    neuralace_advantages = {
        'Infection Risk', 'Form Factor', 'Social Stigma',
        'Battery & Maintenance', 'Device Reliability'
    }

    advantaged_pct = sum(
        categories.get(cat, {}).get('percentage', 0)
        for cat in neuralace_advantages
        if cat in categories
    )

    # Statistical significance boost
    stat_boost = 0
    if statistics and statistics.get('chi_square', {}).get('significant'):
        stat_boost = 10

    score = advantaged_pct + stat_boost

    if score >= 70:
        return {
            'strength': 'VERY STRONG',
            'rationale': f'{advantaged_pct:.0f}% of pain points directly addressed by Neuralace technology.'
        }
    elif score >= 50:
        return {
            'strength': 'STRONG',
            'rationale': 'Majority of patient concerns map to Neuralace competitive advantages.'
        }
    elif score >= 30:
        return {
            'strength': 'MODERATE',
            'rationale': 'Some alignment between patient needs and Neuralace capabilities.'
        }
    else:
        return {
            'strength': 'DEVELOPING',
            'rationale': 'Limited alignment - further market research recommended.'
        }


def _generate_empty_report() -> str:
    """Generate report for empty/no data case."""
    return "\n".join([
        "",
        "=" * 75,
        "  NEURALACE PATIENT VOICE ENGINE v2.0 - STRATEGIC INSIGHT REPORT",
        "=" * 75,
        "",
        "  NO DATA AVAILABLE",
        "",
        "  Unable to generate insights - no patient data found.",
        "  Please check data source configuration.",
        "",
        "  Troubleshooting:",
        "    - Verify Reddit API credentials (live mode)",
        "    - Check network connectivity",
        "    - Try simulation mode for testing",
        "",
        "=" * 75,
        ""
    ])


def generate_executive_summary(analysis: Dict) -> str:
    """Generate a brief executive summary."""
    top_pp = analysis.get('top_pain_point', 'Unknown')
    top_pct = analysis.get('categories', {}).get(top_pp, {}).get('percentage', 0)
    advantage = analysis.get('neuralace_advantage', '')

    return f"""
EXECUTIVE SUMMARY
=================
Top Patient Pain Point: {top_pp} ({top_pct}%)
Neuralace Advantage: {advantage}

Recommendation: Prioritize {top_pp} messaging in market positioning.
"""
