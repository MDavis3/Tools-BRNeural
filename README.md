# BCI Intelligence Tools for Blackrock Neurotech

**Author:** Manav Davis  

**Email:** manav_davis@brown.edu 

**LinkedIn:** https://www.linkedin.com/in/manavdavis313/  

**Created:** January 2026

---

## Overview

This repository contains AI-powered intelligence tools built to support market research and business development for Blackrock Neurotech, with a specific focus on **Neuralace** — their next-generation 10,000+ channel brain-computer interface.

These tools demonstrate the intersection of **AI capabilities** and **BCI domain expertise**, showcasing how intelligent automation can accelerate regulatory intelligence, competitive analysis, and scientific literature monitoring.

---

## 🧠 Tools Included

### 1. BCI Regulatory Pathway Navigator
**Location:** `bci-regulatory-navigator/`

An AI-powered tool for navigating FDA regulatory pathways for brain-computer interface devices.

**Features:**
- 📋 Comprehensive research on FDA pathways (510(k), De Novo, PMA, IDE, Breakthrough)
- 🏢 Competitive landscape analysis (Neuralink, Synchron, Precision, Paradromics)
- 💰 Medicare reimbursement pathway research (TCET, NCDs, LCDs)
- 📊 Predicate device database with 510(k) clearance history
- 🔍 Python CLI with semantic search over 200+ indexed document chunks

**Key Deliverables:**
- Strategic recommendations for Blackrock's MoveAgain and Neuralace regulatory approach
- Analysis of Precision Neuroscience's successful 510(k) strategy
- TCET pathway guidance for Medicare coverage

**Usage:**
```bash
cd bci-regulatory-navigator/src
python cli.py                        # Interactive mode
python cli.py company blackrock      # Company lookup
python cli.py search "Neuralace"     # Search knowledge base
python cli.py pathway 510k           # Pathway details
```

---

### 2. BCI Literature Intelligence Agent
**Location:** `bci-literature-agent/`

An AI agent for tracking neural interface research papers, labs, and key researchers.

**Features:**
- 🔬 Database of 18+ leading BCI research labs worldwide
- 📚 Curated research summaries on Neuralace-relevant topics
- 👥 Key researcher profiles for collaboration targeting
- 🏷️ Topic-specific research briefs

**Research Topics Covered:**
- High-channel-count electrode arrays (1000+ channels)
- Flexible/conformable neural substrates
- Visual cortical prostheses
- Mental health neuromodulation (depression, anxiety)
- Chronic biocompatibility solutions

**Usage:**
```bash
cd bci-literature-agent/src
python cli.py                        # Interactive mode
python cli.py lab stanford-nptl      # Lab lookup
python cli.py search "depression"    # Topic search
```

---

## 🎯 Neuralace Focus

These tools were specifically designed with **Neuralace** in mind — Blackrock's next-generation BCI platform:

| Feature | Specification |
|---------|--------------|
| **Channel Count** | 10,000+ (vs 96 for NeuroPort) |
| **Form Factor** | Ultra-thin flexible "lace" chip |
| **Design** | Brain-conforming, porous structure |
| **Target Applications** | Vision restoration, memory, mental health |
| **Timeline** | Research tool 2024, visual prosthesis 2028 |

### Why Neuralace Needs These Tools

1. **Novel Regulatory Path** — No predicate exists for 10,000-channel flexible arrays
2. **Mental Health Indication** — Depression/anxiety BCIs have unique FDA requirements
3. **Visual Prosthesis Competition** — Cortigent/Orion is the key competitor
4. **Literature Velocity** — 100+ relevant papers/month require intelligent filtering

---

## 📊 Key Findings

### Regulatory Insights
- ✅ **Precision Neuroscience achieved 510(k) in 31 days** — proves hardware-first strategy works
- ✅ **TCET pathway (Aug 2024)** — Breakthrough devices get expedited Medicare coverage
- ✅ **IpsiHand precedent (Jan 2025)** — First BCI with CMS coverage, classified as DME
- ⚠️ **Mental health BCIs** require different clinical trial design than motor BCIs

### Competitive Position
| Company | Device | Status | Channel Count |
|---------|--------|--------|--------------|
| Blackrock | MoveAgain | Breakthrough designated | ~600 |
| Blackrock | Neuralace | R&D | 10,000+ |
| Precision | Layer 7-T | **510(k) CLEARED** | 1,024 |
| Neuralink | N1 | IDE trial | ~1,024 |
| Synchron | Stentrode | Pivotal planning | 16 |
| Paradromics | Connexus | IDE approved | 1,600+ |

### Strategic Recommendations
1. **Submit Neuralace hardware 510(k)** with limited claims (research use, <30 days)
2. **Engage TCET pathway immediately** for MoveAgain Medicare coverage
3. **Partner with UCSF Starr Lab** for depression BCI clinical pathway
4. **Monitor Cortigent/Orion** for visual prosthesis competitive intel

---

## 🛠️ Technical Architecture

Both tools use a similar architecture:

```
project/
├── research/          # Markdown research documents
├── data/              # Structured JSON databases
├── src/               # Python application code
│   ├── cli.py         # Command-line interface
│   ├── search_engine.py   # BM25 semantic search
│   └── document_loader.py # Document processing
└── index/             # Pre-built search indices
```

**Dependencies:** Python 3.8+ (standard library only — no external packages required)

---

## 📁 Repository Structure

```
Tools-BRNeural/
├── README.md                      # This file
├── PORTFOLIO.md                   # Executive summary for applications
├── bci-regulatory-navigator/      # Regulatory intelligence tool
│   ├── README.md
│   ├── requirements.txt
│   ├── research/                  # 6 research documents
│   ├── data/                      # 4 JSON databases
│   ├── src/                       # Python CLI
│   └── index/                     # Search index
└── bci-literature-agent/          # Literature monitoring tool
    ├── README.md
    ├── research/                  # 5 research documents
    ├── data/                      # 3 JSON databases
    └── src/                       # Python CLI
```

---

## 🚀 Future Expansion Ideas

1. **Web Dashboard** — React frontend for non-technical users
2. **Real-time FDA Monitoring** — Track new 510(k) clearances automatically
3. **PubMed/arXiv Integration** — Live paper alerts via API
4. **GPT-4/Claude Q&A** — Natural language regulatory queries
5. **QMS Integration** — Connect to regulatory management systems

---

## 📞 Contact

**Manav Davis**  
Brown University, Economics '25  
Seeking: Market Research & Business Development Intern @ Blackrock Neurotech

*These tools were built to demonstrate the power of AI-assisted competitive intelligence for the BCI industry. I'm excited about helping Neuralace find its footing in the market.*

---

## License

MIT License — See LICENSE file for details.
