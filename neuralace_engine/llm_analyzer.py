"""
LLM-powered analysis module for Neuralace Patient Voice Engine.

Uses Claude API for deep semantic understanding:
- Nuanced sentiment analysis
- Context-aware pain point categorization
- Switching intent detection
- Key quote extraction
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import json
import os

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


@dataclass
class LLMAnalysisResult:
    """Result from LLM analysis of a single comment."""
    text: str
    primary_pain_point: str
    secondary_pain_points: List[str]
    sentiment_score: int  # 1-10 scale
    sentiment_label: str
    severity: int  # 1-10 scale
    switching_intent: bool
    switching_intent_confidence: float
    key_quote: str
    insights: List[str]
    raw_response: Optional[Dict]


@dataclass
class LLMBatchResult:
    """Result from batch LLM analysis."""
    total_analyzed: int
    successful: int
    failed: int
    results: List[LLMAnalysisResult]
    aggregate_insights: List[str]
    cost_estimate: float


class LLMAnalyzer:
    """
    Uses Claude API for sophisticated semantic analysis.

    Provides deeper understanding than keyword matching:
    - Understands context, sarcasm, nuance
    - Handles negation naturally
    - Identifies implicit pain points
    - Extracts actionable quotes
    """

    # Pain point categories for LLM prompt
    PAIN_CATEGORIES = [
        "Infection Risk",
        "Form Factor",
        "Social Stigma",
        "Device Reliability",
        "Battery & Maintenance",
        "Clinical Efficacy",
        "Cost & Access",
        "Quality of Life"
    ]

    # Model configuration
    DEFAULT_MODEL = "claude-sonnet-4-20250514"
    MAX_TOKENS = 1000

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM analyzer.

        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self._client = None

        if ANTHROPIC_AVAILABLE and self.api_key:
            self._client = anthropic.Anthropic(api_key=self.api_key)

    def is_available(self) -> bool:
        """Check if LLM analysis is available."""
        return self._client is not None

    def analyze_comment(self, text: str) -> LLMAnalysisResult:
        """
        Analyze a single patient comment using Claude.

        Args:
            text: The patient comment text

        Returns:
            LLMAnalysisResult with detailed analysis
        """
        if not self.is_available():
            return self._fallback_analysis(text)

        prompt = self._build_analysis_prompt(text)

        try:
            response = self._client.messages.create(
                model=self.DEFAULT_MODEL,
                max_tokens=self.MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse the response
            return self._parse_response(text, response)

        except Exception as e:
            # Fallback on error
            return self._fallback_analysis(text, error=str(e))

    def analyze_batch(
        self,
        data: List[Dict],
        max_items: int = 50
    ) -> LLMBatchResult:
        """
        Analyze a batch of patient comments.

        Args:
            data: List of dicts with 'text' key
            max_items: Maximum items to analyze (for cost control)

        Returns:
            LLMBatchResult with aggregated analysis
        """
        results = []
        successful = 0
        failed = 0

        # Limit to max_items
        items_to_process = data[:max_items]

        for item in items_to_process:
            text = item.get('text', '')
            if not text:
                continue

            result = self.analyze_comment(text)
            results.append(result)

            if result.raw_response is not None or not self.is_available():
                successful += 1
            else:
                failed += 1

        # Generate aggregate insights
        aggregate_insights = self._generate_aggregate_insights(results)

        # Estimate cost (rough: ~$0.003 per 1K tokens)
        estimated_tokens = sum(len(r.text.split()) * 2 for r in results)
        cost_estimate = (estimated_tokens / 1000) * 0.003

        return LLMBatchResult(
            total_analyzed=len(items_to_process),
            successful=successful,
            failed=failed,
            results=results,
            aggregate_insights=aggregate_insights,
            cost_estimate=round(cost_estimate, 4)
        )

    def _build_analysis_prompt(self, text: str) -> str:
        """Build the analysis prompt for Claude."""
        categories_str = ", ".join(self.PAIN_CATEGORIES)

        return f"""Analyze this BCI (Brain-Computer Interface) patient comment for pain points and sentiment.

PATIENT COMMENT:
"{text}"

AVAILABLE PAIN POINT CATEGORIES:
{categories_str}

Provide your analysis in the following JSON format (no markdown, just raw JSON):
{{
    "primary_pain_point": "<most relevant category or 'None'>",
    "secondary_pain_points": ["<other relevant categories>"],
    "sentiment_score": <1-10, where 1=very negative, 5=neutral, 10=very positive>,
    "sentiment_label": "<negative|neutral|positive>",
    "severity": <1-10, where 1=minor inconvenience, 10=life-threatening concern>,
    "switching_intent": <true if patient expresses desire to try different technology>,
    "switching_intent_confidence": <0.0-1.0>,
    "key_quote": "<most impactful phrase from the comment>",
    "insights": ["<specific actionable insight 1>", "<insight 2>"]
}}

Focus on:
1. Understanding the CONTEXT - don't just match keywords
2. Detecting sarcasm, irony, or mixed feelings
3. Identifying implicit concerns not explicitly stated
4. Extracting the most emotionally resonant quote

Respond ONLY with the JSON, no additional text."""

    def _parse_response(self, text: str, response: Any) -> LLMAnalysisResult:
        """Parse Claude's response into structured result."""
        try:
            # Extract text content
            content = response.content[0].text

            # Parse JSON
            data = json.loads(content)

            return LLMAnalysisResult(
                text=text,
                primary_pain_point=data.get('primary_pain_point', 'Unknown'),
                secondary_pain_points=data.get('secondary_pain_points', []),
                sentiment_score=data.get('sentiment_score', 5),
                sentiment_label=data.get('sentiment_label', 'neutral'),
                severity=data.get('severity', 5),
                switching_intent=data.get('switching_intent', False),
                switching_intent_confidence=data.get('switching_intent_confidence', 0.0),
                key_quote=data.get('key_quote', text[:100]),
                insights=data.get('insights', []),
                raw_response=data
            )

        except (json.JSONDecodeError, KeyError, IndexError) as e:
            return self._fallback_analysis(text, error=f"Parse error: {e}")

    def _fallback_analysis(
        self,
        text: str,
        error: Optional[str] = None
    ) -> LLMAnalysisResult:
        """
        Provide fallback analysis when LLM is unavailable.

        Uses basic keyword matching as backup.
        """
        # Simple keyword-based fallback
        text_lower = text.lower()

        # Detect primary pain point
        primary = "Unknown"
        for category in self.PAIN_CATEGORIES:
            keywords = self._get_category_keywords(category)
            if any(kw in text_lower for kw in keywords):
                primary = category
                break

        # Simple sentiment
        negative_words = ['hate', 'terrible', 'worst', 'awful', 'horrible', 'scared', 'terrified']
        positive_words = ['love', 'great', 'amazing', 'happy', 'better', 'improved']

        neg_count = sum(1 for w in negative_words if w in text_lower)
        pos_count = sum(1 for w in positive_words if w in text_lower)

        if neg_count > pos_count:
            sentiment_score = 3
            sentiment_label = 'negative'
        elif pos_count > neg_count:
            sentiment_score = 7
            sentiment_label = 'positive'
        else:
            sentiment_score = 5
            sentiment_label = 'neutral'

        insights = []
        if error:
            insights.append(f"Note: Fallback analysis used ({error})")

        return LLMAnalysisResult(
            text=text,
            primary_pain_point=primary,
            secondary_pain_points=[],
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label,
            severity=5,
            switching_intent=False,
            switching_intent_confidence=0.0,
            key_quote=text[:100] if len(text) > 100 else text,
            insights=insights,
            raw_response=None
        )

    def _get_category_keywords(self, category: str) -> List[str]:
        """Get keywords for fallback matching."""
        keywords_map = {
            "Infection Risk": ["infection", "oozing", "cleaning", "wound", "bacteria"],
            "Form Factor": ["wire", "bulky", "cable", "tethered", "snagged"],
            "Social Stigma": ["staring", "robot", "visible", "embarrassed", "hide"],
            "Device Reliability": ["malfunction", "failure", "broke", "glitch", "error"],
            "Battery & Maintenance": ["battery", "charging", "dead", "replace", "power"],
            "Clinical Efficacy": ["accuracy", "control", "delay", "calibration", "signal"],
            "Cost & Access": ["expensive", "cost", "insurance", "afford", "price"],
            "Quality of Life": ["depression", "anxiety", "isolated", "frustrated", "exhausted"]
        }
        return keywords_map.get(category, [])

    def _generate_aggregate_insights(
        self,
        results: List[LLMAnalysisResult]
    ) -> List[str]:
        """Generate aggregate insights from batch results."""
        insights = []

        if not results:
            return ["No comments analyzed"]

        # Count pain points
        pain_point_counts = {}
        for r in results:
            if r.primary_pain_point and r.primary_pain_point != "Unknown":
                pain_point_counts[r.primary_pain_point] = \
                    pain_point_counts.get(r.primary_pain_point, 0) + 1

        if pain_point_counts:
            top_pain = max(pain_point_counts.items(), key=lambda x: x[1])
            insights.append(
                f"Primary pain point: {top_pain[0]} ({top_pain[1]}/{len(results)} comments)"
            )

        # Average sentiment
        avg_sentiment = sum(r.sentiment_score for r in results) / len(results)
        sentiment_desc = "negative" if avg_sentiment < 4 else "neutral" if avg_sentiment < 7 else "positive"
        insights.append(f"Average sentiment: {avg_sentiment:.1f}/10 ({sentiment_desc})")

        # Switching intent
        switching_count = sum(1 for r in results if r.switching_intent)
        if switching_count > 0:
            insights.append(
                f"Switching intent detected in {switching_count}/{len(results)} comments "
                f"({switching_count/len(results)*100:.0f}%)"
            )

        # High severity items
        high_severity = [r for r in results if r.severity >= 8]
        if high_severity:
            insights.append(
                f"High-severity concerns found in {len(high_severity)} comments - "
                f"requires attention"
            )

        return insights


def create_llm_analyzer(api_key: Optional[str] = None) -> LLMAnalyzer:
    """Factory function to create an LLM analyzer."""
    return LLMAnalyzer(api_key=api_key)
