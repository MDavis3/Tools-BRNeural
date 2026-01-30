"""
Metric card components for displaying KPIs.
"""

import streamlit as st
from typing import Optional, List, Dict, Any


def render_metric_card(
    label: str,
    value: Any,
    delta: Optional[str] = None,
    icon: str = "",
    help_text: str = ""
):
    """
    Render a styled metric card.

    Args:
        label: Metric label/title
        value: Main value to display
        delta: Optional delta/change indicator
        icon: Optional emoji icon
        help_text: Optional help tooltip text
    """
    help_html = f'<span class="help-icon" title="{help_text}">?</span>' if help_text else ''
    delta_html = f'<div style="color: #667eea; font-size: 0.85rem;">{delta}</div>' if delta else ''

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{icon} {label} {help_html}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_metric_row(metrics: List[Dict]):
    """
    Render a row of metric cards.

    Args:
        metrics: List of dicts with keys: label, value, delta (optional), icon (optional), help_text (optional)
    """
    cols = st.columns(len(metrics))

    for col, metric in zip(cols, metrics):
        with col:
            render_metric_card(
                label=metric.get('label', ''),
                value=metric.get('value', ''),
                delta=metric.get('delta'),
                icon=metric.get('icon', ''),
                help_text=metric.get('help_text', '')
            )


def render_stat_card(title: str, items: List[Dict], icon: str = ""):
    """
    Render a card with multiple stat items.

    Args:
        title: Card title
        items: List of dicts with 'label' and 'value' keys
        icon: Optional emoji icon
    """
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 1.1rem; font-weight: bold; margin-bottom: 1rem;">
            {icon} {title}
        </div>
    """, unsafe_allow_html=True)

    for item in items:
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span style="color: #a0a0a0;">{item.get('label', '')}</span>
            <span style="font-weight: bold;">{item.get('value', '')}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_progress_metric(label: str, value: float, max_value: float = 100, color: str = "#667eea"):
    """
    Render a metric with a progress bar.

    Args:
        label: Metric label
        value: Current value
        max_value: Maximum value for percentage calculation
        color: Progress bar color
    """
    percentage = (value / max_value) * 100 if max_value > 0 else 0

    st.markdown(f"""
    <div style="margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
            <span style="color: #a0a0a0;">{label}</span>
            <span style="font-weight: bold;">{value:.1f}%</span>
        </div>
        <div style="background: #2d3548; border-radius: 4px; height: 8px; overflow: hidden;">
            <div style="background: {color}; height: 100%; width: {percentage}%; border-radius: 4px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
