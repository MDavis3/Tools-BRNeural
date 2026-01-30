"""
ClinicalTrials.gov data source for Neuralace Patient Voice Engine.

Fetches information about BCI clinical trials.
"""

from typing import List, Dict, Optional
from datetime import datetime
import random

from .base import DataSource, DataItem, SourceType

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class ClinicalTrialsSource(DataSource):
    """
    ClinicalTrials.gov data source.

    Fetches clinical trial information for BCI devices,
    including outcomes and adverse events.
    """

    BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

    # Mock clinical trial data
    MOCK_TRIALS = [
        {
            "nct_id": "NCT05123456",
            "title": "Safety and Efficacy of Fully Implantable BCI for ALS Communication",
            "description": "Phase 2 trial evaluating a fully implantable wireless BCI system for communication restoration in patients with ALS. Primary endpoints include infection rate, device longevity, and communication accuracy. The device eliminates percutaneous connectors to reduce infection risk.",
            "status": "Recruiting",
            "phase": "Phase 2",
            "conditions": ["ALS", "Motor Neuron Disease"],
            "sponsor": "Blackrock Neurotech",
            "start_date": "2024-01-15"
        },
        {
            "nct_id": "NCT05234567",
            "title": "Long-term Outcomes of Utah Array Implants in Spinal Cord Injury",
            "description": "Observational study tracking long-term outcomes in 150 patients with Utah Array implants. Monitoring infection rates, signal stability, quality of life, and need for revision surgery over 5 years. Adverse events include percutaneous site infections (18%), connector issues (12%).",
            "status": "Active",
            "phase": "Not Applicable",
            "conditions": ["Spinal Cord Injury", "Tetraplegia"],
            "sponsor": "University Medical Center",
            "start_date": "2020-06-01"
        },
        {
            "nct_id": "NCT05345678",
            "title": "Neuralink N1 Device First-in-Human Trial",
            "description": "First-in-human trial of the Neuralink N1 wireless BCI device. Evaluating safety and preliminary efficacy in patients with quadriplegia. The fully implanted design aims to address limitations of percutaneous systems including infection and cosmetic concerns.",
            "status": "Recruiting",
            "phase": "Phase 1",
            "conditions": ["Quadriplegia", "Spinal Cord Injury"],
            "sponsor": "Neuralink Corporation",
            "start_date": "2024-05-01"
        },
        {
            "nct_id": "NCT05456789",
            "title": "Synchron Stentrode for Motor Function Restoration",
            "description": "Pivotal trial of the Synchron Stentrode endovascular BCI. Minimally invasive placement via blood vessels eliminates need for open brain surgery. Evaluating device safety, signal quality, and patient-reported outcomes including mobility and social participation.",
            "status": "Recruiting",
            "phase": "Phase 3",
            "conditions": ["ALS", "Stroke", "Spinal Cord Injury"],
            "sponsor": "Synchron Inc",
            "start_date": "2023-09-15"
        },
        {
            "nct_id": "NCT05567890",
            "title": "Patient Quality of Life with Percutaneous vs Implanted BCIs",
            "description": "Comparative study of quality of life outcomes between percutaneous and fully implanted BCI systems. Measuring daily maintenance burden, infection rates, social participation, and overall satisfaction. Hypothesis: Fully implanted systems will show superior QoL scores.",
            "status": "Not yet recruiting",
            "phase": "Not Applicable",
            "conditions": ["ALS", "Brainstem Stroke"],
            "sponsor": "National Institute of Health",
            "start_date": "2025-01-01"
        },
        {
            "nct_id": "NCT05678901",
            "title": "Wireless Power Transfer for Implanted Neural Devices",
            "description": "Feasibility study of wireless power transfer technology for implanted BCI devices. Aims to eliminate battery replacement surgeries and reduce patient burden. Monitoring power transfer efficiency, thermal safety, and long-term device function.",
            "status": "Enrolling by invitation",
            "phase": "Phase 1",
            "conditions": ["Motor Disability"],
            "sponsor": "Academic Research Consortium",
            "start_date": "2024-03-01"
        }
    ]

    def __init__(self):
        """Initialize the ClinicalTrials source."""
        super().__init__(name="clinicaltrials", source_type=SourceType.CLINICAL_TRIALS)

    def configure(self, **kwargs) -> bool:
        """
        Configure ClinicalTrials.gov API access.

        No authentication required for public API.

        Returns:
            True if configuration successful
        """
        if REQUESTS_AVAILABLE:
            self._is_configured = True
            return True
        self._is_configured = False
        return False

    def is_available(self) -> bool:
        """Check if ClinicalTrials API is available."""
        return self._is_configured and REQUESTS_AVAILABLE

    def fetch(
        self,
        query: str = "brain computer interface",
        limit: int = 50,
        **kwargs
    ) -> List[DataItem]:
        """
        Fetch trials from ClinicalTrials.gov.

        Args:
            query: Search query
            limit: Maximum trials to fetch

        Returns:
            List of DataItem objects
        """
        if not self.is_available():
            return self.get_mock_data(limit)

        try:
            params = {
                "query.term": query,
                "pageSize": min(limit, 100),
                "format": "json"
            }

            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            items = []
            studies = data.get("studies", [])

            for study in studies[:limit]:
                protocol = study.get("protocolSection", {})
                id_module = protocol.get("identificationModule", {})
                desc_module = protocol.get("descriptionModule", {})
                status_module = protocol.get("statusModule", {})

                nct_id = id_module.get("nctId", "")
                title = id_module.get("briefTitle", "")
                description = desc_module.get("briefSummary", "")

                # Parse start date
                start_date_str = status_module.get("startDateStruct", {}).get("date", "")
                try:
                    timestamp = datetime.strptime(start_date_str, "%Y-%m-%d")
                except:
                    timestamp = datetime.now()

                items.append(DataItem(
                    text=f"{title}. {description}",
                    source="clinicaltrials",
                    source_id=nct_id,
                    timestamp=timestamp,
                    url=f"https://clinicaltrials.gov/study/{nct_id}",
                    title=title,
                    score=0,
                    metadata={
                        'type': 'clinical_trial',
                        'nct_id': nct_id,
                        'status': status_module.get("overallStatus", ""),
                        'phase': protocol.get("designModule", {}).get("phases", [])
                    }
                ))

            return items

        except Exception as e:
            print(f"ClinicalTrials fetch error: {e}")
            return self.get_mock_data(limit)

    def get_mock_data(self, limit: int = 6) -> List[DataItem]:
        """Generate mock ClinicalTrials data for testing."""
        items = []

        for mock in self.MOCK_TRIALS[:limit]:
            try:
                timestamp = datetime.strptime(mock['start_date'], "%Y-%m-%d")
            except:
                timestamp = datetime.now()

            items.append(DataItem(
                text=f"{mock['title']}. {mock['description']}",
                source="clinicaltrials",
                source_id=mock['nct_id'],
                timestamp=timestamp,
                url=f"https://clinicaltrials.gov/study/{mock['nct_id']}",
                title=mock['title'],
                score=0,
                metadata={
                    'type': 'clinical_trial',
                    'nct_id': mock['nct_id'],
                    'status': mock['status'],
                    'phase': mock['phase'],
                    'sponsor': mock['sponsor'],
                    'conditions': mock['conditions'],
                    'is_mock': True
                }
            ))

        return items


def create_clinical_trials_source() -> ClinicalTrialsSource:
    """Factory function to create a ClinicalTrials source."""
    return ClinicalTrialsSource()
