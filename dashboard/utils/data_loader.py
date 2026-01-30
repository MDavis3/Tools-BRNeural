"""
Unified data loader for all BCI Intelligence data sources.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from functools import lru_cache

import streamlit as st


class DataLoader:
    """Load and cache data from all BCI intelligence sources."""

    def __init__(self):
        # Get base paths relative to dashboard location
        self.base_path = Path(__file__).parent.parent.parent
        self.regulatory_data_path = self.base_path / "bci-regulatory-navigator" / "data"
        self.literature_data_path = self.base_path / "bci-literature-agent" / "data"

    @staticmethod
    @st.cache_data(ttl=300)
    def _load_json(file_path: str) -> Dict:
        """Load JSON file with caching."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            st.warning(f"Data file not found: {file_path}")
            return {}
        except json.JSONDecodeError:
            st.error(f"Invalid JSON in: {file_path}")
            return {}

    # =================
    # Regulatory Data
    # =================

    def load_fda_pathways(self) -> Dict:
        """Load FDA regulatory pathways data."""
        return self._load_json(str(self.regulatory_data_path / "fda_pathways.json"))

    def load_predicate_devices(self) -> Dict:
        """Load predicate devices database."""
        data = self._load_json(str(self.regulatory_data_path / "predicate_devices.json"))
        # Normalize key name
        if 'predicate_devices' in data and 'predicates' not in data:
            data['predicates'] = data['predicate_devices']
        return data

    def load_bci_companies(self) -> Dict:
        """Load BCI companies data."""
        return self._load_json(str(self.regulatory_data_path / "bci_companies.json"))

    def load_reimbursement(self) -> Dict:
        """Load reimbursement pathways data."""
        return self._load_json(str(self.regulatory_data_path / "reimbursement.json"))

    def load_high_channel_competitors(self) -> Dict:
        """Load high-channel competitor analysis."""
        return self._load_json(str(self.regulatory_data_path / "high_channel_competitors.json"))

    def load_neuralace_pathways(self) -> Dict:
        """Load Neuralace-specific pathway recommendations."""
        return self._load_json(str(self.regulatory_data_path / "neuralace_pathways.json"))

    # =================
    # Literature Data
    # =================

    def load_papers(self) -> Dict:
        """Load research papers database."""
        return self._load_json(str(self.literature_data_path / "papers.json"))

    def load_labs(self) -> Dict:
        """Load research labs database."""
        return self._load_json(str(self.literature_data_path / "labs.json"))

    def load_researchers(self) -> Dict:
        """Load key researchers database."""
        return self._load_json(str(self.literature_data_path / "researchers.json"))

    # =================
    # Aggregated Data
    # =================

    def get_all_competitors(self) -> List[Dict]:
        """Get unified list of all competitors from all sources."""
        competitors = []

        # From BCI companies
        companies_data = self.load_bci_companies()
        if 'companies' in companies_data:
            for company in companies_data['companies']:
                competitors.append({
                    'name': company.get('name', ''),
                    'source': 'regulatory',
                    'type': company.get('type', 'Commercial'),
                    'focus_areas': company.get('focus_areas', []),
                    'key_products': company.get('key_products', []),
                    'clinical_status': company.get('clinical_status', ''),
                    'competitive_position': company.get('competitive_position', ''),
                    'funding': company.get('funding', ''),
                })

        # From labs (commercial entities)
        labs_data = self.load_labs()
        if 'companies' in labs_data:
            for company in labs_data['companies']:
                # Avoid duplicates
                if not any(c['name'] == company.get('name', '') for c in competitors):
                    competitors.append({
                        'name': company.get('name', ''),
                        'source': 'literature',
                        'type': company.get('type', 'Commercial'),
                        'focus_areas': company.get('focus_areas', []),
                        'key_products': company.get('key_products', []),
                        'clinical_status': company.get('clinical_status', ''),
                        'competitive_position': company.get('competitive_position', ''),
                        'funding': company.get('funding', ''),
                    })

        return competitors

    def get_stats_summary(self) -> Dict:
        """Get summary statistics for dashboard overview."""
        papers = self.load_papers()
        labs = self.load_labs()
        pathways = self.load_fda_pathways()
        companies = self.load_bci_companies()

        return {
            'total_papers': len(papers.get('papers', [])),
            'total_labs': len(labs.get('labs', [])),
            'total_companies': len(labs.get('companies', [])) + len(companies.get('companies', [])),
            'fda_pathways': len(pathways.get('pathways', [])),
            'critical_papers': len([p for p in papers.get('papers', [])
                                   if p.get('neuralace_relevance') == 'CRITICAL']),
            'high_collab_labs': len([l for l in labs.get('labs', [])
                                    if l.get('collaboration_potential') in ['CRITICAL', 'HIGH']]),
        }

    def get_papers_by_relevance(self, relevance: str = None) -> List[Dict]:
        """Filter papers by Neuralace relevance level."""
        papers = self.load_papers().get('papers', [])
        if relevance:
            return [p for p in papers if p.get('neuralace_relevance') == relevance]
        return papers

    def get_labs_by_focus(self, focus_area: str = None) -> List[Dict]:
        """Filter labs by focus area."""
        labs = self.load_labs().get('labs', [])
        if focus_area:
            return [l for l in labs
                   if focus_area.lower() in ' '.join(l.get('focus_areas', [])).lower()]
        return labs

    def get_pathway_comparison(self) -> List[Dict]:
        """Get FDA pathways formatted for comparison table."""
        pathways = self.load_fda_pathways().get('pathways', [])
        return [{
            'Pathway': p.get('name', ''),
            'ID': p.get('id', ''),
            'Timeline (days)': p.get('typical_timeline_days', 'N/A'),
            'FDA Fee': f"${p.get('fda_fee_usd', 0):,}",
            'Clinical Data': 'Yes' if p.get('clinical_data_required') == True else 'No' if p.get('clinical_data_required') == False else str(p.get('clinical_data_required', 'Varies')),
            'Device Class': ', '.join(p.get('device_class', [])),
        } for p in pathways]


# Global instance for easy access
@st.cache_resource
def get_data_loader() -> DataLoader:
    """Get singleton DataLoader instance."""
    return DataLoader()
