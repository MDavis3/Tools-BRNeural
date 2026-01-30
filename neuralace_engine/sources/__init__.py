"""
Multi-source data ingestion for Neuralace Patient Voice Engine.

Supports:
- Reddit (patient communities)
- PubMed (clinical literature)
- ClinicalTrials.gov (trial data)
"""

from .base import DataSource, DataItem
from .reddit import RedditSource
from .pubmed import PubMedSource
from .clinical_trials import ClinicalTrialsSource

__all__ = [
    'DataSource',
    'DataItem',
    'RedditSource',
    'PubMedSource',
    'ClinicalTrialsSource'
]
