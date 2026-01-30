"""
Test suite for Neuralace Patient Voice Engine.
Written FIRST per TDD methodology - tests define expected behavior.
"""

import pytest
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from neuralace_engine.ingestor import PatientDataIngestor
from neuralace_engine.analyzer import PainPointAnalyzer
from neuralace_engine.report import generate_strategic_report


class TestPatientDataIngestor:
    """Tests for the data ingestion layer."""

    def test_ingestor_returns_correct_data_structure(self):
        """Verify ingestor returns list of dicts with required keys."""
        ingestor = PatientDataIngestor(mode="simulation")
        data = ingestor.fetch_data(subreddits=['ALS'], limit=10)

        # Must return a list
        assert isinstance(data, list), "fetch_data must return a list"

        # Must have at least one item in simulation mode
        assert len(data) > 0, "Simulation mode must return mock data"

        # Each item must have required keys
        required_keys = {'text', 'source', 'timestamp', 'score'}
        for item in data:
            assert isinstance(item, dict), "Each item must be a dictionary"
            assert required_keys.issubset(item.keys()), f"Missing keys. Required: {required_keys}, Got: {item.keys()}"

            # Type validation
            assert isinstance(item['text'], str), "'text' must be a string"
            assert isinstance(item['source'], str), "'source' must be a string"
            assert isinstance(item['timestamp'], datetime), "'timestamp' must be a datetime"
            assert isinstance(item['score'], int), "'score' must be an integer"

    def test_ingestor_simulation_mode_returns_minimum_20_items(self):
        """Simulation mode must provide at least 20 realistic mock comments."""
        ingestor = PatientDataIngestor(mode="simulation")
        data = ingestor.fetch_data(subreddits=['ALS', 'spinalcordinjuries'], limit=100)

        assert len(data) >= 20, f"Simulation mode must return at least 20 items, got {len(data)}"

    def test_ingestor_handles_live_mode_gracefully(self):
        """Live mode should work without crashing (even without API keys)."""
        ingestor = PatientDataIngestor(mode="live")
        # Should not raise exception, may return empty list or fallback to simulation
        data = ingestor.fetch_data(subreddits=['ALS'], limit=5)
        assert isinstance(data, list), "Even in live mode failure, should return a list"


class TestPainPointAnalyzer:
    """Tests for the pain point analysis logic."""

    def test_analyzer_identifies_infection_keywords(self):
        """Verify analyzer correctly categorizes infection-related text."""
        analyzer = PainPointAnalyzer()

        test_cases = [
            {"text": "The area around my pedestal was oozing yesterday", "source": "ALS", "timestamp": datetime.now(), "score": 10},
            {"text": "I spend 30 minutes cleaning the site daily", "source": "ALS", "timestamp": datetime.now(), "score": 5},
            {"text": "Third infection this year from the percutaneous connector", "source": "spinalcordinjuries", "timestamp": datetime.now(), "score": 15},
        ]

        result = analyzer.analyze(test_cases)

        # All these should be categorized under Infection Risk
        assert 'Infection Risk' in result['categories'], "Must have 'Infection Risk' category"
        assert result['categories']['Infection Risk']['count'] >= 3, "All 3 infection-related texts should be categorized"

    def test_analyzer_identifies_form_factor_issues(self):
        """Verify analyzer catches hardware/form factor complaints."""
        analyzer = PainPointAnalyzer()

        test_cases = [
            {"text": "The wires got tangled in my sleep again", "source": "ALS", "timestamp": datetime.now(), "score": 10},
            {"text": "This thing is so bulky I can't wear hats anymore", "source": "spinalcordinjuries", "timestamp": datetime.now(), "score": 8},
            {"text": "The cable snagged on my wheelchair", "source": "ALS", "timestamp": datetime.now(), "score": 12},
        ]

        result = analyzer.analyze(test_cases)

        assert 'Form Factor' in result['categories'], "Must have 'Form Factor' category"
        assert result['categories']['Form Factor']['count'] >= 3, "All 3 form factor texts should be categorized"

    def test_analyzer_identifies_social_stigma(self):
        """Verify analyzer catches social/visibility concerns."""
        analyzer = PainPointAnalyzer()

        test_cases = [
            {"text": "People keep staring at my head when I go out", "source": "ALS", "timestamp": datetime.now(), "score": 10},
            {"text": "I look like a robot with this thing attached", "source": "spinalcordinjuries", "timestamp": datetime.now(), "score": 7},
            {"text": "The visible hardware makes me feel like a science experiment", "source": "ALS", "timestamp": datetime.now(), "score": 9},
        ]

        result = analyzer.analyze(test_cases)

        assert 'Social Stigma' in result['categories'], "Must have 'Social Stigma' category"
        assert result['categories']['Social Stigma']['count'] >= 3, "All 3 social stigma texts should be categorized"

    def test_handles_empty_dataset_gracefully(self):
        """Verify system doesn't crash on empty input."""
        analyzer = PainPointAnalyzer()

        result = analyzer.analyze([])

        # Should not raise exception
        assert result is not None, "Must return a result even for empty data"
        assert 'categories' in result, "Must have 'categories' key"
        assert 'top_pain_point' in result, "Must have 'top_pain_point' key"

        # Percentages should be zero or None for empty data
        for category, data in result['categories'].items():
            assert data['count'] == 0, f"Count should be 0 for empty data, got {data['count']} for {category}"

    def test_percentage_calculation(self):
        """Verify pain point percentages are calculated correctly."""
        analyzer = PainPointAnalyzer()

        # Create data with known distribution: 2 infection, 1 form factor, 1 stigma
        test_cases = [
            {"text": "Dealing with infection around the pedestal", "source": "ALS", "timestamp": datetime.now(), "score": 10},
            {"text": "The cleaning ritual is exhausting", "source": "ALS", "timestamp": datetime.now(), "score": 5},
            {"text": "The wires are so annoying", "source": "ALS", "timestamp": datetime.now(), "score": 8},
            {"text": "People staring at me constantly", "source": "ALS", "timestamp": datetime.now(), "score": 6},
        ]

        result = analyzer.analyze(test_cases)

        # Sum of percentages should be 100 (or close to it for rounding)
        total_percentage = sum(cat['percentage'] for cat in result['categories'].values())
        assert 99.0 <= total_percentage <= 101.0, f"Percentages should sum to ~100%, got {total_percentage}%"

    def test_representative_quote_extraction(self):
        """Verify system selects an actual quote from the data."""
        analyzer = PainPointAnalyzer()

        test_cases = [
            {"text": "The infection risk is my biggest concern", "source": "ALS", "timestamp": datetime.now(), "score": 20},
            {"text": "I hate the oozing around the site", "source": "ALS", "timestamp": datetime.now(), "score": 15},
        ]

        result = analyzer.analyze(test_cases)

        # Representative quote should be one of the actual texts
        actual_texts = [item['text'] for item in test_cases]
        assert result['representative_quote'] in actual_texts, \
            f"Representative quote must be from actual data. Got: '{result['representative_quote']}'"

    def test_neuralace_advantage_mapping(self):
        """Verify each pain point maps to a Neuralace advantage."""
        analyzer = PainPointAnalyzer()

        test_cases = [
            {"text": "The infection from the pedestal is awful", "source": "ALS", "timestamp": datetime.now(), "score": 10},
        ]

        result = analyzer.analyze(test_cases)

        assert 'neuralace_advantage' in result, "Must include neuralace_advantage"
        assert len(result['neuralace_advantage']) > 0, "Neuralace advantage must not be empty"


class TestReportGenerator:
    """Tests for the strategic report output."""

    def test_report_contains_required_sections(self):
        """Verify report has all required sections."""
        analysis = {
            'categories': {
                'Infection Risk': {'count': 5, 'percentage': 50.0, 'quotes': ["Test quote 1"]},
                'Form Factor': {'count': 3, 'percentage': 30.0, 'quotes': ["Test quote 2"]},
                'Social Stigma': {'count': 2, 'percentage': 20.0, 'quotes': ["Test quote 3"]},
            },
            'top_pain_point': 'Infection Risk',
            'representative_quote': 'Test quote 1',
            'neuralace_advantage': 'Neuralace is FULLY IMPLANTED - no percutaneous connector'
        }

        report = generate_strategic_report(analysis)

        # Check for required content
        assert 'TOP PATIENT PAIN POINT' in report, "Report must contain TOP PATIENT PAIN POINT"
        assert 'Infection Risk' in report, "Report must show the top pain point category"
        assert '50' in report, "Report must show percentage"
        assert 'Test quote 1' in report, "Report must include representative quote"
        assert 'NEURALACE' in report.upper(), "Report must mention Neuralace advantage"

    def test_report_handles_empty_analysis(self):
        """Verify report generation doesn't crash on empty analysis."""
        analysis = {
            'categories': {
                'Infection Risk': {'count': 0, 'percentage': 0.0, 'quotes': []},
                'Form Factor': {'count': 0, 'percentage': 0.0, 'quotes': []},
                'Social Stigma': {'count': 0, 'percentage': 0.0, 'quotes': []},
            },
            'top_pain_point': None,
            'representative_quote': '',
            'neuralace_advantage': ''
        }

        # Should not raise exception
        report = generate_strategic_report(analysis)
        assert isinstance(report, str), "Report must be a string"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
