"""
Theme configuration and custom CSS for BCI Intelligence Dashboard.
"""

import streamlit as st

# Color palette - Blackrock inspired with purple/blue accents
THEME = {
    'primary': '#667eea',
    'primary_light': '#764ba2',
    'secondary': '#1a1f2e',
    'background': '#0e1117',
    'surface': '#1a1f2e',
    'text': '#fafafa',
    'text_muted': '#a0a0a0',
    'success': '#1dd1a1',
    'warning': '#feca57',
    'error': '#ff6b6b',
    'info': '#54a0ff',

    # Relevance colors
    'critical': '#ff6b6b',
    'high': '#feca57',
    'medium': '#54a0ff',
    'low': '#1dd1a1',

    # Chart colors
    'chart_colors': ['#667eea', '#764ba2', '#54a0ff', '#1dd1a1', '#feca57', '#ff6b6b'],
}

# Plotly theme configuration
PLOTLY_THEME = {
    'template': 'plotly_dark',
    'paper_bgcolor': 'rgba(0,0,0,0)',
    'plot_bgcolor': 'rgba(0,0,0,0)',
    'font': {'color': THEME['text']},
    'colorway': THEME['chart_colors'],
}


def apply_custom_css():
    """Apply custom CSS styling to the dashboard."""
    st.markdown("""
    <style>
        /* Main container */
        .main {
            padding: 1rem 2rem;
        }

        /* Headers */
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0;
        }

        .sub-header {
            font-size: 1rem;
            color: #a0a0a0;
            margin-top: 0;
        }

        /* Metric cards */
        .metric-card {
            background: linear-gradient(135deg, #1a1f2e 0%, #252b3d 100%);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #2d3548;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }

        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
        }

        .metric-label {
            font-size: 0.9rem;
            color: #a0a0a0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* Navigation cards */
        .nav-card {
            background: linear-gradient(135deg, #1a1f2e 0%, #252b3d 100%);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #2d3548;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .nav-card:hover {
            border-color: #667eea;
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(102, 126, 234, 0.2);
        }

        .nav-card-icon {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }

        .nav-card-title {
            font-size: 1.1rem;
            font-weight: bold;
            color: #fafafa;
            margin-bottom: 0.5rem;
        }

        .nav-card-desc {
            font-size: 0.85rem;
            color: #a0a0a0;
        }

        /* Relevance badges */
        .badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: bold;
            text-transform: uppercase;
        }

        .badge-critical {
            background: rgba(255, 107, 107, 0.2);
            color: #ff6b6b;
            border: 1px solid #ff6b6b;
        }

        .badge-high {
            background: rgba(254, 202, 87, 0.2);
            color: #feca57;
            border: 1px solid #feca57;
        }

        .badge-medium {
            background: rgba(84, 160, 255, 0.2);
            color: #54a0ff;
            border: 1px solid #54a0ff;
        }

        /* Help tooltips */
        .help-icon {
            display: inline-block;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: #2d3548;
            color: #a0a0a0;
            text-align: center;
            line-height: 18px;
            font-size: 12px;
            cursor: help;
            margin-left: 5px;
        }

        /* Tables */
        .dataframe {
            background: #1a1f2e !important;
        }

        .dataframe th {
            background: #252b3d !important;
            color: #667eea !important;
        }

        .dataframe td {
            color: #fafafa !important;
        }

        /* Expanders */
        .streamlit-expanderHeader {
            background: #1a1f2e;
            border-radius: 8px;
        }

        /* Sidebar */
        .css-1d391kg {
            background: #0e1117;
        }

        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        /* Welcome box */
        .welcome-box {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
            border: 1px solid rgba(102, 126, 234, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }

        /* Status indicators */
        .status-active {
            color: #1dd1a1;
        }

        .status-pending {
            color: #feca57;
        }

        .status-inactive {
            color: #ff6b6b;
        }
    </style>
    """, unsafe_allow_html=True)


def render_badge(text: str, level: str = "medium") -> str:
    """Render a colored badge HTML."""
    return f'<span class="badge badge-{level.lower()}">{text}</span>'


def get_plotly_layout():
    """Get consistent Plotly layout settings."""
    return {
        'template': 'plotly_dark',
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font': {'color': THEME['text'], 'family': 'sans-serif'},
        'margin': {'t': 40, 'b': 40, 'l': 40, 'r': 40},
    }
