"""
Strategic Reports Page
======================

Executive insights, custom AI analysis, and exportable reports.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from datetime import datetime
import json
import io

from utils.theme import apply_custom_css, THEME
from utils.data_loader import get_data_loader
from components.metrics import render_metric_row
from components.help_system import render_page_help

# Optional imports for advanced features
try:
    from neuralace_engine.ingestor import PatientDataIngestor
    from neuralace_engine.analyzer import PainPointAnalyzer
    PATIENT_ENGINE_AVAILABLE = True
except ImportError:
    PATIENT_ENGINE_AVAILABLE = False

try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False


# Page configuration
st.set_page_config(
    page_title="Strategic Reports | BCI Intelligence Hub",
    page_icon="📊",
    layout="wide"
)

apply_custom_css()


def render_header():
    """Render page header."""
    st.markdown("""
    <h1 class="main-header">📊 Strategic Reports</h1>
    <p class="sub-header">Executive Insights & Exportable Intelligence</p>
    """, unsafe_allow_html=True)


def generate_executive_summary():
    """Generate executive summary from all data sources."""
    loader = get_data_loader()

    # Gather data
    stats = loader.get_stats_summary()
    papers = loader.load_papers().get('papers', [])
    pathways = loader.load_fda_pathways().get('pathways', [])
    competitors = loader.get_all_competitors()

    # Critical papers
    critical_papers = [p for p in papers if p.get('neuralace_relevance') == 'CRITICAL']

    # Generate patient voice summary if available
    patient_summary = None
    if PATIENT_ENGINE_AVAILABLE:
        try:
            ingestor = PatientDataIngestor(mode="simulation")
            data = ingestor.fetch_data(subreddits=['ALS'], limit=50)
            analyzer = PainPointAnalyzer(use_sentiment=True)
            analysis = analyzer.analyze(data)
            patient_summary = {
                'top_pain_point': analysis.get('top_pain_point'),
                'neuralace_advantage': analysis.get('neuralace_advantage'),
                'total_analyzed': analysis.get('total_analyzed', 0)
            }
        except Exception:
            pass

    return {
        'generated_at': datetime.now().isoformat(),
        'stats': stats,
        'critical_papers_count': len(critical_papers),
        'critical_papers': [p.get('title') for p in critical_papers[:5]],
        'competitors_count': len(competitors),
        'patient_summary': patient_summary,
        'recommended_pathway': '510(k)' if any(p.get('id') == '510k' for p in pathways) else 'De Novo',
    }


def render_executive_summary():
    """Render executive summary section."""
    st.subheader("📋 Executive Summary")

    summary = generate_executive_summary()

    # Key findings
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### Research Intel")
        st.metric("Total Papers", summary['stats'].get('total_papers', 0))
        st.metric("Critical Relevance", summary['critical_papers_count'])
        st.metric("Research Labs", summary['stats'].get('total_labs', 0))

    with col2:
        st.markdown("### Competitive Intel")
        st.metric("Competitors Tracked", summary['competitors_count'])
        st.metric("Recommended Pathway", summary['recommended_pathway'])

    with col3:
        st.markdown("### Patient Intel")
        if summary['patient_summary']:
            st.metric("Top Pain Point", summary['patient_summary'].get('top_pain_point', 'N/A'))
            st.metric("Comments Analyzed", summary['patient_summary'].get('total_analyzed', 0))
        else:
            st.info("Patient data not loaded")

    # Critical papers highlight
    st.markdown("---")
    st.markdown("### 🔴 Critical Papers for Neuralace")
    for paper in summary['critical_papers']:
        st.markdown(f"- {paper}")


def render_unified_insights():
    """Render unified insights from all sources."""
    st.subheader("🎯 Unified Strategic Insights")

    insights = [
        {
            'category': 'Market Opportunity',
            'insight': 'Patient communities consistently cite form factor, wireless capability, and biocompatibility as top concerns - all areas where Neuralace has advantages.',
            'source': 'Patient Voice Analysis',
            'priority': 'HIGH'
        },
        {
            'category': 'Technology Validation',
            'insight': '2025 Nature paper demonstrates 1,024-channel thin-film arrays with minimally invasive implantation - validates Neuralace approach.',
            'source': 'Research Intelligence',
            'priority': 'CRITICAL'
        },
        {
            'category': 'Regulatory Path',
            'insight': 'Precision Neuroscience\'s 510(k) clearance (March 2025) establishes predicate device pathway for thin-film cortical arrays.',
            'source': 'Regulatory Navigator',
            'priority': 'HIGH'
        },
        {
            'category': 'Competitive Timing',
            'insight': 'Neuralink and Paradromics advancing to human trials - window for differentiation through channel density and biocompatibility.',
            'source': 'Competitive Landscape',
            'priority': 'MEDIUM'
        },
    ]

    for insight in insights:
        priority_color = '#ff6b6b' if insight['priority'] == 'CRITICAL' else '#feca57' if insight['priority'] == 'HIGH' else '#54a0ff'

        st.markdown(f"""
        <div style="background: #1a1f2e; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid {priority_color};">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <strong>{insight['category']}</strong>
                <span style="color: {priority_color}; font-size: 0.8rem;">{insight['priority']}</span>
            </div>
            <p style="margin-bottom: 0.5rem;">{insight['insight']}</p>
            <span style="color: #a0a0a0; font-size: 0.8rem;">Source: {insight['source']}</span>
        </div>
        """, unsafe_allow_html=True)


def render_custom_analysis():
    """Render custom AI analysis section."""
    st.subheader("🤖 Custom AI Analysis")

    if not CLAUDE_AVAILABLE:
        st.info("Claude AI integration requires the `anthropic` package and API key.")
        st.code("pip install anthropic")
        st.markdown("Set `ANTHROPIC_API_KEY` in your environment or Streamlit secrets.")
        return

    # Check for API key
    api_key = os.environ.get('ANTHROPIC_API_KEY') or st.secrets.get('ANTHROPIC_API_KEY', '')

    if not api_key:
        st.warning("ANTHROPIC_API_KEY not found. Add it to your environment or Streamlit secrets.")
        return

    # Custom query input
    query = st.text_area(
        "Enter your strategic question:",
        placeholder="e.g., What are the key differentiators for Neuralace vs Neuralink?",
        height=100
    )

    if st.button("Analyze with Claude", type="primary"):
        if query:
            with st.spinner("Analyzing with Claude..."):
                try:
                    client = anthropic.Anthropic(api_key=api_key)

                    # Build context from data
                    loader = get_data_loader()
                    context = f"""
                    You are a BCI market intelligence analyst for Blackrock Neurotech's Neuralace project.

                    Key data:
                    - Neuralace target: 10,000+ channel flexible neural interface
                    - Top competitors: Neuralink (1024 ch), Paradromics (1600 ch), Synchron (16 ch endovascular)
                    - Papers tracked: {loader.get_stats_summary()['total_papers']} research papers
                    - Labs tracked: {loader.get_stats_summary()['total_labs']} research institutions

                    Question: {query}

                    Provide a strategic analysis with actionable insights.
                    """

                    message = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=1024,
                        messages=[{"role": "user", "content": context}]
                    )

                    st.markdown("### Analysis Result")
                    st.markdown(message.content[0].text)

                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")
        else:
            st.warning("Please enter a question to analyze.")


def render_export_section():
    """Render data export section."""
    st.subheader("📤 Export Data")

    loader = get_data_loader()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### Research Data")

        # Papers CSV
        papers = loader.load_papers().get('papers', [])
        if papers:
            df = pd.DataFrame(papers)
            csv = df.to_csv(index=False)
            st.download_button(
                "Download Papers CSV",
                data=csv,
                file_name="bci_papers.csv",
                mime="text/csv"
            )

        # Labs CSV
        labs = loader.load_labs().get('labs', [])
        if labs:
            df = pd.DataFrame(labs)
            csv = df.to_csv(index=False)
            st.download_button(
                "Download Labs CSV",
                data=csv,
                file_name="research_labs.csv",
                mime="text/csv"
            )

    with col2:
        st.markdown("#### Regulatory Data")

        # Pathways
        pathways = loader.load_fda_pathways().get('pathways', [])
        if pathways:
            json_str = json.dumps(pathways, indent=2)
            st.download_button(
                "Download FDA Pathways JSON",
                data=json_str,
                file_name="fda_pathways.json",
                mime="application/json"
            )

        # Companies
        companies = loader.load_bci_companies().get('companies', [])
        if companies:
            df = pd.DataFrame(companies)
            csv = df.to_csv(index=False)
            st.download_button(
                "Download Companies CSV",
                data=csv,
                file_name="bci_companies.csv",
                mime="text/csv"
            )

    with col3:
        st.markdown("#### Full Report")

        # Generate full report
        summary = generate_executive_summary()
        report = {
            'report_title': 'BCI Intelligence Report',
            'generated_at': summary['generated_at'],
            'executive_summary': summary,
            'data_sources': {
                'papers': len(loader.load_papers().get('papers', [])),
                'labs': len(loader.load_labs().get('labs', [])),
                'pathways': len(loader.load_fda_pathways().get('pathways', [])),
                'companies': len(loader.load_bci_companies().get('companies', [])),
            }
        }

        json_str = json.dumps(report, indent=2)
        st.download_button(
            "Download Full Report JSON",
            data=json_str,
            file_name=f"bci_intelligence_report_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )


def render_shareable_summary():
    """Render shareable text summary."""
    st.subheader("📋 Shareable Summary")

    summary = generate_executive_summary()

    text = f"""
BCI Intelligence Report - {datetime.now().strftime('%Y-%m-%d')}
===============================================

EXECUTIVE SUMMARY

Research Intelligence:
- {summary['stats'].get('total_papers', 0)} research papers tracked
- {summary['critical_papers_count']} papers with critical Neuralace relevance
- {summary['stats'].get('total_labs', 0)} research labs monitored

Competitive Intelligence:
- {summary['competitors_count']} competitors tracked
- Recommended regulatory pathway: {summary['recommended_pathway']}

Key Papers for Neuralace:
{chr(10).join(['- ' + p for p in summary['critical_papers']])}

Generated by BCI Intelligence Hub | Blackrock Neurotech
    """

    st.text_area("Copy this summary:", value=text.strip(), height=300)

    st.download_button(
        "Download as Text",
        data=text,
        file_name=f"bci_summary_{datetime.now().strftime('%Y%m%d')}.txt",
        mime="text/plain"
    )


def render_sidebar():
    """Render sidebar."""
    with st.sidebar:
        st.markdown("### 📊 Reports")
        st.markdown("---")

        st.markdown("#### Report Sections")
        st.markdown("- Executive Summary")
        st.markdown("- Unified Insights")
        st.markdown("- Custom AI Analysis")
        st.markdown("- Data Export")
        st.markdown("- Shareable Summary")

        st.markdown("---")

        st.markdown("#### Last Updated")
        st.caption(datetime.now().strftime('%Y-%m-%d %H:%M'))


def main():
    """Main page entry point."""
    render_header()

    # Help section
    render_page_help(
        "Strategic Reports",
        "Generate executive reports combining all intelligence sources.",
        [
            "Executive summary aggregates key findings from all tools",
            "Custom AI analysis uses Claude for strategic questions",
            "Export data as CSV or JSON for further analysis",
            "Shareable summary for quick stakeholder updates"
        ]
    )

    # Sidebar
    render_sidebar()

    # Main content
    render_executive_summary()

    st.divider()

    render_unified_insights()

    st.divider()

    render_custom_analysis()

    st.divider()

    render_export_section()

    st.divider()

    render_shareable_summary()

    # Footer
    st.divider()
    st.caption("Strategic Reports v1.0 | BCI Intelligence Hub")


if __name__ == "__main__":
    main()
