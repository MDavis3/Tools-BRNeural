"""
Competitive Landscape Page
==========================

Unified view of all BCI competitors with technology comparison and market positioning.
Updated January 2026 with latest regulatory data.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.theme import apply_custom_css, get_plotly_layout, THEME
from utils.data_loader import get_data_loader
from components.metrics import render_metric_row
from components.help_system import render_page_help


# Page configuration
st.set_page_config(
    page_title="Competitive Landscape | BCI Intelligence Hub",
    page_icon="🏢",
    layout="wide"
)

apply_custom_css()

# Comprehensive competitor data (updated Jan 2026)
COMPETITOR_DATA = [
    {
        'Company': 'Neuralink',
        'Key Product': 'N1 Link Implant',
        'Channels': 1024,
        'Approach': 'Penetrating (threads)',
        'Clinical Status': '12 human implants (as of Sept 2025)',
        'FDA Status': 'IDE Approved (May 2023)',
        'Funding': '$650M+ (June 2025)',
        'Wireless': True,
    },
    {
        'Company': 'Synchron',
        'Key Product': 'Stentrode',
        'Channels': 16,
        'Approach': 'Endovascular',
        'Clinical Status': '10 patients implanted (US + Australia)',
        'FDA Status': 'IDE Approved, Pivotal Trial 2026',
        'Funding': '$200M Series D (Nov 2025)',
        'Wireless': True,
    },
    {
        'Company': 'Paradromics',
        'Key Product': 'Connexus BCI',
        'Channels': 1600,
        'Approach': 'Penetrating (microwires)',
        'Clinical Status': 'First-in-human recording completed',
        'FDA Status': 'IDE Approved (Nov 2025), Trial Q1 2026',
        'Funding': '$85M+',
        'Wireless': True,
    },
    {
        'Company': 'Precision Neuroscience',
        'Key Product': 'Layer 7 Cortical Interface',
        'Channels': 1024,
        'Approach': 'Surface (thin-film ECoG)',
        'Clinical Status': '37+ patients across 4 US institutions',
        'FDA Status': '510(k) Cleared (March 2025)',
        'Funding': '$100M+',
        'Wireless': True,
    },
    {
        'Company': 'Blackrock Neurotech',
        'Key Product': 'MoveAgain / NeuroPort',
        'Channels': '96-128 (Neuralace: 10,000+)',
        'Approach': 'Utah Array / Flexible (Neuralace)',
        'Clinical Status': '30,000+ patient days, 500+ institutions',
        'FDA Status': 'Breakthrough Designation (Nov 2021)',
        'Funding': 'Private (Tether backing)',
        'Wireless': False,
    },
    {
        'Company': 'Cognixion',
        'Key Product': 'ONE Headset',
        'Channels': 'Non-invasive EEG',
        'Approach': 'Non-invasive + AR',
        'Clinical Status': 'Commercial (DME supplier)',
        'FDA Status': 'Breakthrough Designation (2023)',
        'Funding': '$30M+',
        'Wireless': True,
    },
    {
        'Company': 'Neurolutions',
        'Key Product': 'IpsiHand',
        'Channels': 'Non-invasive EEG',
        'Approach': 'Non-invasive',
        'Clinical Status': 'Commercial (stroke rehab)',
        'FDA Status': 'De Novo Classified (2021)',
        'Funding': 'N/A',
        'Wireless': True,
    },
    {
        'Company': 'Cortigent (Second Sight)',
        'Key Product': 'Orion Visual Prosthesis',
        'Channels': 60,
        'Approach': 'Cortical (visual)',
        'Clinical Status': '5-year feasibility complete',
        'FDA Status': 'Breakthrough Designation',
        'Funding': 'Acquired by Vivani Medical',
        'Wireless': True,
    },
]

# Updated regulatory timeline (Jan 2026)
REGULATORY_TIMELINE = [
    {'Company': 'Synchron', 'Event': 'IDE Approval (first permanent BCI)', 'Date': '2021-08', 'Status': 'Completed'},
    {'Company': 'Blackrock', 'Event': 'MoveAgain Breakthrough Designation', 'Date': '2021-11', 'Status': 'Granted'},
    {'Company': 'Neuralink', 'Event': 'FDA IDE Approval', 'Date': '2023-05', 'Status': 'Completed'},
    {'Company': 'Neuralink', 'Event': 'First Human Implant (Noland Arbaugh)', 'Date': '2024-01', 'Status': 'Completed'},
    {'Company': 'Neuralink', 'Event': 'Blindsight Breakthrough Designation', 'Date': '2024-09', 'Status': 'Granted'},
    {'Company': 'Synchron', 'Event': 'COMMAND Trial Primary Endpoint Met', 'Date': '2024-10', 'Status': 'Positive'},
    {'Company': 'Precision', 'Event': '510(k) Clearance (Layer 7-T)', 'Date': '2025-03', 'Status': 'Cleared'},
    {'Company': 'Precision', 'Event': 'Nature BME Publication (37 patients)', 'Date': '2025-10', 'Status': 'Published'},
    {'Company': 'Paradromics', 'Event': 'FDA IDE Approval (Connexus)', 'Date': '2025-11', 'Status': 'Completed'},
    {'Company': 'Synchron', 'Event': '$200M Series D for Pivotal Trial', 'Date': '2025-11', 'Status': 'Funded'},
    {'Company': 'Neuralink', 'Event': '12th Human Implant', 'Date': '2025-09', 'Status': 'Completed'},
    {'Company': 'Paradromics', 'Event': 'Connect-One Trial Start', 'Date': '2026-Q1', 'Status': 'Planned'},
    {'Company': 'Synchron', 'Event': 'Pivotal Trial Start', 'Date': '2026', 'Status': 'Planned'},
]


def render_header():
    """Render page header."""
    st.markdown("""
    <h1 class="main-header">🏢 Competitive Landscape</h1>
    <p class="sub-header">BCI Market Intelligence & Competitor Analysis (Updated Jan 2026)</p>
    """, unsafe_allow_html=True)


def render_overview_metrics():
    """Render overview statistics."""
    loader = get_data_loader()
    labs = loader.load_labs()

    metrics = [
        {'icon': '🏢', 'label': 'Commercial BCIs', 'value': len(COMPETITOR_DATA), 'delta': 'Active competitors'},
        {'icon': '🔬', 'label': 'Research Labs', 'value': len(labs.get('labs', [])), 'delta': 'Academic institutions'},
        {'icon': '✅', 'label': 'FDA Cleared/Approved', 'value': 4, 'delta': 'IDE or 510(k)'},
        {'icon': '🎯', 'label': 'High-Channel (1000+)', 'value': 4, 'delta': 'Direct competitors'},
    ]

    render_metric_row(metrics)


def render_company_matrix():
    """Render company comparison matrix."""
    st.subheader("📊 Company Comparison Matrix")

    # Create DataFrame from curated data
    df = pd.DataFrame(COMPETITOR_DATA)

    # Select columns for display
    display_df = df[['Company', 'Key Product', 'Channels', 'Clinical Status', 'FDA Status', 'Funding']]

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.caption("Data updated January 2026 from public sources")


def render_technology_comparison():
    """Render technology comparison chart."""
    st.subheader("⚡ Technology Comparison")

    # Technology specs for visualization
    tech_data = [
        {'Company': 'Neuralink', 'Channels': 1024, 'Approach': 'Penetrating', 'Wireless': True},
        {'Company': 'Paradromics', 'Channels': 1600, 'Approach': 'Penetrating', 'Wireless': True},
        {'Company': 'Precision', 'Channels': 1024, 'Approach': 'Surface (ECoG)', 'Wireless': True},
        {'Company': 'Synchron', 'Channels': 16, 'Approach': 'Endovascular', 'Wireless': True},
        {'Company': 'Cortigent', 'Channels': 60, 'Approach': 'Cortical (Visual)', 'Wireless': True},
        {'Company': 'Blackrock (current)', 'Channels': 128, 'Approach': 'Utah Array', 'Wireless': False},
        {'Company': 'Neuralace (target)', 'Channels': 10000, 'Approach': 'Flexible', 'Wireless': True},
    ]

    df = pd.DataFrame(tech_data)

    col1, col2 = st.columns(2)

    with col1:
        # Channel count bar chart
        fig = px.bar(
            df.sort_values('Channels', ascending=True),
            x='Channels',
            y='Company',
            orientation='h',
            color='Channels',
            color_continuous_scale=['#54a0ff', '#667eea', '#764ba2'],
            title='Channel Count by Company'
        )
        layout = get_plotly_layout()
        fig.update_layout(**layout, showlegend=False, coloraxis_showscale=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Approach distribution
        approach_counts = df['Approach'].value_counts()
        fig = px.pie(
            values=approach_counts.values,
            names=approach_counts.index,
            title='Technology Approaches',
            color_discrete_sequence=THEME['chart_colors']
        )
        layout = get_plotly_layout()
        fig.update_layout(**layout, height=400)
        st.plotly_chart(fig, use_container_width=True)

    # Wireless capability
    st.markdown("#### Wireless Capability")
    col1, col2 = st.columns(2)
    wireless = df[df['Wireless'] == True]['Company'].tolist()
    wired = df[df['Wireless'] == False]['Company'].tolist()

    with col1:
        st.success(f"**Wireless:** {', '.join(wireless)}")
    with col2:
        st.warning(f"**Wired:** {', '.join(wired)}")


def render_market_positioning():
    """Render market positioning scatter plot."""
    st.subheader("🎯 Market Positioning Map")

    # Create positioning data (invasiveness vs channel count)
    positioning = [
        {'Company': 'Neuralink', 'Channels': 1024, 'Invasiveness': 4, 'Size': 30},
        {'Company': 'Paradromics', 'Channels': 1600, 'Invasiveness': 4, 'Size': 25},
        {'Company': 'Precision', 'Channels': 1024, 'Invasiveness': 3, 'Size': 25},
        {'Company': 'Synchron', 'Channels': 16, 'Invasiveness': 2, 'Size': 20},
        {'Company': 'Cortigent', 'Channels': 60, 'Invasiveness': 4, 'Size': 15},
        {'Company': 'Cognixion', 'Channels': 8, 'Invasiveness': 1, 'Size': 15},
        {'Company': 'Neuralace (target)', 'Channels': 10000, 'Invasiveness': 2, 'Size': 40},
    ]

    df = pd.DataFrame(positioning)

    fig = px.scatter(
        df,
        x='Invasiveness',
        y='Channels',
        size='Size',
        color='Company',
        text='Company',
        title='Market Position: Invasiveness vs Channel Count',
        labels={'Invasiveness': 'Invasiveness Level (1=Low, 5=High)', 'Channels': 'Channel Count'},
        color_discrete_sequence=THEME['chart_colors']
    )

    fig.update_traces(textposition='top center')

    layout = get_plotly_layout()
    fig.update_layout(
        **layout,
        height=500,
        xaxis=dict(ticktext=['Non-invasive', 'Minimally', 'Moderate', 'Surgical', 'Deep'], tickvals=[1, 2, 3, 4, 5]),
        yaxis_type='log'
    )

    # Add quadrant annotations
    fig.add_annotation(x=1.5, y=5000, text="Ideal Zone<br>(High channels, Low invasiveness)",
                      showarrow=False, font=dict(color=THEME['success']))

    st.plotly_chart(fig, use_container_width=True)

    st.info("**Neuralace Target:** High channel count (10,000+) with minimally invasive flexible substrate - positioned in the ideal zone.")


def render_regulatory_timeline():
    """Render regulatory progress timeline."""
    st.subheader("📋 Regulatory Progress Timeline (2021-2026)")

    df = pd.DataFrame(REGULATORY_TIMELINE)

    # Sort by date
    df_sorted = df.sort_values('Date')

    # Create scatter timeline
    fig = px.scatter(
        df_sorted,
        x='Date',
        y='Company',
        color='Status',
        size=[20] * len(df_sorted),
        hover_data=['Event'],
        title='BCI Regulatory Milestones',
        color_discrete_map={
            'Completed': '#1dd1a1',
            'Granted': '#54a0ff',
            'Cleared': '#667eea',
            'Positive': '#1dd1a1',
            'Published': '#54a0ff',
            'Funded': '#feca57',
            'Planned': '#a0a0a0',
        }
    )

    layout = get_plotly_layout()
    fig.update_layout(**layout, height=400)

    st.plotly_chart(fig, use_container_width=True)

    # Detailed table
    st.dataframe(df_sorted[['Company', 'Event', 'Date', 'Status']], use_container_width=True, hide_index=True)


def render_neuralace_advantage():
    """Render Neuralace competitive advantages."""
    st.subheader("✨ Neuralace Competitive Advantages")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Technology Differentiators")
        advantages = [
            ("10,000+ Channels", "Highest channel density in development"),
            ("Flexible Substrate", "Minimizes immune response and tissue damage"),
            ("Wireless Design", "No percutaneous connections"),
            ("Minimally Invasive", "Cranial micro-slit implantation possible"),
        ]

        for title, desc in advantages:
            st.success(f"**{title}**\n\n{desc}")

    with col2:
        st.markdown("#### Strategic Position vs Competitors")
        st.info("""
        **vs Neuralink (1024 ch):** 10x channel count, flexible vs rigid threads

        **vs Synchron (16 ch):** 600x channels, direct cortical vs endovascular

        **vs Paradromics (1600 ch):** 6x channels, flexible vs penetrating

        **vs Precision (1024 ch):** 10x channels, similar thin-film approach, Blackrock's 30K+ patient days experience
        """)


def render_sidebar():
    """Render sidebar."""
    with st.sidebar:
        st.markdown("### 🏢 Competitive Intel")
        st.markdown("---")

        st.markdown("#### Key Competitors")
        st.markdown("- **Neuralink** - N1 (1,024 ch)")
        st.markdown("- **Paradromics** - Connexus (1,600 ch)")
        st.markdown("- **Precision** - Layer 7 (1,024 ch)")
        st.markdown("- **Synchron** - Stentrode (16 ch)")

        st.markdown("---")

        st.markdown("#### Neuralace Target")
        st.metric("Channel Count", "10,000+")
        st.metric("Approach", "Flexible")
        st.metric("Wireless", "Yes")

        st.markdown("---")
        st.caption("Data updated Jan 2026")


def main():
    """Main page entry point."""
    render_header()

    # Help section
    render_page_help(
        "Competitive Landscape",
        "Unified view of all BCI competitors with technology and regulatory tracking.",
        [
            "Data updated January 2026 from public sources",
            "Compare channel counts, approaches, and clinical status",
            "View market positioning relative to competitors",
            "Track regulatory milestones across companies"
        ]
    )

    # Sidebar
    render_sidebar()

    # Overview metrics
    render_overview_metrics()

    st.divider()

    # Main content
    render_company_matrix()

    st.divider()

    render_technology_comparison()

    st.divider()

    render_market_positioning()

    st.divider()

    render_regulatory_timeline()

    st.divider()

    render_neuralace_advantage()

    # Footer with sources
    st.divider()
    st.markdown("""
    **Sources:**
    [Neuralink Updates](https://neuralink.com/updates/) |
    [Synchron News](https://synchron.com) |
    [Paradromics Press](https://paradromics.com/news) |
    [FDA 510(k) Database](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm)
    """)
    st.caption("Competitive Intelligence v2.0 | Last updated: January 2026")


if __name__ == "__main__":
    main()
