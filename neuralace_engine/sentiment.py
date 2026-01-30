"""
Sentiment analysis module for Neuralace Patient Voice Engine.
Uses VADER (Valence Aware Dictionary and sEntiment Reasoner) for social media text.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False


@dataclass
class SentimentScore:
    """Container for sentiment analysis results."""
    positive: float      # Proportion of positive sentiment (0-1)
    negative: float      # Proportion of negative sentiment (0-1)
    neutral: float       # Proportion of neutral sentiment (0-1)
    compound: float      # Normalized compound score (-1 to 1)
    label: str          # 'positive', 'negative', or 'neutral'
    magnitude: float    # Strength of sentiment (0-1)


class SentimentAnalyzer:
    """
    Analyzes sentiment of patient comments using VADER.

    VADER is specifically tuned for social media text and handles:
    - Emoticons, emojis
    - Slang and abbreviations
    - Punctuation emphasis (!!!)
    - Capitalization for emphasis
    - Degree modifiers (very, extremely)
    - Negations
    """

    # Thresholds for sentiment classification
    POSITIVE_THRESHOLD = 0.05
    NEGATIVE_THRESHOLD = -0.05

    def __init__(self):
        """Initialize the VADER sentiment analyzer."""
        if not VADER_AVAILABLE:
            self._analyzer = None
        else:
            self._analyzer = SentimentIntensityAnalyzer()

    def analyze(self, text: str) -> SentimentScore:
        """
        Analyze sentiment of a single text.

        Args:
            text: The text to analyze

        Returns:
            SentimentScore with polarity and magnitude
        """
        if not self._analyzer or not text:
            return SentimentScore(
                positive=0.0,
                negative=0.0,
                neutral=1.0,
                compound=0.0,
                label='neutral',
                magnitude=0.0
            )

        scores = self._analyzer.polarity_scores(text)
        compound = scores['compound']

        # Classify sentiment
        if compound >= self.POSITIVE_THRESHOLD:
            label = 'positive'
        elif compound <= self.NEGATIVE_THRESHOLD:
            label = 'negative'
        else:
            label = 'neutral'

        # Calculate magnitude (absolute strength)
        magnitude = abs(compound)

        return SentimentScore(
            positive=scores['pos'],
            negative=scores['neg'],
            neutral=scores['neu'],
            compound=compound,
            label=label,
            magnitude=magnitude
        )

    def analyze_batch(self, texts: List[str]) -> List[SentimentScore]:
        """
        Analyze sentiment of multiple texts.

        Args:
            texts: List of texts to analyze

        Returns:
            List of SentimentScore objects
        """
        return [self.analyze(text) for text in texts]

    def is_pain_point(self, text: str, threshold: float = -0.1) -> Tuple[bool, SentimentScore]:
        """
        Determine if a text represents a valid pain point (negative sentiment).

        Filters out positive mentions like "BCI changed my life!" that
        shouldn't count as pain points even if they contain keywords.

        Args:
            text: The text to analyze
            threshold: Compound score below which is considered negative

        Returns:
            Tuple of (is_pain_point, sentiment_score)
        """
        score = self.analyze(text)
        is_negative = score.compound <= threshold
        return is_negative, score

    def get_sentiment_distribution(self, texts: List[str]) -> Dict[str, int]:
        """
        Get distribution of sentiment labels across texts.

        Args:
            texts: List of texts to analyze

        Returns:
            Dict with counts for each sentiment label
        """
        distribution = {'positive': 0, 'negative': 0, 'neutral': 0}
        for text in texts:
            score = self.analyze(text)
            distribution[score.label] += 1
        return distribution

    def filter_negative_only(self, data: List[Dict]) -> List[Dict]:
        """
        Filter data to only include items with negative sentiment.

        Useful for ensuring pain point analysis only considers
        actual complaints, not positive mentions with keywords.

        Args:
            data: List of dicts with 'text' key

        Returns:
            Filtered list containing only negative sentiment items
        """
        filtered = []
        for item in data:
            text = item.get('text', '')
            is_negative, score = self.is_pain_point(text)
            if is_negative:
                # Add sentiment score to item
                item_copy = item.copy()
                item_copy['sentiment'] = {
                    'compound': score.compound,
                    'label': score.label,
                    'magnitude': score.magnitude
                }
                filtered.append(item_copy)
        return filtered


def create_sentiment_analyzer() -> SentimentAnalyzer:
    """Factory function to create a sentiment analyzer."""
    return SentimentAnalyzer()
