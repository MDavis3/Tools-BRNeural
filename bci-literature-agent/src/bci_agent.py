#!/usr/bin/env python3
"""
BCI Literature Intelligence Agent
AI-powered tool for tracking neural interface research papers.
Designed for Blackrock Neurotech / Neuralace competitive intelligence.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def load_json(filename: str) -> dict:
    """Load a JSON file from the data directory."""
    filepath = DATA_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Data file not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def load_papers() -> list:
    """Load the papers database."""
    data = load_json("papers.json")
    return data.get("papers", [])


def load_labs() -> list:
    """Load the labs database."""
    data = load_json("labs.json")
    return data.get("labs", [])


def load_researchers() -> list:
    """Load the researchers database."""
    data = load_json("researchers.json")
    return data.get("researchers", [])


def load_companies() -> list:
    """Load the companies from labs database."""
    data = load_json("labs.json")
    return data.get("companies", [])


def search_papers(
    query: str = None,
    categories: list = None,
    year_min: int = None,
    year_max: int = None,
    neuralace_relevance: str = None,
) -> list:
    """
    Search papers by various criteria.
    
    Args:
        query: Text search in title and abstract
        categories: List of categories to filter by
        year_min: Minimum publication year
        year_max: Maximum publication year
        neuralace_relevance: Filter by relevance (CRITICAL, HIGH, MEDIUM)
    
    Returns:
        List of matching papers
    """
    papers = load_papers()
    results = []
    
    for paper in papers:
        # Query search
        if query:
            query_lower = query.lower()
            title_match = query_lower in paper.get("title", "").lower()
            abstract_match = query_lower in paper.get("abstract_summary", "").lower()
            findings_match = any(
                query_lower in f.lower() 
                for f in paper.get("key_findings", [])
            )
            if not (title_match or abstract_match or findings_match):
                continue
        
        # Category filter
        if categories:
            paper_cats = paper.get("categories", [])
            if not any(cat in paper_cats for cat in categories):
                continue
        
        # Year filter
        paper_year = paper.get("year")
        if year_min and paper_year and paper_year < year_min:
            continue
        if year_max and paper_year and paper_year > year_max:
            continue
        
        # Neuralace relevance filter
        if neuralace_relevance:
            if paper.get("neuralace_relevance") != neuralace_relevance:
                continue
        
        results.append(paper)
    
    return results


def search_labs(
    focus_area: str = None,
    collaboration_priority: str = None,
) -> list:
    """
    Search labs by focus area or collaboration priority.
    
    Args:
        focus_area: Text to search in focus areas
        collaboration_priority: Filter by priority (CRITICAL, HIGH, MEDIUM)
    
    Returns:
        List of matching labs
    """
    labs = load_labs()
    results = []
    
    for lab in labs:
        if focus_area:
            focus_areas = lab.get("focus_areas", [])
            if not any(focus_area.lower() in fa.lower() for fa in focus_areas):
                continue
        
        if collaboration_priority:
            if lab.get("collaboration_potential") != collaboration_priority:
                continue
        
        results.append(lab)
    
    return results


def search_researchers(
    expertise: str = None,
    collaboration_priority: str = None,
) -> list:
    """
    Search researchers by expertise or collaboration priority.
    
    Args:
        expertise: Text to search in expertise areas
        collaboration_priority: Filter by priority (CRITICAL, HIGH, MEDIUM)
    
    Returns:
        List of matching researchers
    """
    researchers = load_researchers()
    results = []
    
    for researcher in researchers:
        if expertise:
            exp_areas = researcher.get("expertise", [])
            if not any(expertise.lower() in ea.lower() for ea in exp_areas):
                continue
        
        if collaboration_priority:
            if researcher.get("collaboration_priority") != collaboration_priority:
                continue
        
        results.append(researcher)
    
    return results


def get_neuralace_critical_papers() -> list:
    """Get all papers marked as CRITICAL relevance for Neuralace."""
    return search_papers(neuralace_relevance="CRITICAL")


def get_neuralace_focus_areas() -> dict:
    """Get papers organized by Neuralace focus areas."""
    focus_areas = {
        "high-channel": "High-Channel Arrays (1000+)",
        "flexible-electrodes": "Flexible/Conformable Interfaces",
        "visual-prosthesis": "Visual Prosthesis Research",
        "depression": "Depression Neuromodulation",
        "biocompatibility": "Chronic Biocompatibility",
    }
    
    results = {}
    for category, label in focus_areas.items():
        papers = search_papers(categories=[category])
        results[label] = papers
    
    return results


def generate_weekly_briefing(output_file: Optional[str] = None) -> str:
    """
    Generate a weekly briefing template for Blackrock/Neuralace.
    
    Args:
        output_file: Optional file path to save the briefing
    
    Returns:
        The briefing as a string
    """
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Get critical papers
    critical_papers = get_neuralace_critical_papers()
    
    # Get critical collaborators
    critical_researchers = search_researchers(collaboration_priority="CRITICAL")
    
    # Get competitors
    companies = load_companies()
    
    briefing = f"""# BCI Literature Intelligence Briefing
## Week of {today}
### Prepared for: Blackrock Neurotech / Neuralace Team

---

## 🔴 CRITICAL PAPERS FOR NEURALACE

"""
    
    for paper in critical_papers[:5]:
        briefing += f"""### {paper.get('title', 'Untitled')}
- **Journal:** {paper.get('journal', 'Unknown')} ({paper.get('year', 'N/A')})
- **DOI:** {paper.get('doi', 'N/A')}
- **Relevance:** {paper.get('relevance_notes', 'N/A')}
- **Key Findings:**
"""
        for finding in paper.get('key_findings', [])[:3]:
            briefing += f"  - {finding}\n"
        briefing += "\n"
    
    briefing += """---

## 🤝 PRIORITY COLLABORATION TARGETS

"""
    
    for researcher in critical_researchers[:5]:
        briefing += f"""### {researcher.get('name', 'Unknown')}
- **Institution:** {', '.join(researcher.get('institutions', ['Unknown']))}
- **Expertise:** {', '.join(researcher.get('expertise', [])[:3])}
- **Why critical:** {researcher.get('collaboration_notes', 'N/A')}

"""
    
    briefing += """---

## 📊 COMPETITIVE LANDSCAPE

"""
    
    for company in companies[:5]:
        briefing += f"""### {company.get('name', 'Unknown')}
- **Focus:** {', '.join(company.get('focus_areas', [])[:2])}
- **Key Product:** {', '.join(company.get('key_products', ['N/A'])[:1])}
- **Status:** {company.get('clinical_status', 'Unknown')}
- **Position:** {company.get('competitive_position', 'N/A')}

"""
    
    briefing += """---

## 📈 METRICS TO TRACK

| Technology | Current Best | Neuralace Target |
|------------|--------------|------------------|
| Channel Count | 5,120 (Neuropixels) | 10,000+ |
| Electrode Pitch | 6 µm (Neuropixels) | ~200-400 µm |
| Implant Time | 4+ hours (traditional) | <1 hour |
| Chronic Stability | 50-80% loss @ 5 years | <20% loss |

---

## 📚 PAPERS BY FOCUS AREA

"""
    
    focus_areas = get_neuralace_focus_areas()
    for area_name, papers in focus_areas.items():
        briefing += f"\n### {area_name}\n"
        briefing += f"Total papers in database: {len(papers)}\n\n"
        for paper in papers[:2]:
            briefing += f"- {paper.get('title', 'Untitled')} ({paper.get('year', 'N/A')})\n"
    
    briefing += """
---

## 🔔 ACTION ITEMS

1. [ ] Review new publications in high-channel arrays
2. [ ] Monitor TRANSCEND trial updates (Abbott depression DBS)
3. [ ] Track Orion visual prosthesis FDA status
4. [ ] Schedule outreach to CRITICAL-tier researchers
5. [ ] Update competitive analysis with Neuralink announcements

---

*Generated by BCI Literature Intelligence Agent*
*Last updated: """ + today + "*\n"
    
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(briefing)
        print(f"Briefing saved to: {output_path}")
    
    return briefing


def safe_print(text: str) -> None:
    """Print text with encoding fallback for Windows compatibility."""
    try:
        print(text)
    except UnicodeEncodeError:
        # Replace problematic characters for Windows console
        safe_text = text.encode('ascii', 'replace').decode('ascii')
        print(safe_text)


def print_paper_summary(paper: dict) -> None:
    """Print a formatted summary of a paper."""
    safe_print(f"\n{'='*60}")
    safe_print(f"TITLE: {paper.get('title', 'Untitled')}")
    safe_print(f"{'='*60}")
    safe_print(f"Journal: {paper.get('journal', 'Unknown')} ({paper.get('year', 'N/A')})")
    safe_print(f"DOI: {paper.get('doi', 'N/A')}")
    safe_print(f"URL: {paper.get('url', 'N/A')}")
    safe_print(f"\nNeuralace Relevance: {paper.get('neuralace_relevance', 'N/A')}")
    safe_print(f"Relevance Notes: {paper.get('relevance_notes', 'N/A')}")
    safe_print(f"\nCategories: {', '.join(paper.get('categories', []))}")
    safe_print(f"\nAbstract Summary:")
    safe_print(f"  {paper.get('abstract_summary', 'N/A')}")
    safe_print(f"\nKey Findings:")
    for finding in paper.get('key_findings', []):
        safe_print(f"  - {finding}")
    print()


def print_lab_summary(lab: dict) -> None:
    """Print a formatted summary of a lab."""
    print(f"\n{'='*60}")
    print(f"LAB: {lab.get('name', 'Unknown')}")
    print(f"{'='*60}")
    print(f"Institution: {lab.get('institution', 'Unknown')}")
    print(f"Location: {lab.get('location', 'Unknown')}")
    print(f"Website: {lab.get('website', 'N/A')}")
    print(f"PIs: {', '.join(lab.get('principal_investigators', []))}")
    print(f"\nCollaboration Potential: {lab.get('collaboration_potential', 'N/A')}")
    print(f"\nFocus Areas:")
    for area in lab.get('focus_areas', []):
        print(f"  • {area}")
    print(f"\nNeuralace Relevance:")
    for rel in lab.get('neuralace_relevance', []):
        print(f"  • {rel}")
    if lab.get('notes'):
        print(f"\nNotes: {lab.get('notes')}")
    print()


def print_researcher_summary(researcher: dict) -> None:
    """Print a formatted summary of a researcher."""
    print(f"\n{'='*60}")
    print(f"RESEARCHER: {researcher.get('name', 'Unknown')}")
    print(f"{'='*60}")
    print(f"Title: {researcher.get('title', 'Unknown')}")
    print(f"Institutions: {', '.join(researcher.get('institutions', []))}")
    print(f"Location: {researcher.get('location', 'Unknown')}")
    print(f"\nCollaboration Priority: {researcher.get('collaboration_priority', 'N/A')}")
    print(f"Collaboration Notes: {researcher.get('collaboration_notes', 'N/A')}")
    print(f"\nExpertise:")
    for exp in researcher.get('expertise', []):
        print(f"  • {exp}")
    print(f"\nKey Contributions:")
    for contrib in researcher.get('key_contributions', []):
        print(f"  • {contrib}")
    if researcher.get('h_index'):
        print(f"\nh-index: {researcher.get('h_index')}")
    print()


def interactive_menu():
    """Run an interactive menu for the BCI Literature Agent."""
    while True:
        print("\n" + "="*60)
        print("BCI LITERATURE INTELLIGENCE AGENT")
        print("="*60)
        print("\n1. Search papers")
        print("2. Search labs")
        print("3. Search researchers")
        print("4. Get Neuralace-critical papers")
        print("5. Generate weekly briefing")
        print("6. View papers by focus area")
        print("7. View competitive landscape")
        print("8. Exit")
        
        choice = input("\nEnter choice (1-8): ").strip()
        
        if choice == "1":
            query = input("Search query (or press Enter to skip): ").strip()
            category = input("Category filter (high-channel, flexible-electrodes, visual-prosthesis, depression, biocompatibility, or Enter to skip): ").strip()
            
            categories = [category] if category else None
            results = search_papers(query=query if query else None, categories=categories)
            
            print(f"\nFound {len(results)} papers:")
            for paper in results:
                print_paper_summary(paper)
        
        elif choice == "2":
            focus = input("Focus area search (or press Enter to skip): ").strip()
            priority = input("Collaboration priority (CRITICAL, HIGH, MEDIUM, or Enter to skip): ").strip().upper()
            
            results = search_labs(
                focus_area=focus if focus else None,
                collaboration_priority=priority if priority else None
            )
            
            print(f"\nFound {len(results)} labs:")
            for lab in results:
                print_lab_summary(lab)
        
        elif choice == "3":
            expertise = input("Expertise search (or press Enter to skip): ").strip()
            priority = input("Collaboration priority (CRITICAL, HIGH, MEDIUM, or Enter to skip): ").strip().upper()
            
            results = search_researchers(
                expertise=expertise if expertise else None,
                collaboration_priority=priority if priority else None
            )
            
            print(f"\nFound {len(results)} researchers:")
            for researcher in results:
                print_researcher_summary(researcher)
        
        elif choice == "4":
            papers = get_neuralace_critical_papers()
            print(f"\nFound {len(papers)} CRITICAL papers for Neuralace:")
            for paper in papers:
                print_paper_summary(paper)
        
        elif choice == "5":
            output = input("Save to file? (Enter filename or press Enter to skip): ").strip()
            briefing = generate_weekly_briefing(output_file=output if output else None)
            if not output:
                print(briefing)
        
        elif choice == "6":
            focus_areas = get_neuralace_focus_areas()
            for area_name, papers in focus_areas.items():
                print(f"\n{'='*60}")
                print(f"FOCUS AREA: {area_name}")
                print(f"{'='*60}")
                print(f"Total papers: {len(papers)}")
                for paper in papers[:3]:
                    print(f"\n  • {paper.get('title', 'Untitled')}")
                    print(f"    Year: {paper.get('year', 'N/A')}")
                    print(f"    Relevance: {paper.get('neuralace_relevance', 'N/A')}")
        
        elif choice == "7":
            companies = load_companies()
            print("\n" + "="*60)
            print("COMPETITIVE LANDSCAPE")
            print("="*60)
            for company in companies:
                print(f"\n{company.get('name', 'Unknown')}")
                print(f"  Focus: {', '.join(company.get('focus_areas', []))}")
                print(f"  Products: {', '.join(company.get('key_products', []))}")
                print(f"  Status: {company.get('clinical_status', 'Unknown')}")
                print(f"  Position: {company.get('competitive_position', 'N/A')}")
        
        elif choice == "8":
            print("\nGoodbye!")
            break
        
        else:
            print("\nInvalid choice. Please try again.")


# CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "search":
            query = sys.argv[2] if len(sys.argv) > 2 else None
            results = search_papers(query=query)
            for paper in results:
                print_paper_summary(paper)
        
        elif command == "critical":
            papers = get_neuralace_critical_papers()
            for paper in papers:
                print_paper_summary(paper)
        
        elif command == "briefing":
            output = sys.argv[2] if len(sys.argv) > 2 else None
            briefing = generate_weekly_briefing(output_file=output)
            if not output:
                print(briefing)
        
        elif command == "labs":
            priority = sys.argv[2] if len(sys.argv) > 2 else None
            results = search_labs(collaboration_priority=priority)
            for lab in results:
                print_lab_summary(lab)
        
        elif command == "researchers":
            priority = sys.argv[2] if len(sys.argv) > 2 else None
            results = search_researchers(collaboration_priority=priority)
            for researcher in results:
                print_researcher_summary(researcher)
        
        elif command == "help":
            print("""
BCI Literature Intelligence Agent

Usage:
    python bci_agent.py                    # Interactive mode
    python bci_agent.py search <query>     # Search papers
    python bci_agent.py critical           # Show Neuralace-critical papers
    python bci_agent.py briefing [file]    # Generate weekly briefing
    python bci_agent.py labs [priority]    # List labs (optional: CRITICAL, HIGH, MEDIUM)
    python bci_agent.py researchers [pri]  # List researchers
    python bci_agent.py help               # Show this help
            """)
        
        else:
            print(f"Unknown command: {command}")
            print("Run 'python bci_agent.py help' for usage information.")
    
    else:
        interactive_menu()
