"""
PubMed data source for Neuralace Patient Voice Engine.

Fetches clinical literature about BCI complications and outcomes.
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import random

from .base import DataSource, DataItem, SourceType

try:
    from Bio import Entrez
    BIOPYTHON_AVAILABLE = True
except ImportError:
    BIOPYTHON_AVAILABLE = False


class PubMedSource(DataSource):
    """
    PubMed data source using Biopython's Entrez.

    Fetches clinical literature about BCI complications,
    infection rates, and patient outcomes.
    """

    # Mock clinical literature data
    MOCK_ARTICLES = [
        {
            "title": "Long-term infection rates in percutaneous brain-computer interface implants: A systematic review",
            "abstract": "We analyzed 156 patients with percutaneous BCI implants over 5 years. Infection rate was 18.2%, with 8.4% requiring surgical intervention. The percutaneous connector site was the primary infection source in 94% of cases. Fully implanted systems showed significantly lower infection rates (p<0.001).",
            "pmid": "35123456",
            "year": 2024
        },
        {
            "title": "Patient quality of life outcomes following Utah Array implantation for ALS",
            "abstract": "Survey of 89 ALS patients with Utah Array implants revealed significant improvements in communication independence (82%). However, 67% reported moderate-to-severe burden from daily maintenance routines. Wire management and cleaning protocols were cited as primary concerns.",
            "pmid": "35234567",
            "year": 2024
        },
        {
            "title": "Comparison of percutaneous vs. fully implanted BCI systems: A meta-analysis",
            "abstract": "Meta-analysis of 12 studies (n=847) comparing percutaneous and fully implanted BCIs. Fully implanted systems showed 73% lower infection rates, 89% higher patient satisfaction for mobility, and comparable signal quality. Surgical revision rates were similar between groups.",
            "pmid": "35345678",
            "year": 2023
        },
        {
            "title": "Psychosocial impact of visible BCI hardware on patient identity",
            "abstract": "Qualitative study of 34 BCI users exploring psychosocial effects of visible hardware. Themes included social stigma (76% of participants), identity disruption (62%), and avoidance of public spaces (58%). Participants expressed strong preference for less visible alternatives.",
            "pmid": "35456789",
            "year": 2023
        },
        {
            "title": "Battery longevity and replacement burden in implanted neurostimulation devices",
            "abstract": "Analysis of 2,341 implanted neurostimulation procedures. Mean battery life was 4.2 years. Patients reported battery anxiety as a significant concern (44%). Wireless charging and energy harvesting technologies may address this limitation.",
            "pmid": "35567890",
            "year": 2024
        },
        {
            "title": "Signal stability and calibration requirements in chronic BCI implants",
            "abstract": "Longitudinal study of signal stability in 67 chronic BCI implants. Calibration was required on average every 2.3 days. 78% of patients reported frustration with calibration frequency. Adaptive algorithms reduced required calibration by 64%.",
            "pmid": "35678901",
            "year": 2023
        },
        {
            "title": "Cost-effectiveness analysis of brain-computer interfaces for communication restoration",
            "abstract": "Economic analysis of BCI for severe motor impairment. Mean total cost over 5 years: $847,000. Only 23% of costs covered by insurance. Patients reported significant financial burden. Value-based care models may improve access.",
            "pmid": "35789012",
            "year": 2024
        },
        {
            "title": "Complications and revision surgery rates in intracortical electrode arrays",
            "abstract": "Review of 234 intracortical electrode implants. 12% required revision surgery within 3 years. Primary causes: electrode migration (34%), connector issues (28%), infection (24%). Design improvements have reduced these rates in recent generations.",
            "pmid": "35890123",
            "year": 2023
        },
        {
            "title": "Patient perspectives on BCI aesthetics and social acceptance",
            "abstract": "Survey of 145 BCI candidates and 78 current users. 92% rated 'invisibility' as highly important. 84% would prefer longer implant procedure for less visible system. Social acceptance concerns were primary barrier to adoption in 67% of candidates.",
            "pmid": "35901234",
            "year": 2024
        },
        {
            "title": "Emerging fully implantable wireless BCI systems: A technology review",
            "abstract": "Review of emerging fully implantable BCIs including Blackrock Neuralace, Neuralink N1, and Synchron Stentrode. These systems address key limitations of percutaneous designs: infection risk, mobility constraints, and cosmetic concerns. Clinical trials are ongoing.",
            "pmid": "36012345",
            "year": 2024
        }
    ]

    def __init__(self):
        """Initialize the PubMed source."""
        super().__init__(name="pubmed", source_type=SourceType.CLINICAL_LITERATURE)
        self._email = None

    def configure(self, email: Optional[str] = None) -> bool:
        """
        Configure PubMed API access.

        Args:
            email: Email for Entrez API (required by NCBI)

        Returns:
            True if configuration successful
        """
        if not BIOPYTHON_AVAILABLE:
            self._is_configured = False
            return False

        self._email = email
        if self._email:
            Entrez.email = self._email
            self._is_configured = True
            return True

        self._is_configured = False
        return False

    def is_available(self) -> bool:
        """Check if PubMed API is available."""
        return self._is_configured and BIOPYTHON_AVAILABLE

    def fetch(
        self,
        query: str = "brain computer interface complications",
        limit: int = 50,
        **kwargs
    ) -> List[DataItem]:
        """
        Fetch articles from PubMed.

        Args:
            query: Search query
            limit: Maximum articles to fetch

        Returns:
            List of DataItem objects
        """
        if not self.is_available():
            return self.get_mock_data(limit)

        try:
            # Search PubMed
            handle = Entrez.esearch(
                db="pubmed",
                term=query,
                retmax=limit,
                sort="relevance"
            )
            record = Entrez.read(handle)
            handle.close()

            id_list = record.get("IdList", [])
            if not id_list:
                return self.get_mock_data(limit)

            # Fetch article details
            handle = Entrez.efetch(
                db="pubmed",
                id=",".join(id_list),
                rettype="xml",
                retmode="xml"
            )
            articles = Entrez.read(handle)
            handle.close()

            items = []
            for article in articles.get("PubmedArticle", []):
                medline = article.get("MedlineCitation", {})
                article_data = medline.get("Article", {})

                title = article_data.get("ArticleTitle", "")
                abstract_parts = article_data.get("Abstract", {}).get("AbstractText", [])
                abstract = " ".join(str(p) for p in abstract_parts)

                pmid = str(medline.get("PMID", ""))

                # Parse date
                pub_date = article_data.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {})
                year = pub_date.get("Year", "2024")
                try:
                    timestamp = datetime(int(year), 1, 1)
                except:
                    timestamp = datetime.now()

                items.append(DataItem(
                    text=f"{title}. {abstract}",
                    source="pubmed",
                    source_id=pmid,
                    timestamp=timestamp,
                    url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    title=title,
                    score=0,
                    metadata={
                        'type': 'article',
                        'pmid': pmid,
                        'abstract': abstract
                    }
                ))

            return items[:limit]

        except Exception as e:
            print(f"PubMed fetch error: {e}")
            return self.get_mock_data(limit)

    def get_mock_data(self, limit: int = 10) -> List[DataItem]:
        """Generate mock PubMed data for testing."""
        items = []

        for mock in self.MOCK_ARTICLES[:limit]:
            items.append(DataItem(
                text=f"{mock['title']}. {mock['abstract']}",
                source="pubmed",
                source_id=mock['pmid'],
                timestamp=datetime(mock['year'], 6, 15),
                url=f"https://pubmed.ncbi.nlm.nih.gov/{mock['pmid']}/",
                title=mock['title'],
                score=0,
                metadata={
                    'type': 'article',
                    'pmid': mock['pmid'],
                    'abstract': mock['abstract'],
                    'is_mock': True
                }
            ))

        return items


def create_pubmed_source() -> PubMedSource:
    """Factory function to create a PubMed source."""
    return PubMedSource()
