"""
Research Intelligence Page
==========================

Curated database of breakthrough papers, leading labs, and key researchers.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.express as px

from utils.theme import apply_custom_css, get_plotly_layout, THEME, render_badge
from utils.data_loader import get_data_loader
from components.metrics import render_metric_row
from components.help_system import render_page_help


# Page configuration
st.set_page_config(
    page_title="Research Intel | BCI Intelligence Hub",
    page_icon="📚",
    layout="wide"
)

apply_custom_css()


def render_header():
    """Render page header."""
    st.markdown("""
    <h1 class="main-header">📚 Research Intelligence</h1>
    <p class="sub-header">Breakthrough Papers, Leading Labs & Key Researchers</p>
    """, unsafe_allow_html=True)


def render_overview_metrics():
    """Render overview statistics."""
    loader = get_data_loader()
    papers = loader.load_papers().get('papers', [])
    labs = loader.load_labs()

    critical = len([p for p in papers if p.get('neuralace_relevance') == 'CRITICAL'])
    high = len([p for p in papers if p.get('neuralace_relevance') == 'HIGH'])
    lab_count = len(labs.get('labs', []))
    high_collab = len([l for l in labs.get('labs', []) if l.get('collaboration_potential') in ['CRITICAL', 'HIGH']])

    metrics = [
        {'icon': '📄', 'label': 'Total Papers', 'value': len(papers), 'delta': f'{critical} critical relevance'},
        {'icon': '🔴', 'label': 'Critical Papers', 'value': critical, 'delta': 'Highest Neuralace relevance'},
        {'icon': '🟡', 'label': 'High Relevance', 'value': high, 'delta': 'Important for development'},
        {'icon': '🔬', 'label': 'Research Labs', 'value': lab_count, 'delta': f'{high_collab} high collaboration'},
    ]

    render_metric_row(metrics)


def render_papers_browser():
    """Render research papers browser."""
    st.subheader("📄 Research Papers Database")

    loader = get_data_loader()
    papers_data = loader.load_papers()
    papers = papers_data.get('papers', [])

    if not papers:
        st.warning("No papers data available")
        return

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        relevance_filter = st.multiselect(
            "Filter by Relevance:",
            options=['CRITICAL', 'HIGH', 'MEDIUM'],
            default=['CRITICAL', 'HIGH']
        )

    with col2:
        years = sorted(set(p.get('year', 0) for p in papers), reverse=True)
        year_filter = st.multiselect(
            "Filter by Year:",
            options=years,
            default=[]
        )

    with col3:
        categories = set()
        for p in papers:
            categories.update(p.get('categories', []))
        cat_filter = st.multiselect(
            "Filter by Category:",
            options=sorted(categories),
            default=[]
        )

    # Apply filters
    filtered = papers
    if relevance_filter:
        filtered = [p for p in filtered if p.get('neuralace_relevance') in relevance_filter]
    if year_filter:
        filtered = [p for p in filtered if p.get('year') in year_filter]
    if cat_filter:
        filtered = [p for p in filtered if any(c in p.get('categories', []) for c in cat_filter)]

    st.caption(f"Showing {len(filtered)} of {len(papers)} papers")

    # Display papers
    for paper in filtered:
        relevance = paper.get('neuralace_relevance', 'MEDIUM')
        badge_class = 'critical' if relevance == 'CRITICAL' else 'high' if relevance == 'HIGH' else 'medium'

        with st.expander(f"**{paper.get('title', 'Untitled')}** ({paper.get('year', 'N/A')})"):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**Authors:** {', '.join(paper.get('authors', ['Unknown']))}")
                st.markdown(f"**Journal:** {paper.get('journal', 'N/A')}")
                st.markdown(f"**Year:** {paper.get('year', 'N/A')}")

                if paper.get('doi'):
                    st.markdown(f"**DOI:** [{paper.get('doi')}](https://doi.org/{paper.get('doi')})")

                if paper.get('url'):
                    st.markdown(f"[View Paper →]({paper.get('url')})")

            with col2:
                st.markdown(render_badge(relevance, badge_class), unsafe_allow_html=True)
                if paper.get('citation_count'):
                    st.metric("Citations", paper.get('citation_count'))

            st.markdown("---")
            st.markdown("**Abstract Summary:**")
            st.markdown(paper.get('abstract_summary', 'No abstract available'))

            if paper.get('key_findings'):
                st.markdown("**Key Findings:**")
                for finding in paper.get('key_findings', []):
                    st.markdown(f"- {finding}")

            if paper.get('relevance_notes'):
                st.info(f"**Neuralace Relevance:** {paper.get('relevance_notes')}")

            if paper.get('categories'):
                st.markdown(f"**Categories:** {', '.join(paper.get('categories', []))}")


def render_relevance_chart():
    """Render papers by relevance visualization."""
    st.subheader("📊 Papers by Neuralace Relevance")

    loader = get_data_loader()
    papers = loader.load_papers().get('papers', [])

    relevance_counts = {}
    for p in papers:
        rel = p.get('neuralace_relevance', 'MEDIUM')
        relevance_counts[rel] = relevance_counts.get(rel, 0) + 1

    df = pd.DataFrame([
        {'Relevance': k, 'Count': v}
        for k, v in relevance_counts.items()
    ])

    colors = {'CRITICAL': '#ff6b6b', 'HIGH': '#feca57', 'MEDIUM': '#54a0ff'}

    fig = px.pie(
        df,
        values='Count',
        names='Relevance',
        color='Relevance',
        color_discrete_map=colors,
        hole=0.4
    )

    layout = get_plotly_layout()
    fig.update_layout(**layout, height=300)

    st.plotly_chart(fig, use_container_width=True)


def render_labs_directory():
    """Render research labs directory."""
    st.subheader("🔬 Research Labs Directory")

    loader = get_data_loader()
    labs_data = loader.load_labs()
    labs = labs_data.get('labs', [])

    if not labs:
        st.info("No labs data available")
        return

    # Filter by collaboration potential
    collab_filter = st.multiselect(
        "Filter by Collaboration Potential:",
        options=['CRITICAL', 'HIGH', 'MEDIUM'],
        default=['CRITICAL', 'HIGH']
    )

    filtered = [l for l in labs if l.get('collaboration_potential') in collab_filter] if collab_filter else labs

    st.caption(f"Showing {len(filtered)} of {len(labs)} labs")

    for lab in filtered:
        collab = lab.get('collaboration_potential', 'MEDIUM')
        badge_class = 'critical' if collab == 'CRITICAL' else 'high' if collab == 'HIGH' else 'medium'

        with st.expander(f"**{lab.get('name', 'Unknown')}** - {lab.get('institution', 'Unknown')}"):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**Location:** {lab.get('location', 'N/A')}")
                st.markdown(f"**Principal Investigators:** {', '.join(lab.get('principal_investigators', ['Unknown']))}")

                if lab.get('website'):
                    st.markdown(f"[Visit Website →]({lab.get('website')})")

            with col2:
                st.markdown(f"**Collaboration:** {render_badge(collab, badge_class)}", unsafe_allow_html=True)

            st.markdown("**Focus Areas:**")
            for area in lab.get('focus_areas', []):
                st.markdown(f"- {area}")

            if lab.get('key_achievements'):
                st.markdown("**Key Achievements:**")
                for achievement in lab.get('key_achievements', []):
                    st.success(achievement)

            if lab.get('neuralace_relevance'):
                st.info(f"**Neuralace Relevance:** {', '.join(lab.get('neuralace_relevance', []))}")

            if lab.get('notes'):
                st.caption(lab.get('notes'))


def render_journals():
    """Render key journals information."""
    st.subheader("📰 Key Journals")

    loader = get_data_loader()
    papers_data = loader.load_papers()
    journals = papers_data.get('key_journals', [])

    if not journals:
        st.info("No journal data available")
        return

    data = []
    for j in journals:
        data.append({
            'Journal': j.get('name', ''),
            'Impact Factor': j.get('impact_factor', 'N/A'),
            'Relevance': j.get('relevance', ''),
        })

    df = pd.DataFrame(data)
    df = df.sort_values('Impact Factor', ascending=False)

    st.dataframe(df, use_container_width=True, hide_index=True)


def render_sidebar():
    """Render sidebar."""
    with st.sidebar:
        st.markdown("### 📚 Research Intel")
        st.markdown("---")

        st.markdown("#### Quick Stats")
        loader = get_data_loader()
        papers = loader.load_papers().get('papers', [])

        years = [p.get('year', 0) for p in papers if p.get('year')]
        if years:
            st.metric("Latest Paper", max(years))
            st.metric("Papers Range", f"{min(years)}-{max(years)}")

        st.markdown("---")

        st.markdown("#### Relevance Legend")
        st.markdown("🔴 **CRITICAL** - Directly applicable")
        st.markdown("🟡 **HIGH** - Important insights")
        st.markdown("🔵 **MEDIUM** - Background context")


def main():
    """Main page entry point."""
    render_header()

    # Help section
    render_page_help(
        "Research Intelligence",
        "Curated database of breakthrough BCI papers and leading research labs.",
        [
            "Papers are scored for Neuralace relevance (CRITICAL/HIGH/MEDIUM)",
            "Filter by year, category, or relevance level",
            "Labs are rated by collaboration potential",
            "Click on any paper/lab for detailed information"
        ]
    )

    # Sidebar
    render_sidebar()

    # Overview metrics
    render_overview_metrics()

    st.divider()

    # Main content in tabs
    tab1, tab2, tab3 = st.tabs(["📄 Papers", "🔬 Labs", "📰 Journals"])

    with tab1:
        col1, col2 = st.columns([3, 1])
        with col1:
            render_papers_browser()
        with col2:
            render_relevance_chart()

    with tab2:
        render_labs_directory()

    with tab3:
        render_journals()

    # Footer
    st.divider()
    st.caption("Research Intelligence Database v1.0 | Updated 2026-01-30")


if __name__ == "__main__":
    main()
