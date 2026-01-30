"""
Competitive Landscape Page
==========================

Unified view of all BCI competitors with technology comparison and market positioning.
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


def render_header():
    """Render page header."""
    st.markdown("""
    <h1 class="main-header">🏢 Competitive Landscape</h1>
    <p class="sub-header">BCI Market Intelligence & Competitor Analysis</p>
    """, unsafe_allow_html=True)


def render_overview_metrics():
    """Render overview statistics."""
    loader = get_data_loader()
    competitors = loader.get_all_competitors()
    labs = loader.load_labs()

    # Count by type
    commercial = len([c for c in competitors if c.get('type') == 'Commercial'])
    research = len(labs.get('labs', []))

    metrics = [
        {'icon': '🏢', 'label': 'Commercial BCIs', 'value': commercial, 'delta': 'Active competitors'},
        {'icon': '🔬', 'label': 'Research Labs', 'value': research, 'delta': 'Academic institutions'},
        {'icon': '📊', 'label': 'Total Tracked', 'value': commercial + research, 'delta': 'Organizations monitored'},
        {'icon': '🎯', 'label': 'Direct Competitors', 'value': len([c for c in competitors if 'Direct' in c.get('competitive_position', '')]), 'delta': 'High-channel focus'},
    ]

    render_metric_row(metrics)


def render_company_matrix():
    """Render company comparison matrix."""
    st.subheader("📊 Company Comparison Matrix")

    loader = get_data_loader()
    companies = loader.load_bci_companies().get('companies', [])
    labs_companies = loader.load_labs().get('companies', [])

    # Combine companies
    all_companies = companies + labs_companies

    if not all_companies:
        st.warning("No company data available")
        return

    # Create comparison data
    data = []
    for c in all_companies:
        products = c.get('key_products', [])
        product_str = products[0] if products else 'N/A'

        # Extract channel count if mentioned
        channels = 'N/A'
        for p in products:
            if 'channel' in p.lower():
                # Try to extract number
                import re
                match = re.search(r'(\d+[,\d]*)\s*channel', p.lower())
                if match:
                    channels = match.group(1)

        data.append({
            'Company': c.get('name', 'Unknown'),
            'Key Product': product_str,
            'Channels': channels,
            'Focus Areas': ', '.join(c.get('focus_areas', [])[:2]),
            'Clinical Status': c.get('clinical_status', 'Unknown'),
            'Position': c.get('competitive_position', 'N/A'),
            'Funding': c.get('funding', 'N/A'),
        })

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_technology_comparison():
    """Render technology comparison chart."""
    st.subheader("⚡ Technology Comparison")

    # Hardcoded technology specs for visualization
    tech_data = [
        {'Company': 'Neuralink', 'Channels': 1024, 'Approach': 'Penetrating', 'Wireless': True},
        {'Company': 'Paradromics', 'Channels': 1600, 'Approach': 'Penetrating', 'Wireless': True},
        {'Company': 'Precision Neuro', 'Channels': 1024, 'Approach': 'Surface (ECoG)', 'Wireless': True},
        {'Company': 'Synchron', 'Channels': 16, 'Approach': 'Endovascular', 'Wireless': True},
        {'Company': 'BrainGate', 'Channels': 96, 'Approach': 'Utah Array', 'Wireless': False},
        {'Company': 'Blackrock', 'Channels': 128, 'Approach': 'Utah Array', 'Wireless': False},
        {'Company': 'Neuralace (Target)', 'Channels': 10000, 'Approach': 'Flexible', 'Wireless': True},
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
        {'Company': 'BrainGate', 'Channels': 96, 'Invasiveness': 4, 'Size': 20},
        {'Company': 'Neuralace', 'Channels': 10000, 'Invasiveness': 2, 'Size': 40},
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
    st.subheader("📋 Regulatory Progress Timeline")

    timeline_data = [
        {'Company': 'Neuralink', 'Event': 'IDE Approval', 'Date': '2023-05', 'Status': 'Clinical Trial'},
        {'Company': 'Neuralink', 'Event': 'First Human Implant', 'Date': '2024-01', 'Status': 'Active'},
        {'Company': 'Synchron', 'Event': 'IDE Approval', 'Date': '2021-08', 'Status': 'Clinical Trial'},
        {'Company': 'Synchron', 'Event': 'COMMAND Results', 'Date': '2024-06', 'Status': 'Positive'},
        {'Company': 'Paradromics', 'Event': 'IDE Approval', 'Date': '2025-11', 'Status': 'Preparing Trial'},
        {'Company': 'Precision', 'Event': '510(k) Clearance', 'Date': '2025-03', 'Status': 'Cleared'},
        {'Company': 'Blackrock', 'Event': 'Breakthrough Designation', 'Date': '2021-11', 'Status': 'Active'},
    ]

    df = pd.DataFrame(timeline_data)

    fig = px.timeline(
        df,
        x_start='Date',
        x_end='Date',
        y='Company',
        color='Status',
        title='Regulatory Milestones',
        hover_data=['Event'],
        color_discrete_sequence=THEME['chart_colors']
    )

    # Since timeline needs start/end, we'll use scatter instead
    fig = px.scatter(
        df,
        x='Date',
        y='Company',
        color='Status',
        size=[20] * len(df),
        hover_data=['Event'],
        title='Regulatory Milestones Timeline',
        color_discrete_sequence=THEME['chart_colors']
    )

    layout = get_plotly_layout()
    fig.update_layout(**layout, height=400)

    st.plotly_chart(fig, use_container_width=True)

    # Detailed table
    st.dataframe(df[['Company', 'Event', 'Date', 'Status']], use_container_width=True, hide_index=True)


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
        st.markdown("#### Strategic Position")
        st.info("""
        **vs Neuralink:** Higher channel count target, flexible vs rigid substrate

        **vs Synchron:** Much higher channel count, direct cortical vs endovascular

        **vs Paradromics:** Similar channel density, different substrate approach

        **vs Precision:** Similar thin-film approach, Blackrock's clinical experience
        """)


def render_sidebar():
    """Render sidebar."""
    with st.sidebar:
        st.markdown("### 🏢 Competitive Intel")
        st.markdown("---")

        st.markdown("#### Key Competitors")
        st.markdown("- **Neuralink** - N1 (1024 ch)")
        st.markdown("- **Paradromics** - Connexus (1600 ch)")
        st.markdown("- **Synchron** - Stentrode (16 ch)")
        st.markdown("- **Precision** - Layer 7 (1024 ch)")

        st.markdown("---")

        st.markdown("#### Neuralace Target")
        st.metric("Channel Count", "10,000+")
        st.metric("Approach", "Flexible")
        st.metric("Wireless", "Yes")


def main():
    """Main page entry point."""
    render_header()

    # Help section
    render_page_help(
        "Competitive Landscape",
        "Unified view of all BCI competitors with technology and regulatory tracking.",
        [
            "Compare channel counts, approaches, and clinical status",
            "View market positioning relative to competitors",
            "Track regulatory milestones across companies",
            "Understand Neuralace's competitive advantages"
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

    # Footer
    st.divider()
    st.caption("Competitive Intelligence v1.0 | Data updated regularly from public sources")


if __name__ == "__main__":
    main()
