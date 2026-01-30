"""
Help system components for new users.
"""

import streamlit as st
from typing import Dict


# BCI Glossary definitions
BCI_GLOSSARY = {
    "BCI": "Brain-Computer Interface - a system that enables direct communication between the brain and external devices",
    "ALS": "Amyotrophic Lateral Sclerosis - a progressive neurodegenerative disease affecting motor neurons",
    "ECoG": "Electrocorticography - recording brain activity from electrodes placed on the brain's surface",
    "510(k)": "FDA premarket notification demonstrating substantial equivalence to a predicate device",
    "De Novo": "FDA pathway for novel low-to-moderate risk devices without a predicate",
    "PMA": "Premarket Approval - FDA's most rigorous pathway for Class III high-risk devices",
    "IDE": "Investigational Device Exemption - allows unapproved devices in clinical studies",
    "Breakthrough Device": "FDA designation for innovative devices treating serious conditions",
    "TCET": "Transitional Coverage for Emerging Technologies - Medicare coverage pathway",
    "Channel Count": "Number of electrodes/recording sites in a neural interface",
    "Predicate Device": "Legally marketed device used for comparison in 510(k) submissions",
    "Neuralace": "Blackrock Neurotech's next-generation 10,000+ channel neural interface",
    "Utah Array": "A type of penetrating microelectrode array used in BCIs",
    "Neuropixels": "High-density silicon neural probes developed by HHMI/IMEC",
    "DBS": "Deep Brain Stimulation - electrical stimulation of brain structures for therapy",
    "Stentrode": "Synchron's endovascular BCI that doesn't require open brain surgery",
}


def render_help_tooltip(text: str, help_key: str = None) -> str:
    """
    Render inline help tooltip.

    Args:
        text: The text to display with help icon
        help_key: Optional glossary key to show definition

    Returns:
        HTML string with help tooltip
    """
    if help_key and help_key in BCI_GLOSSARY:
        tooltip = BCI_GLOSSARY[help_key]
    else:
        tooltip = text

    return f'{text} <span class="help-icon" title="{tooltip}">?</span>'


def render_welcome_section():
    """Render welcome section for new users on landing page."""
    st.markdown("""
    <div class="welcome-box">
        <h3 style="margin-top: 0;">Welcome to the BCI Intelligence Hub</h3>
        <p style="color: #a0a0a0; margin-bottom: 1rem;">
            Your unified platform for brain-computer interface market intelligence,
            regulatory guidance, and research insights.
        </p>
        <p style="margin-bottom: 0;">
            <strong>New here?</strong> Start with the <strong>Patient Voice</strong> tab to see
            real patient pain points, or explore <strong>Research Intel</strong> to discover
            breakthrough papers in the field.
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_glossary():
    """Render expandable BCI glossary."""
    with st.expander("BCI Terminology Glossary", expanded=False):
        cols = st.columns(2)
        terms = list(BCI_GLOSSARY.items())
        mid = len(terms) // 2

        with cols[0]:
            for term, definition in terms[:mid]:
                st.markdown(f"**{term}**")
                st.caption(definition)
                st.markdown("")

        with cols[1]:
            for term, definition in terms[mid:]:
                st.markdown(f"**{term}**")
                st.caption(definition)
                st.markdown("")


def render_page_help(page_name: str, description: str, tips: list):
    """
    Render help section for a specific page.

    Args:
        page_name: Name of the page
        description: Brief description of page purpose
        tips: List of helpful tips for using the page
    """
    with st.expander(f"Help: {page_name}", expanded=False):
        st.markdown(f"**About this page:** {description}")
        st.markdown("")
        st.markdown("**Tips:**")
        for tip in tips:
            st.markdown(f"- {tip}")


def render_quick_action(icon: str, title: str, description: str, page: str = None):
    """
    Render a quick action card for navigation.

    Args:
        icon: Emoji icon
        title: Action title
        description: Brief description
        page: Optional page to link to
    """
    st.markdown(f"""
    <div class="nav-card">
        <div class="nav-card-icon">{icon}</div>
        <div class="nav-card-title">{title}</div>
        <div class="nav-card-desc">{description}</div>
    </div>
    """, unsafe_allow_html=True)


def init_session_state():
    """Initialize session state for help system."""
    if 'first_visit' not in st.session_state:
        st.session_state.first_visit = True
    if 'show_welcome' not in st.session_state:
        st.session_state.show_welcome = True


def check_first_visit() -> bool:
    """Check if this is user's first visit."""
    init_session_state()
    if st.session_state.first_visit:
        st.session_state.first_visit = False
        return True
    return False


def render_feature_highlight(feature: str, description: str, new: bool = False):
    """Render a feature highlight badge."""
    new_badge = '<span class="badge badge-high">NEW</span> ' if new else ''
    st.markdown(f"""
    <div style="padding: 0.75rem; background: #1a1f2e; border-radius: 8px; margin-bottom: 0.5rem;">
        {new_badge}<strong>{feature}</strong>
        <div style="color: #a0a0a0; font-size: 0.85rem; margin-top: 0.25rem;">{description}</div>
    </div>
    """, unsafe_allow_html=True)
