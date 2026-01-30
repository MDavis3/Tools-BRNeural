"""
BCI Intelligence Hub - Main Landing Page
=========================================

Unified dashboard for Blackrock Neurotech's BCI market intelligence,
regulatory guidance, and research insights.

Run with: streamlit run dashboard/app.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

from utils.theme import apply_custom_css, THEME
from utils.data_loader import get_data_loader
from components.metrics import render_metric_row
from components.help_system import render_welcome_section, render_glossary, init_session_state


# Page configuration
st.set_page_config(
    page_title="BCI Intelligence Hub | Blackrock Neurotech",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling
apply_custom_css()


def render_header():
    """Render the main header."""
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 2rem 0;">
        <h1 class="main-header">🧠 BCI Intelligence Hub</h1>
        <p class="sub-header">Unified Market Intelligence for Blackrock Neurotech</p>
    </div>
    """, unsafe_allow_html=True)


def render_navigation_cards():
    """Render navigation cards to each section."""
    icon_reg = "📋"
    icon_research = "📚"
    icon_comp = "🏢"
    icon_reports = "📊"
    icon_spy = "🕵️"

    st.markdown("### Explore Intelligence Tools")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="nav-card">
            <div class="nav-card-icon">{icon_reg}</div>
            <div class="nav-card-title">Regulatory Navigator</div>
            <div class="nav-card-desc">
                FDA pathway guidance, predicate device search, and
                competitor regulatory status tracking.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Regulatory ->", key="nav_regulatory", use_container_width=True):
            st.switch_page("pages/2_Regulatory_Navigator.py")

    with col2:
        st.markdown(f"""
        <div class="nav-card">
            <div class="nav-card-icon">{icon_research}</div>
            <div class="nav-card-title">Research Intelligence</div>
            <div class="nav-card-desc">
                Curated database of breakthrough papers, leading labs,
                and key researchers in neural interfaces.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Research ->", key="nav_research", use_container_width=True):
            st.switch_page("pages/3_Research_Intel.py")

    st.markdown("<br>", unsafe_allow_html=True)

    col3, col4, col5 = st.columns(3)

    with col3:
        st.markdown(f"""
        <div class="nav-card">
            <div class="nav-card-icon">{icon_comp}</div>
            <div class="nav-card-title">Competitive Landscape</div>
            <div class="nav-card-desc">
                Unified view of all BCI competitors - technology comparison,
                regulatory status, and market positioning.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Competitors ->", key="nav_competitors", use_container_width=True):
            st.switch_page("pages/4_Competitive_Landscape.py")

    with col4:
        st.markdown(f"""
        <div class="nav-card">
            <div class="nav-card-icon">{icon_reports}</div>
            <div class="nav-card-title">Strategic Reports</div>
            <div class="nav-card-desc">
                Executive insights combining all intelligence sources,
                custom AI analysis, and exportable reports.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Reports ->", key="nav_reports", use_container_width=True):
            st.switch_page("pages/5_Strategic_Reports.py")

    with col5:
        st.markdown(f"""
        <div class="nav-card">
            <div class="nav-card-icon">{icon_spy}</div>
            <div class="nav-card-title">Competitor Spy</div>
            <div class="nav-card-desc">
                Monitor competitor sitemaps to detect new pages,
                pricing changes, and strategic signals early.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Spy ->", key="nav_spy", use_container_width=True):
            st.switch_page("pages/6_Competitor_Spy.py")


def render_quick_stats():
    """Render quick overview statistics."""
    loader = get_data_loader()
    stats = loader.get_stats_summary()

    st.markdown("### Quick Overview")

    metrics = [
        {
            'icon': '📄',
            'label': 'Research Papers',
            'value': stats.get('total_papers', 0),
            'delta': f"{stats.get('critical_papers', 0)} critical relevance",
            'help_text': 'Curated papers on BCI technology with Neuralace relevance scoring'
        },
        {
            'icon': '🔬',
            'label': 'Research Labs',
            'value': stats.get('total_labs', 0),
            'delta': f"{stats.get('high_collab_labs', 0)} high collaboration potential",
            'help_text': 'Leading research institutions in neural interfaces'
        },
        {
            'icon': '📋',
            'label': 'FDA Pathways',
            'value': stats.get('fda_pathways', 0),
            'delta': 'With BCI examples',
            'help_text': 'Regulatory pathways analyzed for BCI devices'
        },
        {
            'icon': '🏢',
            'label': 'Competitors Tracked',
            'value': stats.get('total_companies', 0),
            'delta': 'Commercial BCI companies',
            'help_text': 'BCI companies with regulatory and technology tracking'
        },
    ]

    render_metric_row(metrics)


def render_sidebar():
    """Render sidebar with info and links."""
    icon_reg = "📋"
    icon_research = "📚"
    icon_comp = "🏢"
    icon_reports = "📊"
    icon_spy = "🕵️"

    with st.sidebar:
        st.markdown("### 🧠 BCI Intelligence Hub")
        st.markdown("---")

        st.markdown("#### About")
        st.markdown("""
        This platform provides unified market intelligence for
        Blackrock Neurotech's Neuralace development, combining:

        - **Regulatory** pathway guidance
        - **Research** literature database
        - **Competitive** landscape tracking
        - **Competitor Spy** sitemap monitoring
        """)

        st.markdown("---")

        st.markdown("#### Quick Links")
        st.page_link("pages/2_Regulatory_Navigator.py", label=f"{icon_reg} Regulatory", icon="2️⃣")
        st.page_link("pages/3_Research_Intel.py", label=f"{icon_research} Research", icon="3️⃣")
        st.page_link("pages/4_Competitive_Landscape.py", label=f"{icon_comp} Competitors", icon="4️⃣")
        st.page_link("pages/5_Strategic_Reports.py", label=f"{icon_reports} Reports", icon="5️⃣")
        st.page_link("pages/6_Competitor_Spy.py", label=f"{icon_spy} Spy", icon="6️⃣")

        st.markdown("---")

        st.markdown("#### Data Status")
        st.success("All systems operational", icon="✅")

        st.markdown("---")

        st.caption("Blackrock Neurotech | Neuralace Intelligence")
        st.caption("v2.0 - BCI Intelligence Hub")


def main():
    """Main application entry point."""
    # Initialize session state
    init_session_state()

    # Render sidebar
    render_sidebar()

    # Main content
    render_header()

    # Welcome section for new users
    render_welcome_section()

    # Quick statistics
    render_quick_stats()

    st.markdown("<br>", unsafe_allow_html=True)

    # Navigation cards
    render_navigation_cards()

    st.markdown("<br>", unsafe_allow_html=True)

    # Glossary at bottom
    render_glossary()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #a0a0a0; font-size: 0.85rem;">
        BCI Intelligence Hub v2.0 | Powered by Neuralace Intelligence Stack
        <br>
        Built for Blackrock Neurotech
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
