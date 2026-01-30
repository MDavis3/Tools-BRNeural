"""
Patient Voice Analysis Page
===========================

Interactive visualization of patient pain points and BCI market intelligence.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

from neuralace_engine.ingestor import PatientDataIngestor
from neuralace_engine.analyzer import PainPointAnalyzer
from neuralace_engine.statistics import StatisticalAnalyzer
from neuralace_engine.competitors import CompetitorAnalyzer
from neuralace_engine.trends import TrendAnalyzer

# Import dashboard utilities
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.theme import apply_custom_css, get_plotly_layout, THEME
from components.metrics import render_metric_row
from components.help_system import render_page_help


# Page configuration
st.set_page_config(
    page_title="Patient Voice | BCI Intelligence Hub",
    page_icon="👥",
    layout="wide"
)

apply_custom_css()


@st.cache_data(ttl=300)
def load_data(mode: str = "simulation"):
    """Load patient data."""
    ingestor = PatientDataIngestor(mode=mode)
    data = ingestor.fetch_data(subreddits=['ALS', 'spinalcordinjuries'], limit=100)
    return data


@st.cache_data(ttl=300)
def analyze_data(data, period: str = '30d'):
    """Run full analysis pipeline."""
    analyzer = PainPointAnalyzer(use_sentiment=True)
    analysis = analyzer.analyze(data)

    stats_analyzer = StatisticalAnalyzer()
    stats = stats_analyzer.full_statistical_report(analysis)

    comp_analyzer = CompetitorAnalyzer()
    competitors = comp_analyzer.analyze(data)

    trend_analyzer = TrendAnalyzer()
    trends = trend_analyzer.analyze_trends(data, period=period, analyzer=analyzer)

    return {
        'analysis': analysis,
        'statistics': stats,
        'competitors': competitors,
        'trends': trends
    }


def render_header():
    """Render page header."""
    st.markdown("""
    <h1 class="main-header">👥 Patient Voice Analysis</h1>
    <p class="sub-header">Real-time BCI Patient Sentiment & Pain Point Analysis</p>
    """, unsafe_allow_html=True)


def render_key_metrics(analysis, stats):
    """Render key metrics cards."""
    top_pp = analysis.get('top_pain_point', 'N/A')
    top_pct = 0
    if top_pp and top_pp in analysis.get('categories', {}):
        top_pct = analysis['categories'][top_pp].get('percentage', 0)

    p_value = stats['chi_square']['p_value']
    sig_text = "Significant" if stats['chi_square']['significant'] else "Not Significant"

    metrics = [
        {
            'icon': '📊',
            'label': 'Comments Analyzed',
            'value': analysis.get('total_analyzed', 0),
            'delta': f"{analysis.get('filtered_by_sentiment', 0)} positive filtered",
            'help_text': 'Total patient comments analyzed from community data'
        },
        {
            'icon': '🎯',
            'label': 'Top Pain Point',
            'value': top_pp,
            'delta': f"{top_pct}% of mentions",
            'help_text': 'Most frequently mentioned patient concern'
        },
        {
            'icon': '📈',
            'label': 'Statistical Significance',
            'value': sig_text,
            'delta': f"p={p_value}",
            'help_text': 'Chi-square test for distribution significance'
        },
        {
            'icon': '💪',
            'label': 'Effect Size',
            'value': f"{stats['effect_size']['cramers_v']:.3f}",
            'delta': stats['effect_size']['interpretation'],
            'help_text': "Cramer's V measure of association strength"
        },
    ]

    render_metric_row(metrics)


def render_pain_point_chart(analysis):
    """Render pain point distribution chart."""
    categories = analysis.get('categories', {})
    if not categories:
        st.warning("No pain point data available")
        return

    data = []
    for cat, info in categories.items():
        data.append({
            'Category': cat,
            'Count': info.get('count', 0),
            'Percentage': info.get('percentage', 0),
        })

    df = pd.DataFrame(data)
    df = df.sort_values('Percentage', ascending=True)

    fig = px.bar(
        df,
        x='Percentage',
        y='Category',
        orientation='h',
        color='Percentage',
        color_continuous_scale=['#1dd1a1', '#feca57', '#ff6b6b'],
        title='Pain Point Distribution by Category'
    )

    layout = get_plotly_layout()
    fig.update_layout(
        **layout,
        xaxis_title="Percentage of Mentions (%)",
        yaxis_title="",
        showlegend=False,
        height=400,
        coloraxis_showscale=False
    )

    st.plotly_chart(fig, use_container_width=True)


def render_sentiment_distribution(analysis):
    """Render sentiment distribution pie chart."""
    sentiment = analysis.get('sentiment_distribution', {})
    if not sentiment:
        st.info("No sentiment data available")
        return

    fig = go.Figure(data=[go.Pie(
        labels=list(sentiment.keys()),
        values=list(sentiment.values()),
        hole=0.4,
        marker_colors=['#1dd1a1', '#ff6b6b', '#feca57']
    )])

    layout = get_plotly_layout()
    fig.update_layout(
        **layout,
        title='Sentiment Distribution',
        height=300
    )

    st.plotly_chart(fig, use_container_width=True)


def render_trends(trends):
    """Render trend analysis."""
    st.subheader("📈 Trend Analysis")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**🔥 Emerging Concerns**")
        if trends.emerging_concerns:
            for cat in trends.emerging_concerns:
                trend = trends.category_trends.get(cat)
                if trend:
                    st.markdown(f"↑ **{cat}**: +{trend.change}%")
        else:
            st.caption("_None detected_")

    with col2:
        st.markdown("**📉 Declining Concerns**")
        if trends.declining_concerns:
            for cat in trends.declining_concerns:
                trend = trends.category_trends.get(cat)
                if trend:
                    st.markdown(f"↓ **{cat}**: {trend.change}%")
        else:
            st.caption("_None detected_")

    with col3:
        st.markdown("**→ Stable Concerns**")
        for cat in trends.stable_concerns[:3]:
            trend = trends.category_trends.get(cat)
            if trend:
                st.markdown(f"→ **{cat}**: {trend.change:+.1f}%")


def render_competitors(competitors):
    """Render competitor analysis."""
    st.subheader("🏢 Competitor Mentions in Patient Communities")

    if competitors.total_competitor_mentions == 0:
        st.info("No competitor mentions detected in the current dataset.")
        return

    data = []
    for name, profile in competitors.competitors.items():
        data.append({
            'Competitor': name,
            'Mentions': profile.mention_count,
            'Percentage': f"{profile.percentage}%",
            'Positive': profile.sentiment_breakdown.get('positive', 0),
            'Negative': profile.sentiment_breakdown.get('negative', 0),
            'Switching Intent': profile.switching_intent_count
        })

    df = pd.DataFrame(data)
    df = df.sort_values('Mentions', ascending=False)

    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown(f"**Landscape Summary:** {competitors.competitive_landscape}")


def render_quotes(analysis):
    """Render representative patient quotes."""
    st.subheader("💬 Representative Patient Quotes")

    categories = analysis.get('categories', {})

    for cat, info in sorted(categories.items(), key=lambda x: -x[1].get('count', 0)):
        quotes = info.get('quotes', [])
        if quotes:
            with st.expander(f"**{cat}** ({info.get('count', 0)} mentions)"):
                for i, quote_info in enumerate(quotes[:3]):
                    if isinstance(quote_info, dict):
                        text = quote_info.get('text', '')
                        conf = quote_info.get('confidence', 0)
                        st.markdown(f"> _{text}_")
                        st.caption(f"Confidence: {conf:.2f}")
                    else:
                        st.markdown(f"> _{quote_info}_")
                    if i < 2:
                        st.divider()


def render_neuralace_advantage(analysis):
    """Render Neuralace competitive advantage."""
    st.subheader("✨ Neuralace Competitive Advantage")

    top_pp = analysis.get('top_pain_point')
    advantage = analysis.get('neuralace_advantage')
    quote = analysis.get('representative_quote')

    if top_pp and advantage:
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"**Top Pain Point:** {top_pp}")
        with col2:
            st.info(f"**Neuralace Solution:** {advantage}")
        if quote:
            st.markdown(f"**Patient Voice:** _{quote}_")
    else:
        st.warning("Insufficient data to determine competitive advantage.")


def render_sidebar():
    """Render sidebar controls."""
    with st.sidebar:
        st.markdown("### ⚙️ Analysis Settings")

        # Data mode
        mode = st.radio(
            "Data Source",
            options=['simulation', 'live'],
            index=0,
            help="Use simulation for demo data, live for Reddit API"
        )

        if mode == 'live':
            st.warning("Live mode requires Reddit API credentials")

        # Time period
        period = st.selectbox(
            "Trend Analysis Period",
            options=['7d', '30d', '90d'],
            index=1
        )

        st.markdown("---")

        # Filters
        st.markdown("### 🔍 Filters")
        show_sentiment = st.checkbox("Show Sentiment Analysis", value=True)
        show_trends = st.checkbox("Show Trend Analysis", value=True)
        show_competitors = st.checkbox("Show Competitor Analysis", value=True)

        return {
            'mode': mode,
            'period': period,
            'show_sentiment': show_sentiment,
            'show_trends': show_trends,
            'show_competitors': show_competitors
        }


def main():
    """Main page entry point."""
    render_header()

    # Help section
    render_page_help(
        "Patient Voice Analysis",
        "Analyzes patient community discussions to identify pain points with current BCI devices.",
        [
            "Use simulation mode for quick demo with pre-loaded data",
            "Pain points are categorized into 8 key areas",
            "Sentiment filtering removes positive/neutral comments to focus on pain points",
            "Neuralace advantage shows how our technology addresses the top concern"
        ]
    )

    # Sidebar settings
    settings = render_sidebar()

    # Load and analyze data
    with st.spinner("Loading patient data..."):
        data = load_data(mode=settings['mode'])

    with st.spinner("Analyzing pain points..."):
        results = analyze_data(data, period=settings['period'])

    analysis = results['analysis']
    stats = results['statistics']
    competitors = results['competitors']
    trends = results['trends']

    # Warning for small samples
    if stats['sample_assessment'].get('warning'):
        st.warning(stats['sample_assessment']['warning'])

    # Key metrics
    render_key_metrics(analysis, stats)

    st.divider()

    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Pain Points",
        "📈 Trends & Stats",
        "🏢 Competitors",
        "💬 Quotes"
    ])

    with tab1:
        col1, col2 = st.columns([2, 1])
        with col1:
            render_pain_point_chart(analysis)
        with col2:
            if settings['show_sentiment']:
                render_sentiment_distribution(analysis)

        render_neuralace_advantage(analysis)

    with tab2:
        if settings['show_trends']:
            render_trends(trends)

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Chi-Square Test Results")
            st.json(stats['chi_square'])
        with col2:
            st.markdown("### Sample Assessment")
            st.json(stats['sample_assessment'])

    with tab3:
        if settings['show_competitors']:
            render_competitors(competitors)

    with tab4:
        render_quotes(analysis)

    # Footer
    st.divider()
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Patient Voice Engine v2.0")


if __name__ == "__main__":
    main()
