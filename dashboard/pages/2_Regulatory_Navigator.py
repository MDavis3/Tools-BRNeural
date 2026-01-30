"""
Regulatory Navigator Page
=========================

FDA pathway guidance, predicate device search, and compliance tracking.
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
    page_title="Regulatory Navigator | BCI Intelligence Hub",
    page_icon="📋",
    layout="wide"
)

apply_custom_css()


def render_header():
    """Render page header."""
    st.markdown("""
    <h1 class="main-header">📋 Regulatory Navigator</h1>
    <p class="sub-header">FDA Pathway Guidance & Compliance Intelligence</p>
    """, unsafe_allow_html=True)


def render_pathway_comparison():
    """Render FDA pathway comparison table."""
    st.subheader("🛤️ FDA Regulatory Pathways")

    loader = get_data_loader()
    pathways_data = loader.load_fda_pathways()
    pathways = pathways_data.get('pathways', [])

    if not pathways:
        st.warning("No pathway data available")
        return

    # Create comparison table
    comparison = loader.get_pathway_comparison()
    df = pd.DataFrame(comparison)

    st.dataframe(df, use_container_width=True, hide_index=True)

    # Timeline visualization
    st.markdown("#### Timeline & Cost Comparison")

    timeline_data = []
    for p in pathways:
        timeline_data.append({
            'Pathway': p.get('name', ''),
            'Days': p.get('typical_timeline_days', 0),
            'Cost': p.get('fda_fee_usd', 0)
        })

    df_timeline = pd.DataFrame(timeline_data)

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            df_timeline,
            x='Pathway',
            y='Days',
            color='Days',
            color_continuous_scale=['#1dd1a1', '#feca57', '#ff6b6b'],
            title='Review Timeline (Days)'
        )
        layout = get_plotly_layout()
        fig.update_layout(**layout, showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            df_timeline,
            x='Pathway',
            y='Cost',
            color='Cost',
            color_continuous_scale=['#1dd1a1', '#feca57', '#ff6b6b'],
            title='FDA Fee ($)'
        )
        layout = get_plotly_layout()
        fig.update_layout(**layout, showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)


def render_pathway_details():
    """Render detailed pathway information."""
    st.subheader("📖 Pathway Details")

    loader = get_data_loader()
    pathways_data = loader.load_fda_pathways()
    pathways = pathways_data.get('pathways', [])

    if not pathways:
        return

    # Pathway selector
    pathway_names = [p.get('name', '') for p in pathways]
    selected = st.selectbox("Select a pathway to view details:", pathway_names)

    # Find selected pathway
    pathway = next((p for p in pathways if p.get('name') == selected), None)

    if pathway:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**Description:** {pathway.get('description', 'N/A')}")
            st.markdown(f"**Device Class:** {', '.join(pathway.get('device_class', []))}")
            st.markdown(f"**Timeline:** {pathway.get('typical_timeline_days', 'N/A')} days")
            st.markdown(f"**FDA Fee:** ${pathway.get('fda_fee_usd', 0):,}")

            clinical = pathway.get('clinical_data_required')
            if clinical == True:
                st.markdown("**Clinical Data:** Required")
            elif clinical == False:
                st.markdown("**Clinical Data:** Not Required")
            else:
                st.markdown(f"**Clinical Data:** {clinical}")

        with col2:
            st.markdown("**Requirements:**")
            for req in pathway.get('requirements', []):
                st.markdown(f"- {req}")

        # Advantages and limitations
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**✅ Advantages:**")
            for adv in pathway.get('advantages', []):
                st.success(adv, icon="✓")

        with col2:
            st.markdown("**⚠️ Limitations:**")
            for lim in pathway.get('limitations', []):
                st.warning(lim, icon="⚠")

        # BCI Examples
        examples = pathway.get('bci_examples', []) or pathway.get('bci_designations', [])
        if examples:
            st.markdown("**🧠 BCI Examples:**")
            for ex in examples:
                company = ex.get('company', 'Unknown')
                device = ex.get('device', 'Unknown')
                date = ex.get('clearance_date') or ex.get('designation_date') or ex.get('ide_approval_date', 'N/A')
                st.markdown(f"- **{company}** - {device} ({date})")


def render_predicate_search():
    """Render predicate device search."""
    st.subheader("🔍 Predicate Device Search")

    loader = get_data_loader()
    predicates_data = loader.load_predicate_devices()

    predicates = predicates_data.get('predicates', [])

    if not predicates:
        st.info("No predicate device data available")
        return

    # Search box
    search = st.text_input("Search predicates by name, company, or product code:", "")

    # Filter predicates
    filtered = predicates
    if search:
        search_lower = search.lower()
        filtered = [p for p in predicates if
                   search_lower in p.get('device_name', '').lower() or
                   search_lower in p.get('applicant', '').lower() or
                   search_lower in p.get('product_code', '').lower()]

    if filtered:
        data = []
        for p in filtered:
            data.append({
                'Device Name': p.get('device_name', ''),
                '510(k) Number': p.get('k_number', ''),
                'Applicant': p.get('applicant', ''),
                'Clearance Date': p.get('clearance_date', ''),
                'Product Code': p.get('product_code', ''),
            })

        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"Showing {len(filtered)} of {len(predicates)} predicate devices")
    else:
        st.info("No predicates match your search criteria")


def render_company_tracker():
    """Render competitor regulatory status tracker."""
    st.subheader("🏢 BCI Company Regulatory Status")

    loader = get_data_loader()
    companies_data = loader.load_bci_companies()
    companies = companies_data.get('companies', [])

    if not companies:
        st.info("No company data available")
        return

    # Create status table
    data = []
    for c in companies:
        data.append({
            'Company': c.get('name', ''),
            'Product': ', '.join(c.get('key_products', [])),
            'Regulatory Status': c.get('regulatory_status', 'Unknown'),
            'Breakthrough Device': '✓' if c.get('breakthrough_designation') else '-',
            'IDE Status': c.get('ide_status', '-'),
        })

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Status visualization
    st.markdown("#### Regulatory Progress by Company")

    stages = ['Pre-Submission', 'IDE', 'Clinical Trial', '510(k)/De Novo', 'Approved']

    fig = go.Figure()

    for i, company in enumerate(companies):
        name = company.get('name', '')
        status = company.get('regulatory_status', '')

        # Determine progress level
        progress = 1
        if 'IDE' in status:
            progress = 2
        if 'trial' in status.lower() or 'clinical' in status.lower():
            progress = 3
        if '510' in status or 'cleared' in status.lower():
            progress = 4
        if 'approved' in status.lower():
            progress = 5

        fig.add_trace(go.Bar(
            name=name,
            x=[progress],
            y=[name],
            orientation='h',
            marker_color=THEME['chart_colors'][i % len(THEME['chart_colors'])]
        ))

    layout = get_plotly_layout()
    fig.update_layout(
        **layout,
        barmode='group',
        xaxis=dict(
            ticktext=stages,
            tickvals=[1, 2, 3, 4, 5],
            title='Regulatory Stage'
        ),
        yaxis_title='',
        showlegend=False,
        height=300
    )

    st.plotly_chart(fig, use_container_width=True)


def render_reimbursement():
    """Render reimbursement pathway information."""
    st.subheader("💰 Reimbursement Pathways")

    loader = get_data_loader()
    reimb_data = loader.load_reimbursement()

    if not reimb_data:
        st.info("No reimbursement data available")
        return

    # TCET Information
    tcet = reimb_data.get('tcet', {})
    if tcet:
        st.markdown("#### TCET (Transitional Coverage for Emerging Technologies)")
        st.markdown(f"**Description:** {tcet.get('description', 'N/A')}")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Eligibility Criteria:**")
            for crit in tcet.get('eligibility', []):
                st.markdown(f"- {crit}")
        with col2:
            st.markdown("**Benefits:**")
            for ben in tcet.get('benefits', []):
                st.success(ben)

    # Coverage milestones
    milestones = reimb_data.get('milestones', [])
    if milestones:
        st.markdown("#### Coverage Milestones")
        for m in milestones:
            st.markdown(f"**{m.get('date', '')}** - {m.get('event', '')}")


def render_sidebar():
    """Render sidebar navigation."""
    with st.sidebar:
        st.markdown("### 📋 Regulatory Navigator")
        st.markdown("---")

        st.markdown("#### Sections")
        sections = [
            ("🛤️ Pathway Comparison", "pathway"),
            ("📖 Pathway Details", "details"),
            ("🔍 Predicate Search", "predicates"),
            ("🏢 Company Tracker", "companies"),
            ("💰 Reimbursement", "reimbursement"),
        ]

        selected = st.radio(
            "Jump to section:",
            options=[s[0] for s in sections],
            label_visibility="collapsed"
        )

        st.markdown("---")

        st.markdown("#### Quick Facts")
        st.info("**510(k)** is the fastest pathway (~90 days)")
        st.info("**PMA** is required for Class III devices")
        st.info("**Breakthrough** designation speeds review")

        return selected


def main():
    """Main page entry point."""
    render_header()

    # Help section
    render_page_help(
        "Regulatory Navigator",
        "Guides you through FDA regulatory pathways and tracks competitor compliance status.",
        [
            "Compare 6 FDA pathways: 510(k), De Novo, PMA, IDE, Breakthrough, HDE",
            "Search predicate devices for 510(k) submissions",
            "Track competitor regulatory progress",
            "Understand TCET reimbursement pathway for BCIs"
        ]
    )

    # Sidebar
    selected = render_sidebar()

    # Main content
    render_pathway_comparison()

    st.divider()

    render_pathway_details()

    st.divider()

    render_predicate_search()

    st.divider()

    render_company_tracker()

    st.divider()

    render_reimbursement()

    # Footer
    st.divider()
    st.caption("Data sourced from FDA public databases | Regulatory Navigator v1.0")


if __name__ == "__main__":
    main()
