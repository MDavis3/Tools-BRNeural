"""
FastAPI REST API for Neuralace Patient Voice Engine v2.0

Run with: uvicorn api.main:app --reload

Endpoints:
- GET /api/v1/pain-points - Get pain point analysis
- GET /api/v1/statistics - Get statistical analysis
- GET /api/v1/trends - Get trend analysis
- GET /api/v1/competitors - Get competitor analysis
- POST /api/v1/analyze - Analyze custom text
- GET /api/v1/health - Health check
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

from neuralace_engine.ingestor import PatientDataIngestor
from neuralace_engine.analyzer import PainPointAnalyzer
from neuralace_engine.statistics import StatisticalAnalyzer
from neuralace_engine.competitors import CompetitorAnalyzer
from neuralace_engine.trends import TrendAnalyzer
from neuralace_engine.sentiment import SentimentAnalyzer


# Initialize FastAPI app
app = FastAPI(
    title="Neuralace Patient Voice Engine API",
    description="API for analyzing BCI patient pain points and market intelligence",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class AnalyzeTextRequest(BaseModel):
    """Request model for text analysis."""
    text: str = Field(..., description="Text to analyze", min_length=1)
    use_sentiment: bool = Field(True, description="Apply sentiment filtering")


class AnalyzeTextResponse(BaseModel):
    """Response model for text analysis."""
    text: str
    categories: List[str]
    sentiment: Dict[str, Any]
    confidence: float


class PainPointCategory(BaseModel):
    """Pain point category data."""
    name: str
    count: int
    percentage: float
    confidence_avg: float
    quotes: List[Dict[str, Any]]


class PainPointResponse(BaseModel):
    """Response model for pain point analysis."""
    total_analyzed: int
    filtered_by_sentiment: int
    top_pain_point: Optional[str]
    representative_quote: str
    neuralace_advantage: str
    categories: Dict[str, Dict[str, Any]]
    sentiment_distribution: Dict[str, int]
    timestamp: str


class StatisticsResponse(BaseModel):
    """Response model for statistical analysis."""
    sample_assessment: Dict[str, Any]
    chi_square: Dict[str, Any]
    effect_size: Dict[str, Any]
    confidence_intervals: Dict[str, Dict[str, Any]]


class TrendResponse(BaseModel):
    """Response model for trend analysis."""
    period: str
    emerging_concerns: List[str]
    declining_concerns: List[str]
    stable_concerns: List[str]
    top_mover: Optional[str]
    top_mover_change: float
    category_trends: Dict[str, Dict[str, Any]]


class CompetitorResponse(BaseModel):
    """Response model for competitor analysis."""
    total_mentions: int
    most_mentioned: Optional[str]
    most_positive: Optional[str]
    highest_switching_intent: Optional[str]
    competitive_landscape: str
    competitors: Dict[str, Dict[str, Any]]


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    version: str
    timestamp: str
    components: Dict[str, bool]


# Cache for analysis results (simple in-memory)
_cache: Dict[str, Any] = {}
_cache_timestamp: Optional[datetime] = None
CACHE_TTL_SECONDS = 300  # 5 minutes


def get_cached_analysis():
    """Get cached analysis or compute new one."""
    global _cache, _cache_timestamp

    now = datetime.now()
    if _cache_timestamp and (now - _cache_timestamp).seconds < CACHE_TTL_SECONDS:
        return _cache

    # Load fresh data
    ingestor = PatientDataIngestor(mode="simulation")
    data = ingestor.fetch_data(subreddits=['ALS', 'spinalcordinjuries'], limit=100)

    # Run analysis
    analyzer = PainPointAnalyzer(use_sentiment=True)
    analysis = analyzer.analyze(data)

    # Run statistics
    stats_analyzer = StatisticalAnalyzer()
    stats = stats_analyzer.full_statistical_report(analysis)

    # Run competitor analysis
    comp_analyzer = CompetitorAnalyzer()
    competitors = comp_analyzer.analyze(data)

    # Run trend analysis
    trend_analyzer = TrendAnalyzer()
    trends = trend_analyzer.analyze_trends(data, period='30d', analyzer=analyzer)

    _cache = {
        'data': data,
        'analysis': analysis,
        'statistics': stats,
        'competitors': competitors,
        'trends': trends
    }
    _cache_timestamp = now

    return _cache


# API Endpoints

@app.get("/api/v1/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Check API health and component status."""
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        timestamp=datetime.now().isoformat(),
        components={
            "analyzer": True,
            "sentiment": True,
            "statistics": True,
            "competitors": True,
            "trends": True
        }
    )


@app.get("/api/v1/pain-points", response_model=PainPointResponse, tags=["Analysis"])
async def get_pain_points(
    refresh: bool = Query(False, description="Force refresh of cached data")
):
    """
    Get pain point analysis results.

    Returns categorized pain points with sentiment, confidence scores,
    and Neuralace competitive advantage mapping.
    """
    global _cache_timestamp
    if refresh:
        _cache_timestamp = None

    cache = get_cached_analysis()
    analysis = cache['analysis']

    return PainPointResponse(
        total_analyzed=analysis['total_analyzed'],
        filtered_by_sentiment=analysis['filtered_by_sentiment'],
        top_pain_point=analysis['top_pain_point'],
        representative_quote=analysis['representative_quote'],
        neuralace_advantage=analysis['neuralace_advantage'],
        categories=analysis['categories'],
        sentiment_distribution=analysis['sentiment_distribution'],
        timestamp=datetime.now().isoformat()
    )


@app.get("/api/v1/statistics", response_model=StatisticsResponse, tags=["Analysis"])
async def get_statistics():
    """
    Get statistical analysis of pain point data.

    Returns chi-square test results, confidence intervals,
    effect sizes, and sample adequacy assessment.
    """
    cache = get_cached_analysis()
    stats = cache['statistics']

    return StatisticsResponse(
        sample_assessment=stats['sample_assessment'],
        chi_square=stats['chi_square'],
        effect_size=stats['effect_size'],
        confidence_intervals=stats['confidence_intervals']
    )


@app.get("/api/v1/trends", response_model=TrendResponse, tags=["Analysis"])
async def get_trends(
    period: str = Query("30d", description="Analysis period: 7d, 30d, or 90d")
):
    """
    Get temporal trend analysis.

    Returns emerging, declining, and stable pain point trends
    over the specified time period.
    """
    if period not in ['7d', '30d', '90d']:
        raise HTTPException(status_code=400, detail="Invalid period. Use: 7d, 30d, or 90d")

    cache = get_cached_analysis()
    data = cache['data']

    # Recompute trends with requested period
    analyzer = PainPointAnalyzer(use_sentiment=False)
    trend_analyzer = TrendAnalyzer()
    trends = trend_analyzer.analyze_trends(data, period=period, analyzer=analyzer)

    # Convert CategoryTrend objects to dicts
    category_trends = {}
    for cat, trend in trends.category_trends.items():
        category_trends[cat] = {
            'current_percentage': trend.current_percentage,
            'previous_percentage': trend.previous_percentage,
            'change': trend.change,
            'change_rate': trend.change_rate,
            'direction': trend.direction,
            'velocity': trend.velocity,
            'is_emerging': trend.is_emerging
        }

    return TrendResponse(
        period=trends.analysis_period,
        emerging_concerns=trends.emerging_concerns,
        declining_concerns=trends.declining_concerns,
        stable_concerns=trends.stable_concerns,
        top_mover=trends.top_mover,
        top_mover_change=trends.top_mover_change,
        category_trends=category_trends
    )


@app.get("/api/v1/competitors", response_model=CompetitorResponse, tags=["Analysis"])
async def get_competitors():
    """
    Get competitor mention analysis.

    Returns analysis of competitor technology mentions,
    sentiment breakdown, and switching intent signals.
    """
    cache = get_cached_analysis()
    competitors = cache['competitors']

    # Convert CompetitorProfile objects to dicts
    competitor_data = {}
    for name, profile in competitors.competitors.items():
        competitor_data[name] = {
            'mention_count': profile.mention_count,
            'percentage': profile.percentage,
            'sentiment_breakdown': profile.sentiment_breakdown,
            'associated_pain_points': profile.associated_pain_points,
            'switching_intent_count': profile.switching_intent_count,
            'sample_quotes': profile.sample_quotes
        }

    return CompetitorResponse(
        total_mentions=competitors.total_competitor_mentions,
        most_mentioned=competitors.most_mentioned,
        most_positive=competitors.most_positive_sentiment,
        highest_switching_intent=competitors.highest_switching_intent,
        competitive_landscape=competitors.competitive_landscape,
        competitors=competitor_data
    )


@app.post("/api/v1/analyze", response_model=AnalyzeTextResponse, tags=["Analysis"])
async def analyze_text(request: AnalyzeTextRequest):
    """
    Analyze custom text for pain points.

    Useful for testing the analysis pipeline with specific
    patient comments or custom text.
    """
    text = request.text

    # Sentiment analysis
    sentiment_analyzer = SentimentAnalyzer()
    sentiment = sentiment_analyzer.analyze(text)

    # Pain point categorization
    analyzer = PainPointAnalyzer(use_sentiment=False)
    categories = analyzer._categorize_text(text)

    # Get confidence (simplified)
    confidence = min(1.0, len(categories) * 0.3 + 0.1)

    return AnalyzeTextResponse(
        text=text,
        categories=categories,
        sentiment={
            'label': sentiment.label,
            'compound': sentiment.compound,
            'magnitude': sentiment.magnitude
        },
        confidence=round(confidence, 3)
    )


@app.get("/api/v1/categories", tags=["Reference"])
async def get_categories():
    """Get list of all pain point categories and their keywords."""
    analyzer = PainPointAnalyzer(use_sentiment=False)

    categories = {}
    for cat in analyzer.get_all_categories():
        categories[cat] = {
            'keywords': analyzer.get_category_keywords(cat),
            'neuralace_advantage': analyzer.NEURALACE_ADVANTAGES.get(cat, '')
        }

    return {"categories": categories}


@app.get("/api/v1/competitors/list", tags=["Reference"])
async def get_competitor_list():
    """Get list of tracked competitors with descriptions."""
    comp_analyzer = CompetitorAnalyzer()

    competitors = []
    for name in comp_analyzer.get_competitor_list():
        info = comp_analyzer.get_competitor_info(name)
        competitors.append({
            'name': name,
            'type': info.get('type', 'unknown'),
            'notes': info.get('notes', '')
        })

    return {"competitors": competitors}


# Run with: uvicorn api.main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
