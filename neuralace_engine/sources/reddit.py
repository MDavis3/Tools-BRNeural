"""
Reddit data source for Neuralace Patient Voice Engine.

Fetches patient discussions from subreddits like r/ALS, r/spinalcordinjuries.
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import random
import os

from .base import DataSource, DataItem, SourceType

try:
    import praw
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False


class RedditSource(DataSource):
    """
    Reddit data source using PRAW.

    Fetches patient discussions from BCI-related subreddits.
    """

    # Default target subreddits for BCI patient communities
    DEFAULT_SUBREDDITS = [
        'ALS',
        'spinalcordinjuries',
        'disability',
        'paralysis',
        'strokesurvivors'
    ]

    # High-fidelity mock data for simulation
    MOCK_COMMENTS = [
        # Infection Risk
        {"text": "The skin around my pedestal gets crusty and I have to clean it twice daily with saline", "category": "Infection Risk"},
        {"text": "Anyone else dealing with oozing around the connector site? My doctor says it's normal but...", "category": "Infection Risk"},
        {"text": "Third infection this year. The percutaneous connector is basically an open wound", "category": "Infection Risk"},
        {"text": "I hate washing my hair around the pedestal - terrified of getting water in there", "category": "Infection Risk"},
        {"text": "Cleaning the site is a 30-minute ritual every morning", "category": "Infection Risk"},
        {"text": "The infection risk alone makes me wonder if this was worth it", "category": "Infection Risk"},
        # Form Factor
        {"text": "The wire snagged on my pillow last night and pulled - absolutely terrifying", "category": "Form Factor"},
        {"text": "Can't sleep on my left side anymore because of the bulky connector", "category": "Form Factor"},
        {"text": "The cable management is ridiculous - I look like I'm plugged into the Matrix", "category": "Form Factor"},
        {"text": "Wires tangled around my wheelchair joystick AGAIN", "category": "Form Factor"},
        {"text": "This tethered setup means I can't move more than 3 feet from the computer", "category": "Form Factor"},
        {"text": "The external processor is so bulky I need special hats", "category": "Form Factor"},
        {"text": "Had to tape down the wires to avoid snagging on doorframes", "category": "Form Factor"},
        # Social Stigma
        {"text": "Kids at the mall were staring and pointing at my head", "category": "Social Stigma"},
        {"text": "My date asked if I was 'some kind of robot' - date over", "category": "Social Stigma"},
        {"text": "I avoid going out because of how visible this thing is", "category": "Social Stigma"},
        {"text": "People treat me differently now - the hardware makes me look 'damaged'", "category": "Social Stigma"},
        {"text": "Can't hide this thing under a hat - the connector sticks out", "category": "Social Stigma"},
        {"text": "I feel like a science experiment when I'm in public", "category": "Social Stigma"},
        {"text": "My grandson said I look like a robot - he won't hug me anymore", "category": "Social Stigma"},
        # Device Reliability
        {"text": "The device crashed in the middle of my job interview - mortifying", "category": "Device Reliability"},
        {"text": "Third malfunction this month. I can't rely on this thing", "category": "Device Reliability"},
        {"text": "Signal keeps dropping. The glitches are getting worse", "category": "Device Reliability"},
        # Battery & Maintenance
        {"text": "Battery died during a phone call with my daughter. Again.", "category": "Battery"},
        {"text": "Charging this thing is a 4-hour process every night", "category": "Battery"},
        {"text": "Had to replace the battery module - insurance only covered half", "category": "Battery"},
        # Clinical Efficacy
        {"text": "The control accuracy varies so much day to day", "category": "Clinical"},
        {"text": "Calibration takes forever and drifts within an hour", "category": "Clinical"},
        {"text": "The latency makes real-time communication impossible", "category": "Clinical"},
        # Cost & Access
        {"text": "Insurance denied coverage for the replacement parts", "category": "Cost"},
        {"text": "The out-of-pocket costs are destroying our savings", "category": "Cost"},
        {"text": "Waited 18 months just to get approved for the trial", "category": "Cost"},
        # Quality of Life
        {"text": "The depression from dealing with all this is overwhelming", "category": "QoL"},
        {"text": "I'm exhausted from the constant maintenance routine", "category": "QoL"},
        {"text": "Feel more isolated now than before the implant", "category": "QoL"},
        # Mixed/Hopeful
        {"text": "Overall happy with the results but the maintenance is exhausting", "category": "Mixed"},
        {"text": "The BCI changed my life but I wish it was less visible", "category": "Mixed"},
        {"text": "Would trade anything for a fully implanted version without all these external parts", "category": "Mixed"},
        {"text": "Heard about Neuralink - when will that be available for ALS patients?", "category": "Competitor"},
        {"text": "Waiting for Synchron's device - the minimally invasive approach sounds promising", "category": "Competitor"},
    ]

    def __init__(self):
        """Initialize the Reddit source."""
        super().__init__(name="reddit", source_type=SourceType.SOCIAL_MEDIA)
        self._reddit = None
        self._client_id = None
        self._client_secret = None

    def configure(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        user_agent: str = "NeuralacePatientVoiceEngine/2.0"
    ) -> bool:
        """
        Configure Reddit API credentials.

        Args:
            client_id: Reddit API client ID
            client_secret: Reddit API client secret
            user_agent: User agent string

        Returns:
            True if configuration successful
        """
        self._client_id = client_id or os.getenv('REDDIT_CLIENT_ID')
        self._client_secret = client_secret or os.getenv('REDDIT_CLIENT_SECRET')

        if not PRAW_AVAILABLE:
            self._is_configured = False
            return False

        if self._client_id and self._client_secret:
            try:
                self._reddit = praw.Reddit(
                    client_id=self._client_id,
                    client_secret=self._client_secret,
                    user_agent=user_agent
                )
                self._is_configured = True
                return True
            except Exception:
                self._is_configured = False
                return False

        self._is_configured = False
        return False

    def is_available(self) -> bool:
        """Check if Reddit API is available."""
        return self._is_configured and self._reddit is not None

    def fetch(
        self,
        query: str = "",
        limit: int = 100,
        subreddits: Optional[List[str]] = None,
        sort: str = "hot"
    ) -> List[DataItem]:
        """
        Fetch posts and comments from Reddit.

        Args:
            query: Search query (optional)
            limit: Maximum items to fetch
            subreddits: List of subreddit names
            sort: Sort order (hot, new, top)

        Returns:
            List of DataItem objects
        """
        if not self.is_available():
            return self.get_mock_data(limit)

        subreddits = subreddits or self.DEFAULT_SUBREDDITS
        items = []

        try:
            for sub_name in subreddits:
                subreddit = self._reddit.subreddit(sub_name)

                # Get submissions
                if sort == "hot":
                    submissions = subreddit.hot(limit=limit // len(subreddits))
                elif sort == "new":
                    submissions = subreddit.new(limit=limit // len(subreddits))
                else:
                    submissions = subreddit.top(limit=limit // len(subreddits))

                for submission in submissions:
                    # Add submission
                    items.append(DataItem(
                        text=f"{submission.title} {submission.selftext or ''}".strip(),
                        source="reddit",
                        source_id=submission.id,
                        timestamp=datetime.fromtimestamp(submission.created_utc),
                        url=f"https://reddit.com{submission.permalink}",
                        title=submission.title,
                        author=str(submission.author) if submission.author else None,
                        score=submission.score,
                        metadata={
                            'subreddit': sub_name,
                            'type': 'submission',
                            'num_comments': submission.num_comments
                        }
                    ))

                    # Add top comments
                    submission.comments.replace_more(limit=0)
                    for comment in submission.comments[:5]:
                        items.append(DataItem(
                            text=comment.body,
                            source="reddit",
                            source_id=comment.id,
                            timestamp=datetime.fromtimestamp(comment.created_utc),
                            url=f"https://reddit.com{comment.permalink}",
                            author=str(comment.author) if comment.author else None,
                            score=comment.score,
                            metadata={
                                'subreddit': sub_name,
                                'type': 'comment',
                                'parent_id': submission.id
                            }
                        ))

        except Exception as e:
            print(f"Reddit fetch error: {e}")
            return self.get_mock_data(limit)

        return items[:limit]

    def get_mock_data(self, limit: int = 20) -> List[DataItem]:
        """Generate mock Reddit data for testing."""
        items = []
        base_time = datetime.now()

        for i, mock in enumerate(self.MOCK_COMMENTS[:limit]):
            subreddit = random.choice(self.DEFAULT_SUBREDDITS)
            items.append(DataItem(
                text=mock['text'],
                source="reddit",
                source_id=f"mock_{i}",
                timestamp=base_time - timedelta(hours=random.randint(1, 720)),
                url=f"https://reddit.com/r/{subreddit}/comments/mock_{i}",
                author=f"user_{random.randint(1000, 9999)}",
                score=random.randint(5, 100),
                metadata={
                    'subreddit': subreddit,
                    'type': 'comment',
                    'is_mock': True,
                    'category_hint': mock.get('category')
                }
            ))

        return items


def create_reddit_source() -> RedditSource:
    """Factory function to create a Reddit source."""
    return RedditSource()
