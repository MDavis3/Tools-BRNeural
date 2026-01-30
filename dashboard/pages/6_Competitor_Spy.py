"""
Competitor Spy Page
===================

Monitor competitor sitemaps to detect new pages, product launches, and strategic shifts.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import io
import gzip
from datetime import datetime
from typing import Dict, List, Tuple, Set
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

import streamlit as st
import pandas as pd
import plotly.express as px
import requests

from utils.theme import apply_custom_css, get_plotly_layout
from components.metrics import render_metric_row
from components.help_system import render_page_help


EMOJI_SPY = "\U0001F575\ufe0f"
EMOJI_TARGET = "\U0001F3AF"
EMOJI_CHART = "\U0001F4CA"
EMOJI_ALERT = "\U0001F6A8"
EMOJI_EXPORT = "\U0001F4E4"
EMOJI_FOLDER = "\U0001F4C2"
EMOJI_PIN = "\U0001F4CD"
EMOJI_SEARCH = "\U0001F50D"

# Page configuration
st.set_page_config(
    page_title="Competitor Spy | BCI Intelligence Hub",
    page_icon=EMOJI_SPY,
    layout="wide"
)

apply_custom_css()


DEFAULT_COMPETITORS = [
    {"name": "Neuralink", "domain": "neuralink.com"},
    {"name": "Synchron", "domain": "synchron.com"},
    {"name": "Paradromics", "domain": "paradromics.com"},
    {"name": "Precision Neuroscience", "domain": "precisionneuroscience.com"},
    {"name": "Cortigent", "domain": "cortigent.com"},
]

SIGNAL_PATTERNS = {
    "Product / Features": [r"/product", r"/features", r"/solutions", r"/platform"],
    "Pricing / Plans": [r"/pricing", r"/plan", r"/enterprise", r"/tier", r"/quote"],
    "Integrations / Partners": [r"/integrations", r"/partners", r"/partner", r"/alliances"],
    "Docs / API": [r"/docs", r"/developer", r"/api", r"/sdk"],
    "Careers / Hiring": [r"/careers", r"/jobs", r"/hiring", r"/open-roles"],
    "Press / News": [r"/press", r"/news", r"/media", r"/blog", r"/insights"],
    "Clinical / Trials": [r"/clinical", r"/trial", r"/study", r"/research"],
    "Regulatory": [r"/fda", r"/regulatory", r"/clearance", r"/approval"],
}

USER_AGENT = "BCI-Intelligence-Hub/2.1 (sitemap-monitor)"


def normalize_domain(raw: str) -> str:
    raw = (raw or "").strip()
    if not raw:
        return ""
    raw = raw.replace("https://", "").replace("http://", "")
    raw = raw.split("/")[0]
    return raw.strip().lower()


def as_base_url(domain_or_url: str) -> str:
    if domain_or_url.startswith("http://") or domain_or_url.startswith("https://"):
        return domain_or_url.rstrip("/")
    return f"https://{domain_or_url}".rstrip("/")


@st.cache_data(ttl=900)
def fetch_bytes(url: str) -> Tuple[int, bytes, str]:
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
    return resp.status_code, resp.content, resp.headers.get("content-type", "")


def decode_sitemap_content(content: bytes, content_type: str, url: str) -> str:
    is_gzip = url.endswith(".gz") or "gzip" in (content_type or "").lower()
    if is_gzip:
        with gzip.GzipFile(fileobj=io.BytesIO(content)) as gz:
            return gz.read().decode("utf-8", errors="replace")
    return content.decode("utf-8", errors="replace")


def parse_sitemap_xml(xml_text: str) -> Tuple[str, List[Dict[str, str]]]:
    root = ET.fromstring(xml_text)
    tag = root.tag.split("}", 1)[-1].lower()

    if tag == "sitemapindex":
        items = []
        for sm in root.findall(".//{*}sitemap"):
            loc = sm.findtext(".//{*}loc") or ""
            lastmod = sm.findtext(".//{*}lastmod") or ""
            if loc:
                items.append({"loc": loc.strip(), "lastmod": lastmod.strip()})
        return "index", items

    items = []
    for url in root.findall(".//{*}url"):
        loc = url.findtext(".//{*}loc") or ""
        lastmod = url.findtext(".//{*}lastmod") or ""
        if loc:
            items.append({"loc": loc.strip(), "lastmod": lastmod.strip()})
    return "urlset", items


def discover_sitemaps(domain: str, use_robots: bool = True) -> List[str]:
    base = as_base_url(domain)
    sitemaps = []

    if use_robots:
        robots_url = f"{base}/robots.txt"
        try:
            status, content, _ = fetch_bytes(robots_url)
            if status == 200:
                text = content.decode("utf-8", errors="replace")
                for line in text.splitlines():
                    if line.lower().startswith("sitemap:"):
                        sitemap_url = line.split(":", 1)[1].strip()
                        if sitemap_url:
                            sitemaps.append(sitemap_url)
        except Exception:
            pass

    if not sitemaps:
        sitemaps.append(f"{base}/sitemap.xml")

    return list(dict.fromkeys(sitemaps))


def collect_urls_for_domain(domain: str,
                            max_sitemaps: int = 20,
                            use_robots: bool = True) -> Tuple[List[Dict], List[str]]:
    sitemap_queue = discover_sitemaps(domain, use_robots=use_robots)
    visited = set()
    errors = []
    results = []

    while sitemap_queue and len(visited) < max_sitemaps:
        sitemap_url = sitemap_queue.pop(0)
        if sitemap_url in visited:
            continue
        visited.add(sitemap_url)

        try:
            status, content, content_type = fetch_bytes(sitemap_url)
            if status != 200:
                errors.append(f"{sitemap_url} (HTTP {status})")
                continue

            xml_text = decode_sitemap_content(content, content_type, sitemap_url)
            kind, items = parse_sitemap_xml(xml_text)

            if kind == "index":
                for item in items:
                    if item["loc"] and item["loc"] not in visited:
                        sitemap_queue.append(item["loc"])
            else:
                for item in items:
                    results.append({
                        "domain": domain,
                        "url": item["loc"],
                        "lastmod": item.get("lastmod", "")
                    })
        except Exception as e:
            errors.append(f"{sitemap_url} ({e})")

    return results, errors


def tag_url(url: str) -> List[str]:
    tags = []
    path = urlparse(url).path.lower()
    for label, patterns in SIGNAL_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, path):
                tags.append(label)
                break
    return tags


def build_dataframe(rows: List[Dict]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=["domain", "url", "path", "lastmod", "signals"])

    df = pd.DataFrame(rows)
    df["path"] = df["url"].apply(lambda u: urlparse(u).path)
    df["signals"] = df["url"].apply(lambda u: ", ".join(tag_url(u)) or "General")
    return df


def render_header():
    st.markdown(f"""
    <h1 class="main-header">{EMOJI_SPY} Competitor Spy</h1>
    <p class="sub-header">Track competitor sitemaps to spot launches, pricing changes, and strategic shifts early</p>
    """, unsafe_allow_html=True)


def render_purpose():
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="nav-card">
            <div class="nav-card-icon">{EMOJI_TARGET}</div>
            <div class="nav-card-title">1) Add targets</div>
            <div class="nav-card-desc">
                Enter competitor domains. We auto-discover sitemaps from robots.txt
                or use /sitemap.xml directly.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="nav-card">
            <div class="nav-card-icon">{EMOJI_SEARCH}</div>
            <div class="nav-card-title">2) Scan URLs</div>
            <div class="nav-card-desc">
                Parse sitemap indexes and URL lists, then tag pages by signal type
                (product, pricing, integrations, clinical, etc.).
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="nav-card">
            <div class="nav-card-icon">{EMOJI_ALERT}</div>
            <div class="nav-card-title">3) Spot changes</div>
            <div class="nav-card-desc">
                Compare against a baseline to highlight new URLs that may indicate
                upcoming launches or strategic moves.
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_sidebar() -> Dict:
    with st.sidebar:
        st.markdown(f"### {EMOJI_SPY} Competitor Spy")
        st.markdown("---")

        st.markdown("#### Targets")
        use_defaults = st.checkbox("Use default BCI competitor list", value=True)
        default_domains = "\\n".join([c["domain"] for c in DEFAULT_COMPETITORS])
        domains_input = st.text_area(
            "Competitor domains (one per line)",
            value=default_domains if use_defaults else "",
            height=140
        )

        st.markdown("---")
        st.markdown("#### Collection")
        use_robots = st.checkbox("Discover sitemaps via robots.txt", value=True)
        max_sitemaps = st.slider("Max sitemaps to scan per domain", 3, 50, 20)

        st.markdown("---")
        st.markdown("#### Baseline Comparison")
        compare_session = st.checkbox("Compare with last run (this session)", value=True)
        baseline_file = st.file_uploader(
            "Upload baseline CSV (optional)",
            type=["csv"]
        )

        st.markdown("---")
        st.markdown("#### How to use")
        st.caption("Add domains, click Scan, then review New URLs + Signal Pages.")

        return {
            "domains": [normalize_domain(d) for d in domains_input.splitlines() if normalize_domain(d)],
            "use_robots": use_robots,
            "max_sitemaps": max_sitemaps,
            "compare_session": compare_session,
            "baseline_file": baseline_file
        }


def baseline_from_upload(upload) -> Dict[str, Set[str]]:
    if upload is None:
        return {}
    df = pd.read_csv(upload)
    if "domain" not in df.columns or "url" not in df.columns:
        return {}
    return df.groupby("domain")["url"].apply(set).to_dict()


def render_results(domains: List[str], use_robots: bool, max_sitemaps: int,
                   compare_session: bool, baseline_upload) -> None:
    if not domains:
        st.warning("Add at least one competitor domain to begin.")
        return

    baseline_uploaded = baseline_from_upload(baseline_upload)
    session_baseline = st.session_state.get("competitor_spy_baseline", {})

    all_rows = []
    error_log = {}
    progress = st.progress(0)

    for idx, domain in enumerate(domains):
        rows, errors = collect_urls_for_domain(domain, max_sitemaps=max_sitemaps, use_robots=use_robots)
        error_log[domain] = errors
        all_rows.extend(rows)
        progress.progress((idx + 1) / len(domains))

    progress.empty()

    if not all_rows:
        st.error("No sitemap URLs found. Check domains or try disabling robots.txt discovery.")
        return

    df = build_dataframe(all_rows).drop_duplicates(subset=["domain", "url"])

    # Baseline comparison
    new_url_flags = []
    for _, row in df.iterrows():
        domain = row["domain"]
        url = row["url"]
        baseline_set = set()
        if compare_session:
            baseline_set |= set(session_baseline.get(domain, set()))
        baseline_set |= set(baseline_uploaded.get(domain, set()))
        new_url_flags.append(url not in baseline_set if baseline_set else False)

    df["new"] = new_url_flags

    # Save baseline to session
    if compare_session:
        st.session_state["competitor_spy_baseline"] = {
            d: set(df[df["domain"] == d]["url"]) for d in df["domain"].unique()
        }

    # Metrics
    total_urls = len(df)
    new_urls = int(df["new"].sum())
    total_domains = df["domain"].nunique()

    metrics = [
        {"icon": EMOJI_SEARCH, "label": "Domains Scanned", "value": total_domains, "delta": f"{max_sitemaps} sitemaps max"},
        {"icon": EMOJI_FOLDER, "label": "URLs Collected", "value": total_urls, "delta": "Unique URLs"},
        {"icon": EMOJI_ALERT, "label": "New URLs", "value": new_urls, "delta": "vs baseline"},
        {"icon": EMOJI_PIN, "label": "Signal Pages", "value": int((df['signals'] != 'General').sum()), "delta": "Tagged intel"},
    ]
    render_metric_row(metrics)

    # Signal distribution
    st.subheader(f"{EMOJI_CHART} Signal Breakdown")
    signal_counts = df["signals"].str.get_dummies(sep=", ").sum().sort_values(ascending=False)
    signal_df = pd.DataFrame({"Signal": signal_counts.index, "Count": signal_counts.values})
    fig = px.bar(signal_df, x="Count", y="Signal", orientation="h", title="Signal Tags Found")
    fig.update_layout(**get_plotly_layout(), height=360, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    # New URLs table
    st.subheader(f"{EMOJI_ALERT} Newly Detected URLs")
    new_df = df[df["new"]].sort_values(["domain", "url"])
    if new_df.empty:
        st.info("No new URLs detected for this baseline.")
    else:
        st.dataframe(new_df[["domain", "url", "path", "lastmod", "signals"]], use_container_width=True)

    # High-signal URLs
    st.subheader("High-Signal URLs")
    signal_df = df[df["signals"] != "General"].sort_values(["domain", "signals"])
    st.dataframe(signal_df[["domain", "url", "path", "lastmod", "signals"]], use_container_width=True)

    # Per-domain detail
    st.subheader(f"{EMOJI_FOLDER} Per-Domain URL Explorer")
    for domain in df["domain"].unique():
        with st.expander(f"{domain} ({len(df[df['domain'] == domain])} URLs)"):
            st.dataframe(
                df[df["domain"] == domain][["url", "path", "lastmod", "signals", "new"]],
                use_container_width=True,
                hide_index=True
            )

        if error_log.get(domain):
            st.caption(f"Errors: {', '.join(error_log[domain][:3])}")

    # Export
    st.subheader(f"{EMOJI_EXPORT} Export")
    csv = df.to_csv(index=False)
    st.download_button(
        "Download Sitemap URLs CSV",
        data=csv,
        file_name=f"competitor_sitemaps_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )

    st.info("Tip: Upload this CSV later as a baseline to detect changes across sessions.")


def main():
    render_header()

    render_page_help(
        "Competitor Spy",
        "Monitor competitor sitemaps to surface new product pages, integrations, pricing changes, and strategic moves before they are announced.",
        [
            "Sitemaps often include unpublished URLs before public launches",
            "Use robots.txt discovery for better coverage when available",
            "Upload a baseline CSV to detect new URLs across sessions",
            "Combine this with external monitors (Visualping, Distill) for alerts"
        ]
    )

    render_purpose()
    st.markdown("---")

    settings = render_sidebar()

    if st.button("Scan Sitemaps", type="primary"):
        render_results(
            settings["domains"],
            settings["use_robots"],
            settings["max_sitemaps"],
            settings["compare_session"],
            settings["baseline_file"]
        )


if __name__ == "__main__":
    main()
