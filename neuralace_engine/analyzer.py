"""
Pain point analysis logic for Neuralace Patient Voice Engine v2.0.

Enhanced with:
- 8 pain categories (expanded from 3)
- Negation handling
- Sentiment integration
- Confidence scoring
- Word boundary matching
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import re

from .sentiment import SentimentAnalyzer, SentimentScore


@dataclass
class CategoryMatch:
    """Container for a single category match."""
    category: str
    keywords_matched: List[str]
    confidence: float
    negated: bool
    sentiment: Optional[SentimentScore]


class PainPointAnalyzer:
    """
    Analyzes patient discussions for pain points related to BCI devices.

    Enhanced v2.0 features:
    - 8 pain categories covering full patient concern spectrum
    - Negation detection to filter false positives
    - Sentiment analysis integration
    - Confidence scoring based on keyword density
    """

    # Expanded to 8 risk bucket categories
    RISK_BUCKETS = {
        'Infection Risk': [
            'infection', 'infected', 'oozing', 'ooze', 'cleaning', 'clean',
            'saline', 'wound', 'crusty', 'pedestal', 'percutaneous', 'site',
            'bacteria', 'bacterial', 'sterile', 'pus', 'swelling', 'swollen',
            'irritation', 'irritated', 'sepsis', 'abscess', 'discharge'
        ],
        'Form Factor': [
            'bulky', 'wire', 'wires', 'wired', 'tethered', 'tether', 'cable',
            'cables', 'tangled', 'tangle', 'snagged', 'snag', 'snagging',
            'connector', 'connectors', 'external', 'plugged', 'heavy',
            'awkward', 'pillow', 'doorframe', 'uncomfortable', 'cumbersome'
        ],
        'Social Stigma': [
            'staring', 'stare', 'stares', 'visible', 'visibility', 'robot',
            'robotic', 'pointing', 'point', 'hide', 'hiding', 'hidden',
            'public', 'appearance', 'embarrassed', 'embarrassing', 'stigma',
            'weird', 'different', 'damaged', 'experiment', 'cyborg', 'freak'
        ],
        'Device Reliability': [
            'malfunction', 'malfunctioning', 'failure', 'failed', 'fails',
            'broke', 'broken', 'breaking', 'glitch', 'glitchy', 'bug', 'buggy',
            'crash', 'crashed', 'crashing', 'unreliable', 'inconsistent',
            'error', 'errors', 'defect', 'defective', 'faulty'
        ],
        'Battery & Maintenance': [
            'battery', 'batteries', 'charging', 'charge', 'charged', 'dead',
            'died', 'dying', 'replace', 'replacement', 'replacing', 'recharge',
            'power', 'powered', 'maintenance', 'maintain', 'upkeep', 'drain',
            'drained', 'draining', 'lifespan', 'longevity'
        ],
        'Clinical Efficacy': [
            'accuracy', 'accurate', 'inaccurate', 'control', 'controlling',
            'delay', 'delayed', 'latency', 'lag', 'lagging', 'precision',
            'imprecise', 'calibration', 'calibrate', 'calibrating', 'drift',
            'drifting', 'sensitivity', 'responsive', 'unresponsive', 'signal'
        ],
        'Cost & Access': [
            'expensive', 'cost', 'costs', 'costly', 'price', 'priced',
            'insurance', 'insurer', 'afford', 'affordable', 'unaffordable',
            'coverage', 'covered', 'payment', 'pay', 'paying', 'bill',
            'bills', 'financial', 'money', 'budget', 'copay', 'deductible'
        ],
        'Quality of Life': [
            'depression', 'depressed', 'depressing', 'anxiety', 'anxious',
            'isolated', 'isolation', 'lonely', 'loneliness', 'frustrated',
            'frustrating', 'frustration', 'hopeless', 'hopelessness', 'burden',
            'burdened', 'overwhelming', 'overwhelmed', 'exhausted', 'exhausting',
            'tired', 'fatigue', 'fatigued', 'stressed', 'stress', 'mental'
        ]
    }

    # Neuralace competitive advantages mapped to each pain point
    NEURALACE_ADVANTAGES = {
        'Infection Risk': 'Neuralace is FULLY IMPLANTED with no percutaneous connector, eliminating the infection pathway entirely',
        'Form Factor': 'Neuralace is WIRELESS with no external cables - complete freedom of movement, sleep on any side, no snagging hazards',
        'Social Stigma': 'Neuralace is INVISIBLE under the skin - no visible hardware means complete social normalcy and discretion',
        'Device Reliability': 'Neuralace uses next-generation hermetic packaging and redundant systems for industry-leading reliability',
        'Battery & Maintenance': 'Neuralace features wireless power transfer - no battery replacements, minimal maintenance burden',
        'Clinical Efficacy': 'Neuralace\'s high-density electrode array provides superior signal resolution and real-time adaptive calibration',
        'Cost & Access': 'Blackrock Neurotech is committed to expanding access through insurance partnerships and value-based care models',
        'Quality of Life': 'Neuralace restores independence and agency, with seamless integration that supports mental wellbeing'
    }

    # Words that negate the meaning of following keywords
    NEGATION_WORDS = {
        'not', 'no', 'never', 'without', "don't", "didn't", "doesn't",
        "isn't", "aren't", "wasn't", "weren't", "haven't", "hasn't",
        "won't", "wouldn't", "can't", "cannot", "couldn't", "shouldn't",
        'none', 'neither', 'nor', 'nothing', 'nobody', 'nowhere',
        'hardly', 'scarcely', 'barely', 'rarely', 'seldom'
    }

    # How many words before a keyword to check for negation
    NEGATION_WINDOW = 4

    def __init__(self, use_sentiment: bool = True):
        """
        Initialize the analyzer.

        Args:
            use_sentiment: Whether to filter by sentiment (default True)
        """
        self.use_sentiment = use_sentiment
        self._sentiment_analyzer = SentimentAnalyzer() if use_sentiment else None

        # Pre-compile regex patterns with word boundaries
        self._patterns = {}
        for category, keywords in self.RISK_BUCKETS.items():
            # Use word boundaries to prevent partial matches
            pattern = r'\b(' + '|'.join(re.escape(kw) for kw in keywords) + r')\b'
            self._patterns[category] = re.compile(pattern, re.IGNORECASE)

        # Compile negation pattern
        negation_pattern = r'\b(' + '|'.join(re.escape(w) for w in self.NEGATION_WORDS) + r')\b'
        self._negation_pattern = re.compile(negation_pattern, re.IGNORECASE)

    def analyze(self, data: List[Dict]) -> Dict:
        """
        Analyze patient data for pain points.

        Args:
            data: List of dicts with keys: text, source, timestamp, score

        Returns:
            Dict with:
                - categories: Dict of category -> {count, percentage, quotes, confidence_avg}
                - top_pain_point: str (category with highest count)
                - representative_quote: str (highest-scored quote from top category)
                - neuralace_advantage: str (advantage mapping for top pain point)
                - sentiment_distribution: Dict of sentiment label counts
                - total_analyzed: int
                - filtered_by_sentiment: int (if sentiment filtering enabled)
        """
        # Initialize category tracking
        categories = {
            category: {
                'count': 0,
                'percentage': 0.0,
                'quotes': [],
                'confidence_scores': [],
                'confidence_avg': 0.0
            }
            for category in self.RISK_BUCKETS.keys()
        }

        sentiment_distribution = {'positive': 0, 'negative': 0, 'neutral': 0}
        filtered_count = 0
        total_analyzed = len(data)

        # Handle empty data
        if not data:
            return self._empty_result(categories, sentiment_distribution)

        # Categorize each text
        total_matches = 0
        for item in data:
            text = item.get('text', '')
            score = item.get('score', 0)

            # Sentiment analysis
            sentiment = None
            if self._sentiment_analyzer:
                sentiment = self._sentiment_analyzer.analyze(text)
                sentiment_distribution[sentiment.label] += 1

                # Filter out positive mentions (not real pain points)
                if sentiment.compound > 0.1:  # Slightly positive or more
                    filtered_count += 1
                    continue

            # Get category matches with negation and confidence
            matches = self._categorize_text_advanced(text, sentiment)

            for match in matches:
                if match.negated:
                    continue  # Skip negated mentions

                categories[match.category]['count'] += 1
                categories[match.category]['quotes'].append({
                    'text': text,
                    'score': score,
                    'confidence': match.confidence,
                    'keywords': match.keywords_matched
                })
                categories[match.category]['confidence_scores'].append(match.confidence)
                total_matches += 1

        # Calculate percentages and average confidence
        if total_matches > 0:
            for category in categories:
                cat_data = categories[category]
                cat_data['percentage'] = round(
                    (cat_data['count'] / total_matches) * 100, 1
                )
                if cat_data['confidence_scores']:
                    cat_data['confidence_avg'] = round(
                        sum(cat_data['confidence_scores']) / len(cat_data['confidence_scores']),
                        3
                    )

        # Find top pain point (by count, then by confidence)
        top_pain_point = max(
            categories.keys(),
            key=lambda c: (categories[c]['count'], categories[c]['confidence_avg'])
        )

        # Handle case where all counts are zero
        if categories[top_pain_point]['count'] == 0:
            top_pain_point = None

        # Get representative quote (highest confidence * score from top category)
        representative_quote = ''
        if top_pain_point and categories[top_pain_point]['quotes']:
            best_quote = max(
                categories[top_pain_point]['quotes'],
                key=lambda q: q['score'] * q['confidence']
            )
            representative_quote = best_quote['text']

        # Get Neuralace advantage for top pain point
        neuralace_advantage = ''
        if top_pain_point:
            neuralace_advantage = self.NEURALACE_ADVANTAGES.get(top_pain_point, '')

        # Clean up quotes for output
        for category in categories:
            categories[category]['quotes'] = [
                {
                    'text': q['text'],
                    'confidence': q['confidence'],
                    'keywords': q['keywords']
                }
                for q in categories[category]['quotes']
            ]
            del categories[category]['confidence_scores']  # Remove internal tracking

        return {
            'categories': categories,
            'top_pain_point': top_pain_point,
            'representative_quote': representative_quote,
            'neuralace_advantage': neuralace_advantage,
            'sentiment_distribution': sentiment_distribution,
            'total_analyzed': total_analyzed,
            'filtered_by_sentiment': filtered_count
        }

    def _categorize_text_advanced(
        self,
        text: str,
        sentiment: Optional[SentimentScore] = None
    ) -> List[CategoryMatch]:
        """
        Advanced categorization with negation detection and confidence scoring.

        Args:
            text: The patient comment/post text
            sentiment: Pre-computed sentiment score (optional)

        Returns:
            List of CategoryMatch objects
        """
        matches = []
        words = text.lower().split()
        word_count = len(words) if words else 1

        for category, pattern in self._patterns.items():
            found_keywords = pattern.findall(text)
            if not found_keywords:
                continue

            # Check for negation
            negated = self._is_negated(text, found_keywords)

            # Calculate confidence
            unique_keywords = list(set(kw.lower() for kw in found_keywords))
            keyword_density = len(unique_keywords) / word_count

            # Base confidence from keyword density (0.1 to 0.5)
            base_confidence = min(0.5, keyword_density * 10)

            # Boost confidence with sentiment magnitude if available
            sentiment_boost = 0.0
            if sentiment and sentiment.label == 'negative':
                sentiment_boost = sentiment.magnitude * 0.3

            # Boost for multiple keyword matches
            multi_match_boost = min(0.2, (len(unique_keywords) - 1) * 0.1)

            confidence = min(1.0, base_confidence + sentiment_boost + multi_match_boost)

            matches.append(CategoryMatch(
                category=category,
                keywords_matched=unique_keywords,
                confidence=round(confidence, 3),
                negated=negated,
                sentiment=sentiment
            ))

        return matches

    def _is_negated(self, text: str, keywords: List[str]) -> bool:
        """
        Check if keywords are negated in the text.

        Args:
            text: The full text
            keywords: List of matched keywords

        Returns:
            True if keywords appear to be negated
        """
        text_lower = text.lower()
        words = text_lower.split()

        for keyword in keywords:
            keyword_lower = keyword.lower()
            try:
                # Find position of keyword
                for i, word in enumerate(words):
                    if keyword_lower in word:
                        # Check preceding words for negation
                        start = max(0, i - self.NEGATION_WINDOW)
                        preceding = words[start:i]
                        for neg_word in self.NEGATION_WORDS:
                            if neg_word in preceding:
                                return True
            except (ValueError, IndexError):
                continue

        return False

    def _categorize_text(self, text: str) -> List[str]:
        """
        Simple categorization (legacy compatibility).

        Args:
            text: The patient comment/post text

        Returns:
            List of category names that the text matches
        """
        matched = []
        for category, pattern in self._patterns.items():
            if pattern.search(text):
                matched.append(category)
        return matched

    def _empty_result(self, categories: Dict, sentiment_distribution: Dict) -> Dict:
        """Return empty result structure."""
        return {
            'categories': categories,
            'top_pain_point': None,
            'representative_quote': '',
            'neuralace_advantage': '',
            'sentiment_distribution': sentiment_distribution,
            'total_analyzed': 0,
            'filtered_by_sentiment': 0
        }

    def get_category_keywords(self, category: str) -> List[str]:
        """Get keywords for a specific category."""
        return self.RISK_BUCKETS.get(category, [])

    def get_all_categories(self) -> List[str]:
        """Get list of all category names."""
        return list(self.RISK_BUCKETS.keys())
