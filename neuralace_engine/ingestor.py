"""
Data ingestion layer for Neuralace Patient Voice Engine.
Supports live Reddit API and simulation mode with realistic mock data.
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import random


# Comprehensive list of relevant subreddits for BCI/Neuralace research
RELEVANT_SUBREDDITS = {
    # Patient Communities (Primary)
    'patient': [
        'ALS',
        'spinalcordinjuries',
        'Paralysis',
        'disability',
        'stroke',
        'epilepsy',
        'Parkinsons',
        'Blind',
        'TBI',  # Traumatic Brain Injury
        'MultipleSclerosis',
    ],
    # BCI/Neurotech Discussions
    'tech': [
        'neuralink',
        'neuroscience',
        'Neurotechnology',
        'BCI',
        'biotech',
    ],
    # General Interest / Future Tech
    'general': [
        'Futurology',
        'transhumanism',
        'singularity',
        'medicine',
    ],
}

# Flatten for easy access
ALL_SUBREDDITS = (
    RELEVANT_SUBREDDITS['patient'] +
    RELEVANT_SUBREDDITS['tech'] +
    RELEVANT_SUBREDDITS['general']
)


class PatientDataIngestor:
    """Ingests patient discussion data from Reddit communities."""

    # Expanded mock comments covering all pain point categories
    MOCK_COMMENTS = [
        # Infection Risk Category
        {
            "text": "The skin around my pedestal gets crusty and I have to clean it twice daily with saline",
            "category": "Infection Risk",
            "subreddit": "spinalcordinjuries"
        },
        {
            "text": "Anyone else dealing with oozing around the connector site? My doctor says it's normal but...",
            "category": "Infection Risk",
            "subreddit": "ALS"
        },
        {
            "text": "Third infection this year. The percutaneous connector is basically an open wound that never heals",
            "category": "Infection Risk",
            "subreddit": "spinalcordinjuries"
        },
        {
            "text": "I hate washing my hair around the pedestal - terrified of getting water in there",
            "category": "Infection Risk",
            "subreddit": "Paralysis"
        },
        {
            "text": "Cleaning the site is a 30-minute ritual every morning. Worth it but exhausting",
            "category": "Infection Risk",
            "subreddit": "ALS"
        },
        {
            "text": "The infection risk alone makes me wonder if this was worth it some days",
            "category": "Infection Risk",
            "subreddit": "disability"
        },

        # Form Factor Category
        {
            "text": "The wire snagged on my pillow last night and pulled - absolutely terrifying experience",
            "category": "Form Factor",
            "subreddit": "spinalcordinjuries"
        },
        {
            "text": "Can't sleep on my left side anymore because of the bulky connector. Miss that",
            "category": "Form Factor",
            "subreddit": "Paralysis"
        },
        {
            "text": "The cable management is ridiculous - I look like I'm plugged into the Matrix lol",
            "category": "Form Factor",
            "subreddit": "neuralink"
        },
        {
            "text": "Wires tangled around my wheelchair joystick AGAIN. Third time this week",
            "category": "Form Factor",
            "subreddit": "spinalcordinjuries"
        },
        {
            "text": "This tethered setup means I can't move more than 3 feet from the computer",
            "category": "Form Factor",
            "subreddit": "ALS"
        },
        {
            "text": "The external processor is so bulky I need special hats to cover it",
            "category": "Form Factor",
            "subreddit": "disability"
        },
        {
            "text": "Had to tape down the wires to avoid snagging on doorframes constantly",
            "category": "Form Factor",
            "subreddit": "Paralysis"
        },

        # Social Stigma Category
        {
            "text": "Kids at the mall were staring and pointing at my head. I know they don't mean harm but...",
            "category": "Social Stigma",
            "subreddit": "disability"
        },
        {
            "text": "My date asked if I was 'some kind of robot' - yeah that date was over pretty quick",
            "category": "Social Stigma",
            "subreddit": "spinalcordinjuries"
        },
        {
            "text": "I avoid going out because of how visible this thing is. Becoming a hermit",
            "category": "Social Stigma",
            "subreddit": "ALS"
        },
        {
            "text": "People treat me differently now - the hardware makes me look 'damaged' to them",
            "category": "Social Stigma",
            "subreddit": "disability"
        },
        {
            "text": "Can't hide this thing under a hat - the connector sticks out no matter what",
            "category": "Social Stigma",
            "subreddit": "Paralysis"
        },
        {
            "text": "I feel like a science experiment when I'm in public with all this visible hardware",
            "category": "Social Stigma",
            "subreddit": "neuralink"
        },
        {
            "text": "My grandson said I look like a robot - he won't hug me anymore and it breaks my heart",
            "category": "Social Stigma",
            "subreddit": "ALS"
        },

        # Device Reliability Category
        {
            "text": "Signal dropped out during an important video call with my doctor. So frustrating",
            "category": "Device Reliability",
            "subreddit": "ALS"
        },
        {
            "text": "The calibration drifts every few hours - have to recalibrate 3-4 times daily",
            "category": "Device Reliability",
            "subreddit": "spinalcordinjuries"
        },
        {
            "text": "Lost control for 10 seconds yesterday. When you can't move anyway, those seconds feel like hours",
            "category": "Device Reliability",
            "subreddit": "Paralysis"
        },
        {
            "text": "Electrode degradation is real - my accuracy has dropped 20% over 18 months",
            "category": "Device Reliability",
            "subreddit": "neuralink"
        },

        # Battery & Maintenance Category
        {
            "text": "Battery only lasts 4 hours. I have to plan my whole day around charging",
            "category": "Battery & Maintenance",
            "subreddit": "spinalcordinjuries"
        },
        {
            "text": "The maintenance schedule is basically a part-time job at this point",
            "category": "Battery & Maintenance",
            "subreddit": "ALS"
        },
        {
            "text": "Charger broke and I was without my BCI for 3 days waiting for replacement. Terrifying",
            "category": "Battery & Maintenance",
            "subreddit": "disability"
        },

        # Clinical Efficacy Category
        {
            "text": "Only getting 5 words per minute. They promised faster but reality is different",
            "category": "Clinical Efficacy",
            "subreddit": "ALS"
        },
        {
            "text": "The cursor control is good for basic tasks but forget about anything precise",
            "category": "Clinical Efficacy",
            "subreddit": "spinalcordinjuries"
        },
        {
            "text": "Took 6 months of training before I could type reliably. That's a long learning curve",
            "category": "Clinical Efficacy",
            "subreddit": "Paralysis"
        },

        # Cost & Access Category
        {
            "text": "Insurance denied coverage AGAIN. $150k out of pocket is not happening",
            "category": "Cost & Access",
            "subreddit": "ALS"
        },
        {
            "text": "The closest BCI clinic is 400 miles away. Every checkup is a 2-day trip",
            "category": "Cost & Access",
            "subreddit": "disability"
        },
        {
            "text": "Medicare doesn't cover this and I'm drowning in medical debt already",
            "category": "Cost & Access",
            "subreddit": "spinalcordinjuries"
        },

        # Quality of Life Category
        {
            "text": "Despite all the issues, this BCI gave me back my ability to communicate with family",
            "category": "Quality of Life",
            "subreddit": "ALS"
        },
        {
            "text": "Would I do it again? Yes. But I wish the tech was further along",
            "category": "Quality of Life",
            "subreddit": "spinalcordinjuries"
        },
        {
            "text": "The independence it gives me outweighs the hassles, but barely some days",
            "category": "Quality of Life",
            "subreddit": "Paralysis"
        },

        # Neuralink/Competitor Mentions
        {
            "text": "Watching Neuralink progress closely. Hope their wireless design actually works as promised",
            "category": "Competitor Mention",
            "subreddit": "neuralink"
        },
        {
            "text": "Synchron's endovascular approach sounds less scary than open brain surgery tbh",
            "category": "Competitor Mention",
            "subreddit": "Futurology"
        },
        {
            "text": "Anyone know about Blackrock's new Neuralace? 10,000 channels sounds incredible if true",
            "category": "Competitor Mention",
            "subreddit": "neuroscience"
        },
        {
            "text": "The fact that current BCIs still need wires in 2025 is ridiculous. Where's the wireless future?",
            "category": "Form Factor",
            "subreddit": "transhumanism"
        },
    ]

    def __init__(self, mode: str = "simulation"):
        """
        Initialize the ingestor.

        Args:
            mode: "live" for Reddit API, "simulation" for mock data
        """
        self.mode = mode

    def fetch_data(self, subreddits: List[str], limit: int = 100,
                   search_terms: Optional[List[str]] = None) -> List[Dict]:
        """
        Fetch patient discussion data.

        Args:
            subreddits: List of subreddit names to fetch from
            limit: Maximum number of posts/comments to fetch
            search_terms: Optional search terms to filter results (for live mode)

        Returns:
            List of dicts with keys: text, source, timestamp, score
        """
        if self.mode == "simulation":
            return self._fetch_simulation_data(subreddits, limit)
        elif self.mode == "live":
            return self._fetch_live_data(subreddits, limit, search_terms)
        else:
            raise ValueError(f"Invalid mode: {self.mode}. Use 'simulation' or 'live'")

    def _fetch_simulation_data(self, subreddits: List[str], limit: int) -> List[Dict]:
        """Generate realistic mock data for testing and demos."""
        results = []
        base_time = datetime.now()

        # Filter mock comments to requested subreddits if specified
        filtered_mocks = self.MOCK_COMMENTS
        if subreddits:
            subreddit_set = set(s.lower() for s in subreddits)
            filtered_mocks = [
                m for m in self.MOCK_COMMENTS
                if m.get('subreddit', '').lower() in subreddit_set
            ]
            # If no matches, use all mocks but assign to requested subreddits
            if not filtered_mocks:
                filtered_mocks = self.MOCK_COMMENTS

        for i, mock in enumerate(filtered_mocks):
            # Use mock's subreddit or distribute across provided subreddits
            if mock.get('subreddit', '').lower() in [s.lower() for s in subreddits]:
                source = mock['subreddit']
            else:
                source = subreddits[i % len(subreddits)] if subreddits else "ALS"

            results.append({
                "text": mock["text"],
                "source": source,
                "timestamp": base_time - timedelta(hours=random.randint(1, 720)),
                "score": random.randint(5, 100)
            })

        return results[:limit] if limit < len(results) else results

    def _fetch_live_data(self, subreddits: List[str], limit: int,
                         search_terms: Optional[List[str]] = None) -> List[Dict]:
        """
        Fetch real data from Reddit using PRAW.

        Credentials are read from:
        1. Streamlit secrets (secrets.toml)
        2. Environment variables
        """
        try:
            import praw
            import streamlit as st

            # Try to get credentials from Streamlit secrets first, then env vars
            try:
                client_id = st.secrets.get("REDDIT_CLIENT_ID", os.environ.get("REDDIT_CLIENT_ID"))
                client_secret = st.secrets.get("REDDIT_CLIENT_SECRET", os.environ.get("REDDIT_CLIENT_SECRET"))
                user_agent = st.secrets.get("REDDIT_USER_AGENT", os.environ.get("REDDIT_USER_AGENT", "BCI-Intelligence-Hub/2.0"))
            except Exception:
                # Not running in Streamlit context
                client_id = os.environ.get("REDDIT_CLIENT_ID")
                client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
                user_agent = os.environ.get("REDDIT_USER_AGENT", "BCI-Intelligence-Hub/2.0")

            if not client_id or not client_secret:
                print("Reddit API credentials not found. Falling back to simulation mode.")
                return self._fetch_simulation_data(subreddits, limit)

            reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )

            results = []
            posts_per_subreddit = max(10, limit // len(subreddits)) if subreddits else limit

            for subreddit_name in subreddits:
                try:
                    subreddit = reddit.subreddit(subreddit_name)

                    # Search with terms if provided, otherwise get hot posts
                    if search_terms:
                        query = ' OR '.join(search_terms)
                        submissions = subreddit.search(query, limit=posts_per_subreddit, time_filter='year')
                    else:
                        submissions = subreddit.hot(limit=posts_per_subreddit)

                    for submission in submissions:
                        # Add post
                        text = submission.title
                        if submission.selftext:
                            text += " " + submission.selftext

                        results.append({
                            "text": text,
                            "source": subreddit_name,
                            "timestamp": datetime.fromtimestamp(submission.created_utc),
                            "score": submission.score,
                            "url": f"https://reddit.com{submission.permalink}"
                        })

                        # Get top comments
                        try:
                            submission.comments.replace_more(limit=0)
                            for comment in submission.comments[:3]:
                                if hasattr(comment, 'body') and len(comment.body) > 20:
                                    results.append({
                                        "text": comment.body,
                                        "source": subreddit_name,
                                        "timestamp": datetime.fromtimestamp(comment.created_utc),
                                        "score": comment.score,
                                        "url": f"https://reddit.com{submission.permalink}"
                                    })
                        except Exception:
                            pass  # Skip comment errors

                except Exception as e:
                    print(f"Error fetching from r/{subreddit_name}: {e}")
                    continue

            return results[:limit] if results else self._fetch_simulation_data(subreddits, limit)

        except ImportError:
            print("PRAW not installed. Install with: pip install praw")
            return self._fetch_simulation_data(subreddits, limit)
        except Exception as e:
            print(f"Live mode error ({e}), falling back to simulation")
            return self._fetch_simulation_data(subreddits, limit)


def get_all_subreddits() -> List[str]:
    """Get list of all relevant subreddits."""
    return ALL_SUBREDDITS


def get_subreddits_by_category(category: str) -> List[str]:
    """Get subreddits for a specific category."""
    return RELEVANT_SUBREDDITS.get(category, [])
