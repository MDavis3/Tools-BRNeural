"""
Temporal trend analysis module for Neuralace Patient Voice Engine.

Analyzes how pain points evolve over time:
- 7-day, 30-day, 90-day trend lines
- Emerging vs stable pain points
- Velocity metrics (rising, falling, stable)
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict
import math


@dataclass
class TrendPoint:
    """A single point in a trend line."""
    period_start: datetime
    period_end: datetime
    count: int
    percentage: float


@dataclass
class CategoryTrend:
    """Trend analysis for a single category."""
    category: str
    current_percentage: float
    previous_percentage: float
    change: float  # Percentage point change
    change_rate: float  # Rate of change (%)
    direction: str  # 'rising', 'falling', 'stable'
    velocity: str  # 'fast', 'moderate', 'slow'
    is_emerging: bool
    trend_points: List[TrendPoint]


@dataclass
class TrendReport:
    """Complete trend analysis report."""
    analysis_period: str
    total_items: int
    category_trends: Dict[str, CategoryTrend]
    emerging_concerns: List[str]
    declining_concerns: List[str]
    stable_concerns: List[str]
    top_mover: Optional[str]
    top_mover_change: float


class TrendAnalyzer:
    """
    Analyzes temporal trends in pain point data.

    Identifies which pain points are emerging, stable, or declining
    to help prioritize product development.
    """

    # Thresholds for trend classification
    SIGNIFICANT_CHANGE = 5.0  # Percentage points
    FAST_VELOCITY = 10.0  # Percentage points
    MODERATE_VELOCITY = 5.0

    # Time periods
    PERIODS = {
        '7d': timedelta(days=7),
        '30d': timedelta(days=30),
        '90d': timedelta(days=90)
    }

    def __init__(self):
        """Initialize the trend analyzer."""
        pass

    def analyze_trends(
        self,
        data: List[Dict],
        period: str = '30d',
        analyzer=None
    ) -> TrendReport:
        """
        Analyze temporal trends in pain point data.

        Args:
            data: List of dicts with 'text', 'timestamp', etc.
            period: Analysis period ('7d', '30d', '90d')
            analyzer: Optional PainPointAnalyzer instance

        Returns:
            TrendReport with trend analysis
        """
        if period not in self.PERIODS:
            period = '30d'

        period_delta = self.PERIODS[period]
        now = datetime.now()
        period_start = now - period_delta

        # Split data into current and previous periods
        current_data = []
        previous_data = []

        for item in data:
            timestamp = item.get('timestamp')
            if not timestamp:
                continue

            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp)
                except ValueError:
                    continue

            if timestamp >= period_start:
                current_data.append(item)
            elif timestamp >= period_start - period_delta:
                previous_data.append(item)

        # Analyze both periods
        if analyzer is None:
            from .analyzer import PainPointAnalyzer
            analyzer = PainPointAnalyzer(use_sentiment=False)

        current_analysis = analyzer.analyze(current_data) if current_data else None
        previous_analysis = analyzer.analyze(previous_data) if previous_data else None

        # Calculate trends for each category
        category_trends = self._calculate_category_trends(
            current_analysis,
            previous_analysis,
            period
        )

        # Classify trends
        emerging = []
        declining = []
        stable = []
        top_mover = None
        max_change = 0.0

        for cat, trend in category_trends.items():
            if trend.is_emerging:
                emerging.append(cat)
            elif trend.direction == 'falling' and abs(trend.change) >= self.SIGNIFICANT_CHANGE:
                declining.append(cat)
            else:
                stable.append(cat)

            if abs(trend.change) > abs(max_change):
                max_change = trend.change
                top_mover = cat

        return TrendReport(
            analysis_period=period,
            total_items=len(current_data) + len(previous_data),
            category_trends=category_trends,
            emerging_concerns=emerging,
            declining_concerns=declining,
            stable_concerns=stable,
            top_mover=top_mover,
            top_mover_change=max_change
        )

    def _calculate_category_trends(
        self,
        current: Optional[Dict],
        previous: Optional[Dict],
        period: str
    ) -> Dict[str, CategoryTrend]:
        """Calculate trend metrics for each category."""
        trends = {}

        # Get all categories
        all_categories = set()
        if current and 'categories' in current:
            all_categories.update(current['categories'].keys())
        if previous and 'categories' in previous:
            all_categories.update(previous['categories'].keys())

        for category in all_categories:
            current_pct = 0.0
            previous_pct = 0.0

            if current and 'categories' in current:
                current_pct = current['categories'].get(category, {}).get('percentage', 0.0)
            if previous and 'categories' in previous:
                previous_pct = previous['categories'].get(category, {}).get('percentage', 0.0)

            # Calculate change
            change = current_pct - previous_pct

            # Calculate rate of change
            if previous_pct > 0:
                change_rate = (change / previous_pct) * 100
            else:
                change_rate = 100.0 if current_pct > 0 else 0.0

            # Determine direction
            if change >= self.SIGNIFICANT_CHANGE:
                direction = 'rising'
            elif change <= -self.SIGNIFICANT_CHANGE:
                direction = 'falling'
            else:
                direction = 'stable'

            # Determine velocity
            abs_change = abs(change)
            if abs_change >= self.FAST_VELOCITY:
                velocity = 'fast'
            elif abs_change >= self.MODERATE_VELOCITY:
                velocity = 'moderate'
            else:
                velocity = 'slow'

            # Is emerging? (new or rapidly rising)
            is_emerging = (
                (previous_pct < 5.0 and current_pct >= 10.0) or
                (direction == 'rising' and velocity == 'fast')
            )

            trends[category] = CategoryTrend(
                category=category,
                current_percentage=current_pct,
                previous_percentage=previous_pct,
                change=round(change, 1),
                change_rate=round(change_rate, 1),
                direction=direction,
                velocity=velocity,
                is_emerging=is_emerging,
                trend_points=[]  # Could add more granular data
            )

        return trends

    def get_trend_summary(self, trend_report: TrendReport) -> Dict:
        """
        Generate a summary of trends for display.

        Args:
            trend_report: TrendReport from analyze_trends

        Returns:
            Dict with formatted trend summary
        """
        summary = {
            'period': trend_report.analysis_period,
            'emerging': [],
            'declining': [],
            'stable': [],
            'top_mover': None
        }

        for cat in trend_report.emerging_concerns:
            trend = trend_report.category_trends.get(cat)
            if trend:
                summary['emerging'].append({
                    'category': cat,
                    'change': f"+{trend.change}%",
                    'symbol': '↑'
                })

        for cat in trend_report.declining_concerns:
            trend = trend_report.category_trends.get(cat)
            if trend:
                summary['declining'].append({
                    'category': cat,
                    'change': f"{trend.change}%",
                    'symbol': '↓'
                })

        for cat in trend_report.stable_concerns:
            trend = trend_report.category_trends.get(cat)
            if trend:
                summary['stable'].append({
                    'category': cat,
                    'change': f"{trend.change:+.1f}%",
                    'symbol': '→'
                })

        if trend_report.top_mover:
            summary['top_mover'] = {
                'category': trend_report.top_mover,
                'change': trend_report.top_mover_change
            }

        return summary

    def format_trend_line(self, category: str, trend: CategoryTrend) -> str:
        """
        Format a single trend line for display.

        Args:
            category: Category name
            trend: CategoryTrend object

        Returns:
            Formatted string like "↑ Social Stigma: +15% over 30 days (emerging)"
        """
        if trend.direction == 'rising':
            symbol = '↑'
        elif trend.direction == 'falling':
            symbol = '↓'
        else:
            symbol = '→'

        change_str = f"+{trend.change}" if trend.change > 0 else str(trend.change)
        status = " (emerging)" if trend.is_emerging else ""

        return f"{symbol} {category}: {change_str}% ({trend.velocity}){status}"


def create_trend_analyzer() -> TrendAnalyzer:
    """Factory function to create a trend analyzer."""
    return TrendAnalyzer()
