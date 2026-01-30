"""
Base class for data sources in Neuralace Patient Voice Engine.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class SourceType(Enum):
    """Types of data sources."""
    SOCIAL_MEDIA = "social_media"
    CLINICAL_LITERATURE = "clinical_literature"
    CLINICAL_TRIALS = "clinical_trials"
    NEWS = "news"
    FORUM = "forum"


@dataclass
class DataItem:
    """
    Standardized data item from any source.

    All sources produce DataItems in this format for
    consistent analysis across the pipeline.
    """
    text: str                          # Main content
    source: str                        # Source identifier (e.g., "reddit", "pubmed")
    source_id: str                     # Unique ID within source
    timestamp: datetime                # Publication/creation time
    url: Optional[str] = None          # Link to original
    title: Optional[str] = None        # Title if applicable
    author: Optional[str] = None       # Author/username
    score: int = 0                     # Engagement/relevance score
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary for analysis."""
        return {
            'text': self.text,
            'source': self.source,
            'source_id': self.source_id,
            'timestamp': self.timestamp,
            'url': self.url,
            'title': self.title,
            'author': self.author,
            'score': self.score,
            'metadata': self.metadata
        }


class DataSource(ABC):
    """
    Abstract base class for data sources.

    All data sources must implement this interface
    to ensure consistent data fetching and formatting.
    """

    def __init__(self, name: str, source_type: SourceType):
        """
        Initialize the data source.

        Args:
            name: Human-readable source name
            source_type: Type of source (social_media, clinical, etc.)
        """
        self.name = name
        self.source_type = source_type
        self._is_configured = False

    @abstractmethod
    def configure(self, **kwargs) -> bool:
        """
        Configure the data source with credentials/settings.

        Args:
            **kwargs: Source-specific configuration

        Returns:
            True if configuration successful
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the source is available and properly configured.

        Returns:
            True if source can be used
        """
        pass

    @abstractmethod
    def fetch(
        self,
        query: str,
        limit: int = 100,
        **kwargs
    ) -> List[DataItem]:
        """
        Fetch data from the source.

        Args:
            query: Search query or topic
            limit: Maximum items to fetch
            **kwargs: Source-specific parameters

        Returns:
            List of DataItem objects
        """
        pass

    @abstractmethod
    def get_mock_data(self, limit: int = 20) -> List[DataItem]:
        """
        Generate mock data for testing/demo.

        Args:
            limit: Number of mock items to generate

        Returns:
            List of mock DataItem objects
        """
        pass

    def fetch_or_mock(
        self,
        query: str,
        limit: int = 100,
        **kwargs
    ) -> List[DataItem]:
        """
        Fetch real data if available, otherwise return mock data.

        Args:
            query: Search query
            limit: Maximum items
            **kwargs: Additional parameters

        Returns:
            List of DataItem objects (real or mock)
        """
        if self.is_available():
            return self.fetch(query, limit, **kwargs)
        return self.get_mock_data(limit)

    def __repr__(self) -> str:
        status = "configured" if self._is_configured else "not configured"
        return f"{self.__class__.__name__}(name='{self.name}', status='{status}')"


class AggregatedSource:
    """
    Aggregates multiple data sources into a unified interface.
    """

    def __init__(self):
        """Initialize the aggregator."""
        self.sources: Dict[str, DataSource] = {}

    def add_source(self, source: DataSource) -> None:
        """Add a data source to the aggregator."""
        self.sources[source.name] = source

    def remove_source(self, name: str) -> None:
        """Remove a data source from the aggregator."""
        if name in self.sources:
            del self.sources[name]

    def fetch_all(
        self,
        query: str,
        limit_per_source: int = 50,
        **kwargs
    ) -> List[DataItem]:
        """
        Fetch from all configured sources.

        Args:
            query: Search query
            limit_per_source: Max items per source
            **kwargs: Additional parameters

        Returns:
            Combined list of DataItems from all sources
        """
        all_items = []
        for source in self.sources.values():
            items = source.fetch_or_mock(query, limit_per_source, **kwargs)
            all_items.extend(items)
        return all_items

    def get_available_sources(self) -> List[str]:
        """Get list of available (configured) sources."""
        return [
            name for name, source in self.sources.items()
            if source.is_available()
        ]

    def get_source_status(self) -> Dict[str, bool]:
        """Get availability status of all sources."""
        return {
            name: source.is_available()
            for name, source in self.sources.items()
        }
