"""
Data ingestion layer for Neuralace Patient Voice Engine.
Supports live Reddit API and simulation mode with realistic mock data.
"""

from datetime import datetime, timedelta
from typing import List, Dict
import random


class PatientDataIngestor:
    """Ingests patient discussion data from Reddit communities."""

    # 23 high-fidelity mock comments based on real BCI patient experiences
    MOCK_COMMENTS = [
        # Infection Risk Category (6 comments)
        {
            "text": "The skin around my pedestal gets crusty and I have to clean it twice daily with saline",
            "category": "Infection Risk"
        },
        {
            "text": "Anyone else dealing with oozing around the connector site? My doctor says it's normal but...",
            "category": "Infection Risk"
        },
        {
            "text": "Third infection this year. The percutaneous connector is basically an open wound",
            "category": "Infection Risk"
        },
        {
            "text": "I hate washing my hair around the pedestal - terrified of getting water in there",
            "category": "Infection Risk"
        },
        {
            "text": "Cleaning the site is a 30-minute ritual every morning",
            "category": "Infection Risk"
        },
        {
            "text": "The infection risk alone makes me wonder if this was worth it",
            "category": "Infection Risk"
        },
        # Form Factor Category (7 comments)
        {
            "text": "The wire snagged on my pillow last night and pulled - absolutely terrifying",
            "category": "Form Factor"
        },
        {
            "text": "Can't sleep on my left side anymore because of the bulky connector",
            "category": "Form Factor"
        },
        {
            "text": "The cable management is ridiculous - I look like I'm plugged into the Matrix",
            "category": "Form Factor"
        },
        {
            "text": "Wires tangled around my wheelchair joystick AGAIN",
            "category": "Form Factor"
        },
        {
            "text": "This tethered setup means I can't move more than 3 feet from the computer",
            "category": "Form Factor"
        },
        {
            "text": "The external processor is so bulky I need special hats",
            "category": "Form Factor"
        },
        {
            "text": "Had to tape down the wires to avoid snagging on doorframes",
            "category": "Form Factor"
        },
        # Social Stigma Category (7 comments)
        {
            "text": "Kids at the mall were staring and pointing at my head",
            "category": "Social Stigma"
        },
        {
            "text": "My date asked if I was 'some kind of robot' - date over",
            "category": "Social Stigma"
        },
        {
            "text": "I avoid going out because of how visible this thing is",
            "category": "Social Stigma"
        },
        {
            "text": "People treat me differently now - the hardware makes me look 'damaged'",
            "category": "Social Stigma"
        },
        {
            "text": "Can't hide this thing under a hat - the connector sticks out",
            "category": "Social Stigma"
        },
        {
            "text": "I feel like a science experiment when I'm in public",
            "category": "Social Stigma"
        },
        {
            "text": "My grandson said I look like a robot - he won't hug me anymore",
            "category": "Social Stigma"
        },
        # Mixed/Ambiguous (3 comments)
        {
            "text": "Overall happy with the results but the maintenance is exhausting",
            "category": "Mixed"
        },
        {
            "text": "The BCI changed my life but I wish it was less visible",
            "category": "Mixed"
        },
        {
            "text": "Would trade anything for a fully implanted version without all these external parts",
            "category": "Mixed"
        },
    ]

    def __init__(self, mode: str = "simulation"):
        """
        Initialize the ingestor.

        Args:
            mode: "live" for Reddit API, "simulation" for mock data
        """
        self.mode = mode

    def fetch_data(self, subreddits: List[str], limit: int = 100) -> List[Dict]:
        """
        Fetch patient discussion data.

        Args:
            subreddits: List of subreddit names to fetch from
            limit: Maximum number of posts/comments to fetch

        Returns:
            List of dicts with keys: text, source, timestamp, score
        """
        if self.mode == "simulation":
            return self._fetch_simulation_data(subreddits, limit)
        elif self.mode == "live":
            return self._fetch_live_data(subreddits, limit)
        else:
            raise ValueError(f"Invalid mode: {self.mode}. Use 'simulation' or 'live'")

    def _fetch_simulation_data(self, subreddits: List[str], limit: int) -> List[Dict]:
        """Generate realistic mock data for testing and demos."""
        results = []
        base_time = datetime.now()

        for i, mock in enumerate(self.MOCK_COMMENTS):
            # Distribute across provided subreddits
            source = subreddits[i % len(subreddits)] if subreddits else "ALS"

            results.append({
                "text": mock["text"],
                "source": source,
                "timestamp": base_time - timedelta(hours=random.randint(1, 720)),
                "score": random.randint(5, 50)
            })

        return results[:limit] if limit < len(results) else results

    def _fetch_live_data(self, subreddits: List[str], limit: int) -> List[Dict]:
        """
        Fetch real data from Reddit using PRAW.

        Note: Requires PRAW credentials to be configured.
        Falls back to simulation mode if API is unavailable.
        """
        try:
            import praw

            # Placeholder for API credentials
            # In production, these would come from environment variables or config
            reddit = praw.Reddit(
                client_id="YOUR_CLIENT_ID",
                client_secret="YOUR_CLIENT_SECRET",
                user_agent="NeuralacePatientVoiceEngine/1.0"
            )

            results = []
            for subreddit_name in subreddits:
                subreddit = reddit.subreddit(subreddit_name)
                for submission in subreddit.hot(limit=limit // len(subreddits)):
                    results.append({
                        "text": submission.title + " " + (submission.selftext or ""),
                        "source": subreddit_name,
                        "timestamp": datetime.fromtimestamp(submission.created_utc),
                        "score": submission.score
                    })

                    # Also get top comments
                    submission.comments.replace_more(limit=0)
                    for comment in submission.comments[:5]:
                        results.append({
                            "text": comment.body,
                            "source": subreddit_name,
                            "timestamp": datetime.fromtimestamp(comment.created_utc),
                            "score": comment.score
                        })

            return results[:limit]

        except Exception as e:
            # Fallback to simulation if live mode fails
            print(f"Live mode unavailable ({e}), falling back to simulation")
            return self._fetch_simulation_data(subreddits, limit)
