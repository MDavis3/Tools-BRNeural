"""
Neuralace Patient Voice Engine v2.0

A comprehensive Python toolkit for mining patient communities
and validating Blackrock Neurotech's Neuralace value proposition.

Modules:
- ingestor: Data ingestion from Reddit and other sources
- analyzer: Pain point categorization with sentiment
- sentiment: VADER sentiment analysis
- statistics: Statistical significance testing
- trends: Temporal trend analysis
- competitors: Competitor mention tracking
- llm_analyzer: Claude API integration
- report: Strategic report generation
- sources: Multi-source data ingestion (Reddit, PubMed, ClinicalTrials)
"""

from .ingestor import PatientDataIngestor
from .analyzer import PainPointAnalyzer
from .sentiment import SentimentAnalyzer
from .statistics import StatisticalAnalyzer
from .trends import TrendAnalyzer
from .competitors import CompetitorAnalyzer
from .llm_analyzer import LLMAnalyzer
from .report import generate_strategic_report

__version__ = "2.0.0"

__all__ = [
    'PatientDataIngestor',
    'PainPointAnalyzer',
    'SentimentAnalyzer',
    'StatisticalAnalyzer',
    'TrendAnalyzer',
    'CompetitorAnalyzer',
    'LLMAnalyzer',
    'generate_strategic_report',
]
