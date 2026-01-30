"""
Statistical analysis module for Neuralace Patient Voice Engine.

Provides:
- Chi-square tests for category distribution significance
- Confidence intervals on percentages
- Sample size adequacy assessment
- Effect size calculations
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import math

try:
    from scipy import stats
    import numpy as np
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


@dataclass
class StatisticalResult:
    """Container for statistical test results."""
    test_name: str
    statistic: float
    p_value: float
    significant: bool  # p < 0.05
    interpretation: str


@dataclass
class ConfidenceInterval:
    """Container for confidence interval."""
    estimate: float
    lower: float
    upper: float
    confidence_level: float
    margin_of_error: float


@dataclass
class SampleAssessment:
    """Assessment of sample size adequacy."""
    sample_size: int
    minimum_recommended: int
    is_adequate: bool
    warning: Optional[str]
    power_estimate: Optional[float]


class StatisticalAnalyzer:
    """
    Performs statistical analysis on pain point data.

    Provides rigorous statistical testing to ensure conclusions
    are supported by data, not just patterns.
    """

    # Minimum samples for reliable statistics
    MIN_SAMPLE_SIZE = 30
    RECOMMENDED_SAMPLE_SIZE = 100

    # Significance level
    ALPHA = 0.05

    def __init__(self):
        """Initialize the statistical analyzer."""
        if not SCIPY_AVAILABLE:
            self._scipy_available = False
        else:
            self._scipy_available = True

    def chi_square_test(self, observed: Dict[str, int]) -> StatisticalResult:
        """
        Perform chi-square goodness-of-fit test.

        Tests whether the observed category distribution differs
        significantly from a uniform (equal) distribution.

        Args:
            observed: Dict of category -> count

        Returns:
            StatisticalResult with test outcome
        """
        if not self._scipy_available:
            return self._fallback_chi_square(observed)

        counts = list(observed.values())
        total = sum(counts)

        if total == 0:
            return StatisticalResult(
                test_name="Chi-Square Goodness of Fit",
                statistic=0.0,
                p_value=1.0,
                significant=False,
                interpretation="No data available for testing"
            )

        # Expected: uniform distribution
        n_categories = len(counts)
        expected = [total / n_categories] * n_categories

        # Perform chi-square test
        chi2, p_value = stats.chisquare(counts, f_exp=expected)

        significant = p_value < self.ALPHA
        interpretation = self._interpret_chi_square(chi2, p_value, significant)

        return StatisticalResult(
            test_name="Chi-Square Goodness of Fit",
            statistic=round(chi2, 3),
            p_value=round(p_value, 4),
            significant=significant,
            interpretation=interpretation
        )

    def _fallback_chi_square(self, observed: Dict[str, int]) -> StatisticalResult:
        """Manual chi-square calculation when scipy unavailable."""
        counts = list(observed.values())
        total = sum(counts)

        if total == 0:
            return StatisticalResult(
                test_name="Chi-Square Goodness of Fit",
                statistic=0.0,
                p_value=1.0,
                significant=False,
                interpretation="No data available for testing"
            )

        n = len(counts)
        expected = total / n
        chi2 = sum((obs - expected) ** 2 / expected for obs in counts)

        # Approximate p-value (very rough without scipy)
        # df = n - 1
        df = n - 1
        # Critical values: df=7, alpha=0.05 -> 14.07
        critical_value = 14.07 if df == 7 else df * 2

        significant = chi2 > critical_value
        p_value_approx = 0.01 if chi2 > critical_value * 1.5 else (0.05 if significant else 0.1)

        return StatisticalResult(
            test_name="Chi-Square Goodness of Fit (approx)",
            statistic=round(chi2, 3),
            p_value=p_value_approx,
            significant=significant,
            interpretation=f"Chi-square = {chi2:.2f}, {'significant' if significant else 'not significant'} at alpha=0.05"
        )

    def _interpret_chi_square(self, chi2: float, p_value: float, significant: bool) -> str:
        """Generate human-readable interpretation of chi-square result."""
        if significant:
            if p_value < 0.001:
                strength = "highly"
            elif p_value < 0.01:
                strength = "very"
            else:
                strength = "statistically"
            return f"Pain point distribution is {strength} significant (p={p_value:.4f}). Categories are NOT equally distributed."
        else:
            return f"No significant difference in pain point distribution (p={p_value:.4f}). Cannot conclude categories differ from uniform."

    def confidence_interval(
        self,
        count: int,
        total: int,
        confidence: float = 0.95
    ) -> ConfidenceInterval:
        """
        Calculate confidence interval for a proportion.

        Uses Wilson score interval for better coverage
        with small samples.

        Args:
            count: Number of observations in category
            total: Total observations
            confidence: Confidence level (default 0.95)

        Returns:
            ConfidenceInterval with bounds
        """
        if total == 0:
            return ConfidenceInterval(
                estimate=0.0,
                lower=0.0,
                upper=0.0,
                confidence_level=confidence,
                margin_of_error=0.0
            )

        p = count / total
        n = total

        if self._scipy_available:
            z = stats.norm.ppf(1 - (1 - confidence) / 2)
        else:
            # Approximate z-score for 95% CI
            z = 1.96 if confidence == 0.95 else 2.576 if confidence == 0.99 else 1.645

        # Wilson score interval
        denominator = 1 + z**2 / n
        center = (p + z**2 / (2 * n)) / denominator
        spread = z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denominator

        lower = max(0, center - spread)
        upper = min(1, center + spread)

        # Convert to percentage
        estimate_pct = p * 100
        lower_pct = lower * 100
        upper_pct = upper * 100
        margin = (upper_pct - lower_pct) / 2

        return ConfidenceInterval(
            estimate=round(estimate_pct, 1),
            lower=round(lower_pct, 1),
            upper=round(upper_pct, 1),
            confidence_level=confidence,
            margin_of_error=round(margin, 1)
        )

    def assess_sample_size(self, n: int) -> SampleAssessment:
        """
        Assess whether sample size is adequate for reliable conclusions.

        Args:
            n: Sample size

        Returns:
            SampleAssessment with recommendations
        """
        is_adequate = n >= self.MIN_SAMPLE_SIZE
        warning = None
        power = None

        if n < 10:
            warning = f"CRITICAL: Sample size ({n}) too small for any statistical inference"
            power = 0.1
        elif n < self.MIN_SAMPLE_SIZE:
            warning = f"WARNING: Sample size ({n}) below minimum ({self.MIN_SAMPLE_SIZE}). Results may be unreliable."
            power = 0.3 + (n / self.MIN_SAMPLE_SIZE) * 0.4
        elif n < self.RECOMMENDED_SAMPLE_SIZE:
            warning = f"NOTICE: Sample size ({n}) adequate but below recommended ({self.RECOMMENDED_SAMPLE_SIZE})"
            power = 0.7 + ((n - self.MIN_SAMPLE_SIZE) / (self.RECOMMENDED_SAMPLE_SIZE - self.MIN_SAMPLE_SIZE)) * 0.2
        else:
            power = min(0.95, 0.9 + (n / 500) * 0.05)

        return SampleAssessment(
            sample_size=n,
            minimum_recommended=self.MIN_SAMPLE_SIZE,
            is_adequate=is_adequate,
            warning=warning,
            power_estimate=round(power, 2) if power else None
        )

    def effect_size_cramers_v(self, observed: Dict[str, int]) -> float:
        """
        Calculate Cramer's V effect size for categorical data.

        Interpretation:
        - < 0.1: negligible
        - 0.1 - 0.3: small
        - 0.3 - 0.5: medium
        - > 0.5: large

        Args:
            observed: Dict of category -> count

        Returns:
            Cramer's V value (0 to 1)
        """
        counts = list(observed.values())
        total = sum(counts)
        n_categories = len(counts)

        if total == 0 or n_categories <= 1:
            return 0.0

        # Calculate chi-square
        expected = total / n_categories
        chi2 = sum((obs - expected) ** 2 / expected for obs in counts)

        # Cramer's V
        cramers_v = math.sqrt(chi2 / (total * (n_categories - 1)))

        return round(min(1.0, cramers_v), 3)

    def interpret_effect_size(self, v: float) -> str:
        """Interpret Cramer's V effect size."""
        if v < 0.1:
            return "negligible"
        elif v < 0.3:
            return "small"
        elif v < 0.5:
            return "medium"
        else:
            return "large"

    def full_statistical_report(self, analysis_result: Dict) -> Dict:
        """
        Generate comprehensive statistical report from analysis results.

        Args:
            analysis_result: Output from PainPointAnalyzer.analyze()

        Returns:
            Dict with all statistical measures
        """
        categories = analysis_result.get('categories', {})
        total_analyzed = analysis_result.get('total_analyzed', 0)

        # Extract counts
        counts = {cat: data['count'] for cat, data in categories.items()}
        total_matches = sum(counts.values())

        # Sample size assessment
        sample_assessment = self.assess_sample_size(total_analyzed)

        # Chi-square test
        chi_square_result = self.chi_square_test(counts)

        # Effect size
        effect_size = self.effect_size_cramers_v(counts)
        effect_interpretation = self.interpret_effect_size(effect_size)

        # Confidence intervals for each category
        confidence_intervals = {}
        for cat, count in counts.items():
            ci = self.confidence_interval(count, total_matches)
            confidence_intervals[cat] = {
                'estimate': ci.estimate,
                'lower': ci.lower,
                'upper': ci.upper,
                'margin_of_error': ci.margin_of_error,
                'formatted': f"{ci.estimate}% ({ci.lower}% - {ci.upper}%)"
            }

        return {
            'sample_assessment': {
                'n': sample_assessment.sample_size,
                'is_adequate': sample_assessment.is_adequate,
                'warning': sample_assessment.warning,
                'power': sample_assessment.power_estimate
            },
            'chi_square': {
                'statistic': chi_square_result.statistic,
                'p_value': chi_square_result.p_value,
                'significant': chi_square_result.significant,
                'interpretation': chi_square_result.interpretation
            },
            'effect_size': {
                'cramers_v': effect_size,
                'interpretation': effect_interpretation
            },
            'confidence_intervals': confidence_intervals
        }


def create_statistical_analyzer() -> StatisticalAnalyzer:
    """Factory function to create a statistical analyzer."""
    return StatisticalAnalyzer()
