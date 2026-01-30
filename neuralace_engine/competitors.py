"""
Competitor tracking module for Neuralace Patient Voice Engine.

Tracks mentions of competing BCI technologies:
- Neuralink
- Synchron (Stentrode)
- BrainGate
- Paradromics
- Other Utah Array implementations
"""

from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
import re
from collections import defaultdict


@dataclass
class CompetitorMention:
    """A single competitor mention in patient data."""
    competitor: str
    text: str
    context: str  # Surrounding sentence/phrase
    sentiment: str  # 'positive', 'negative', 'neutral'
    pain_points_mentioned: List[str]
    switching_intent: bool


@dataclass
class CompetitorProfile:
    """Profile of a competitor based on patient mentions."""
    name: str
    mention_count: int
    percentage: float
    sentiment_breakdown: Dict[str, int]
    associated_pain_points: Dict[str, int]
    switching_intent_count: int
    sample_quotes: List[str]


@dataclass
class CompetitorReport:
    """Complete competitor analysis report."""
    total_competitor_mentions: int
    competitors: Dict[str, CompetitorProfile]
    most_mentioned: Optional[str]
    most_positive_sentiment: Optional[str]
    highest_switching_intent: Optional[str]
    competitive_landscape: str  # Summary analysis


class CompetitorAnalyzer:
    """
    Analyzes patient discussions for competitor mentions.

    Tracks which competing technologies patients discuss,
    their sentiment toward them, and switching intent signals.
    """

    # Competitor definitions with aliases
    COMPETITORS = {
        'Neuralink': {
            'patterns': [
                r'\bneuralink\b', r'\belon\s*musk\b.*bci', r'\bn[1l]\b',
                r'\btesla\s*brain\b'
            ],
            'type': 'emerging',
            'notes': 'High-profile, consumer-focused BCI'
        },
        'Synchron': {
            'patterns': [
                r'\bsynchron\b', r'\bstentrode\b', r'\bstent\s*electrode\b',
                r'\bendovascular\b.*bci'
            ],
            'type': 'emerging',
            'notes': 'Minimally invasive, blood vessel based'
        },
        'BrainGate': {
            'patterns': [
                r'\bbraingate\b', r'\bbrain\s*gate\b', r'\bbrown\s*university\b.*bci',
                r'\bmgh\b.*bci'
            ],
            'type': 'research',
            'notes': 'Academic research consortium'
        },
        'Paradromics': {
            'patterns': [
                r'\bparadromics\b', r'\bconnexus\b'
            ],
            'type': 'emerging',
            'notes': 'High-bandwidth neural interface'
        },
        'Utah Array': {
            'patterns': [
                r'\butah\s*array\b', r'\bblackrock\s*array\b',
                r'\bmicroelectrode\s*array\b', r'\bmea\b'
            ],
            'type': 'established',
            'notes': 'Current standard, used by multiple groups'
        },
        'Kernel': {
            'patterns': [
                r'\bkernel\b.*neuro', r'\bkernel\s*flow\b'
            ],
            'type': 'emerging',
            'notes': 'Non-invasive neuroimaging'
        },
        'Precision Neuroscience': {
            'patterns': [
                r'\bprecision\s*neuroscience\b', r'\blayer\s*7\b'
            ],
            'type': 'emerging',
            'notes': 'Thin-film electrode arrays'
        }
    }

    # Switching intent signals
    SWITCHING_INTENT_PATTERNS = [
        r'wish\s*(i|we)\s*(had|could|can)',
        r'switch(ing)?\s*to',
        r'waiting\s*for',
        r'hope\s*(to|for)',
        r'can\'t\s*wait\s*for',
        r'better\s*than\s*(this|my|current)',
        r'upgrade\s*to',
        r'considering',
        r'looking\s*at',
        r'interested\s*in',
        r'when\s*(will|can|is)',
        r'rather\s*have'
    ]

    def __init__(self):
        """Initialize the competitor analyzer."""
        # Compile patterns
        self._competitor_patterns = {}
        for comp, info in self.COMPETITORS.items():
            combined = '|'.join(info['patterns'])
            self._competitor_patterns[comp] = re.compile(combined, re.IGNORECASE)

        self._switching_pattern = re.compile(
            '|'.join(self.SWITCHING_INTENT_PATTERNS),
            re.IGNORECASE
        )

    def analyze(self, data: List[Dict]) -> CompetitorReport:
        """
        Analyze patient data for competitor mentions.

        Args:
            data: List of dicts with 'text' key

        Returns:
            CompetitorReport with competitor analysis
        """
        mentions = defaultdict(list)  # competitor -> list of CompetitorMention
        total_mentions = 0

        for item in data:
            text = item.get('text', '')
            if not text:
                continue

            # Check for each competitor
            for competitor, pattern in self._competitor_patterns.items():
                if pattern.search(text):
                    mention = self._extract_mention(text, competitor, item)
                    mentions[competitor].append(mention)
                    total_mentions += 1

        # Build competitor profiles
        competitors = {}
        for comp, mention_list in mentions.items():
            competitors[comp] = self._build_profile(comp, mention_list, total_mentions)

        # Find superlatives
        most_mentioned = max(
            competitors.keys(),
            key=lambda c: competitors[c].mention_count,
            default=None
        ) if competitors else None

        most_positive = self._find_most_positive(competitors)
        highest_switching = self._find_highest_switching(competitors)

        # Generate landscape summary
        landscape = self._generate_landscape_summary(competitors, total_mentions)

        return CompetitorReport(
            total_competitor_mentions=total_mentions,
            competitors=competitors,
            most_mentioned=most_mentioned,
            most_positive_sentiment=most_positive,
            highest_switching_intent=highest_switching,
            competitive_landscape=landscape
        )

    def _extract_mention(
        self,
        text: str,
        competitor: str,
        item: Dict
    ) -> CompetitorMention:
        """Extract details about a competitor mention."""
        # Get sentiment (simplified - could integrate with SentimentAnalyzer)
        sentiment = self._simple_sentiment(text)

        # Check for switching intent
        switching_intent = bool(self._switching_pattern.search(text))

        # Extract context (sentence containing mention)
        context = self._extract_context(text, competitor)

        # Check for pain points mentioned alongside
        pain_points = self._extract_pain_points(text)

        return CompetitorMention(
            competitor=competitor,
            text=text,
            context=context,
            sentiment=sentiment,
            pain_points_mentioned=pain_points,
            switching_intent=switching_intent
        )

    def _simple_sentiment(self, text: str) -> str:
        """Simple keyword-based sentiment detection."""
        text_lower = text.lower()

        positive_words = {
            'love', 'great', 'amazing', 'better', 'best', 'excited',
            'hope', 'promising', 'innovative', 'impressed', 'revolutionary'
        }
        negative_words = {
            'hate', 'terrible', 'worse', 'worst', 'disappointed',
            'skeptical', 'doubt', 'concern', 'worried', 'scary', 'risky'
        }

        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)

        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        return 'neutral'

    def _extract_context(self, text: str, competitor: str) -> str:
        """Extract the sentence containing the competitor mention."""
        sentences = re.split(r'[.!?]', text)
        for sentence in sentences:
            if competitor.lower() in sentence.lower():
                return sentence.strip()
            # Check patterns too
            if self._competitor_patterns[competitor].search(sentence):
                return sentence.strip()
        return text[:200]  # Fallback to first 200 chars

    def _extract_pain_points(self, text: str) -> List[str]:
        """Extract pain point categories mentioned in text."""
        from .analyzer import PainPointAnalyzer
        analyzer = PainPointAnalyzer(use_sentiment=False)
        return analyzer._categorize_text(text)

    def _build_profile(
        self,
        competitor: str,
        mentions: List[CompetitorMention],
        total: int
    ) -> CompetitorProfile:
        """Build a competitor profile from mentions."""
        sentiment_breakdown = {'positive': 0, 'negative': 0, 'neutral': 0}
        pain_point_counts = defaultdict(int)
        switching_count = 0
        quotes = []

        for mention in mentions:
            sentiment_breakdown[mention.sentiment] += 1
            if mention.switching_intent:
                switching_count += 1
            for pp in mention.pain_points_mentioned:
                pain_point_counts[pp] += 1
            if len(quotes) < 3:  # Keep up to 3 sample quotes
                quotes.append(mention.context[:150])

        percentage = (len(mentions) / total * 100) if total > 0 else 0

        return CompetitorProfile(
            name=competitor,
            mention_count=len(mentions),
            percentage=round(percentage, 1),
            sentiment_breakdown=dict(sentiment_breakdown),
            associated_pain_points=dict(pain_point_counts),
            switching_intent_count=switching_count,
            sample_quotes=quotes
        )

    def _find_most_positive(self, competitors: Dict[str, CompetitorProfile]) -> Optional[str]:
        """Find competitor with highest positive sentiment ratio."""
        best = None
        best_ratio = 0

        for name, profile in competitors.items():
            total = sum(profile.sentiment_breakdown.values())
            if total > 0:
                ratio = profile.sentiment_breakdown['positive'] / total
                if ratio > best_ratio:
                    best_ratio = ratio
                    best = name

        return best

    def _find_highest_switching(self, competitors: Dict[str, CompetitorProfile]) -> Optional[str]:
        """Find competitor with highest switching intent."""
        best = None
        best_count = 0

        for name, profile in competitors.items():
            if profile.switching_intent_count > best_count:
                best_count = profile.switching_intent_count
                best = name

        return best

    def _generate_landscape_summary(
        self,
        competitors: Dict[str, CompetitorProfile],
        total: int
    ) -> str:
        """Generate a summary of the competitive landscape."""
        if not competitors:
            return "No competitor mentions detected in the analyzed data."

        parts = []
        parts.append(f"Detected {total} competitor mentions across {len(competitors)} technologies.")

        # Most discussed
        sorted_comps = sorted(
            competitors.items(),
            key=lambda x: x[1].mention_count,
            reverse=True
        )

        if sorted_comps:
            top = sorted_comps[0]
            parts.append(
                f"Most discussed: {top[0]} ({top[1].mention_count} mentions, "
                f"{top[1].percentage:.1f}% of competitor discussions)."
            )

        # Switching intent
        total_switching = sum(c.switching_intent_count for c in competitors.values())
        if total_switching > 0:
            parts.append(
                f"Switching intent detected in {total_switching} mentions - "
                f"indicates patient interest in alternative technologies."
            )

        return " ".join(parts)

    def get_competitor_list(self) -> List[str]:
        """Get list of tracked competitors."""
        return list(self.COMPETITORS.keys())

    def get_competitor_info(self, competitor: str) -> Optional[Dict]:
        """Get information about a specific competitor."""
        return self.COMPETITORS.get(competitor)


def create_competitor_analyzer() -> CompetitorAnalyzer:
    """Factory function to create a competitor analyzer."""
    return CompetitorAnalyzer()
