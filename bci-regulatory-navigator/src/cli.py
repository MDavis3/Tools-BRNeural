#!/usr/bin/env python3
"""
BCI Regulatory Pathway Navigator - CLI Interface
An AI-powered tool for understanding FDA regulatory pathways for brain-computer interface devices.

Designed for Blackrock Neurotech regulatory analysis.
Created by Manav Davis (Brown University)
"""
import sys
import json
import argparse
from pathlib import Path
from typing import Optional

# Fix encoding for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, OSError):
        pass

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from search_engine import RegulatorySearchEngine, format_search_results
from document_loader import get_document_summary, load_json_file
from config import DATA_DIR, RESEARCH_DIR


class RegulatoryNavigator:
    """Main CLI application for regulatory pathway navigation."""
    
    def __init__(self):
        self.engine = RegulatorySearchEngine()
        self._initialized = False
    
    def initialize(self, force_rebuild: bool = False):
        """Initialize the search engine."""
        if not self._initialized or force_rebuild:
            print("Initializing BCI Regulatory Navigator...")
            self.engine.initialize(force_rebuild=force_rebuild)
            self._initialized = True
            print("Ready!\n")
    
    def search(self, query: str, top_k: int = 5, show_full: bool = True) -> None:
        """Search the knowledge base."""
        self.initialize()
        results = self.engine.search(query, top_k=top_k)
        print(format_search_results(results, show_content=show_full))
    
    def get_pathway_info(self, pathway: str) -> None:
        """Get detailed information about a specific regulatory pathway."""
        pathways_file = DATA_DIR / "fda_pathways.json"
        if not pathways_file.exists():
            print("Pathways data not found.")
            return
        
        data = load_json_file(pathways_file)
        pathway_lower = pathway.lower()
        
        for p in data.get("pathways", []):
            if pathway_lower in p["id"].lower() or pathway_lower in p["name"].lower():
                self._display_pathway(p)
                return
        
        print(f"Pathway '{pathway}' not found.")
        print("Available pathways: " + ", ".join(p["id"] for p in data.get("pathways", [])))
    
    def _display_pathway(self, pathway: dict) -> None:
        """Display pathway information in a formatted way."""
        print(f"\n{'='*60}")
        print(f"[PATHWAY] {pathway['name']} ({pathway['id'].upper()})")
        print(f"{'='*60}")
        print(f"\n{pathway['description']}")
        
        if "device_class" in pathway:
            print(f"\n[CLASS] Device Classes: {', '.join(pathway['device_class'])}")
        
        if "typical_timeline_days" in pathway:
            print(f"[TIME] Typical Timeline: {pathway['typical_timeline_days']} days")
        
        if "fda_fee_usd" in pathway:
            print(f"[COST] FDA Fee: ${pathway['fda_fee_usd']:,}")
        
        if "requirements" in pathway:
            print("\n[REQUIREMENTS]")
            for req in pathway["requirements"]:
                print(f"   * {req}")
        
        if "advantages" in pathway:
            print("\n[ADVANTAGES]")
            for adv in pathway["advantages"]:
                print(f"   + {adv}")
        
        if "limitations" in pathway:
            print("\n[LIMITATIONS]")
            for lim in pathway["limitations"]:
                print(f"   - {lim}")
        
        if "bci_examples" in pathway:
            print("\n[BCI EXAMPLES]")
            for ex in pathway["bci_examples"]:
                company = ex.get("company", "Unknown")
                device = ex.get("device", "Unknown")
                print(f"   * {company}: {device}")
    
    def get_company_info(self, company: str) -> None:
        """Get detailed information about a BCI company."""
        companies_file = DATA_DIR / "bci_companies.json"
        if not companies_file.exists():
            print("Companies data not found.")
            return
        
        data = load_json_file(companies_file)
        company_lower = company.lower()
        
        for c in data.get("companies", []):
            if company_lower in c["id"].lower() or company_lower in c["name"].lower():
                self._display_company(c)
                return
        
        print(f"Company '{company}' not found.")
        print("Available: " + ", ".join(c["name"] for c in data.get("companies", [])))
    
    def _display_company(self, company: dict) -> None:
        """Display company information."""
        print(f"\n{'='*60}")
        print(f"[COMPANY] {company['name']}")
        print(f"{'='*60}")
        
        if "founded" in company:
            print(f"Founded: {company['founded']}")
        if "headquarters" in company:
            print(f"HQ: {company['headquarters']}")
        if "focus" in company:
            print(f"Focus: {company['focus']}")
        
        if "products" in company:
            print("\n[PRODUCTS]")
            for prod in company["products"]:
                print(f"\n   {prod['name']}")
                print(f"   Type: {prod.get('type', 'N/A')}")
                print(f"   FDA Status: {prod.get('fda_status', 'N/A')}")
                if "electrode_count" in prod:
                    print(f"   Electrodes: {prod['electrode_count']}")
        
        if "regulatory_strategy" in company:
            strat = company["regulatory_strategy"]
            print("\n[REGULATORY STRATEGY]")
            for key, value in strat.items():
                key_formatted = key.replace("_", " ").title()
                print(f"   * {key_formatted}: {value}")
    
    def get_predicate_info(self, k_number: Optional[str] = None) -> None:
        """Get information about predicate devices."""
        predicates_file = DATA_DIR / "predicate_devices.json"
        if not predicates_file.exists():
            print("Predicate devices data not found.")
            return
        
        data = load_json_file(predicates_file)
        
        if k_number:
            k_upper = k_number.upper()
            for pred in data.get("predicate_devices", []):
                if k_upper in pred["k_number"]:
                    self._display_predicate(pred)
                    return
            print(f"Predicate '{k_number}' not found.")
        else:
            print("\n[PREDICATE DEVICES] Class II Cortical Electrodes")
            print("="*60)
            for pred in data.get("predicate_devices", []):
                print(f"\n{pred['k_number']}: {pred['device_name']}")
                print(f"   Manufacturer: {pred['manufacturer']}")
                print(f"   Clearance: {pred['clearance_date']}")
    
    def _display_predicate(self, pred: dict) -> None:
        """Display predicate device information."""
        print(f"\n{'='*60}")
        print(f"[PREDICATE] {pred['k_number']}: {pred['device_name']}")
        print(f"{'='*60}")
        print(f"Manufacturer: {pred['manufacturer']}")
        print(f"Clearance Date: {pred['clearance_date']}")
        print(f"Regulation: {pred['regulation_number']} ({pred['regulation_name']})")
        print(f"Product Code: {pred['product_code']}")
        print(f"Device Class: {pred['device_class']}")
        print(f"\nIntended Use: {pred['intended_use']}")
        
        if "technical_characteristics" in pred:
            print("\n[TECHNICAL CHARACTERISTICS]")
            for key, value in pred["technical_characteristics"].items():
                print(f"   * {key}: {value}")
    
    def list_documents(self) -> None:
        """List all available documents in the knowledge base."""
        summary = get_document_summary()
        
        print("\n[KNOWLEDGE BASE] BCI Regulatory Navigator")
        print("="*60)
        
        print("\n[RESEARCH DOCUMENTS]")
        for doc in summary["research_files"]:
            print(f"   * {doc['file']}")
            print(f"     {doc['title']}")
        
        print("\n[STRUCTURED DATA]")
        for doc in summary["data_files"]:
            print(f"   * {doc['file']}")
            print(f"     {doc['title']}")
    
    def interactive_mode(self) -> None:
        """Run in interactive mode."""
        self.initialize()
        
        print("\n" + "="*60)
        print("BCI REGULATORY PATHWAY NAVIGATOR")
        print("="*60)
        print("""
Welcome! This tool helps you navigate FDA regulatory pathways
for brain-computer interface devices.

Commands:
  search <query>     - Search the knowledge base
  pathway <name>     - Get pathway details (510k, de_novo, pma, ide, breakthrough)
  company <name>     - Get company info (blackrock, neuralink, synchron, etc.)
  predicate [k#]     - List or lookup predicate devices
  docs               - List available documents
  help               - Show this help message
  quit               - Exit the navigator

Example queries:
  * "510(k) pathway for cortical electrodes"
  * "Blackrock MoveAgain regulatory status"
  * "Medicare reimbursement for BCI"
  * "predicate devices for brain interface"
""")
        
        while True:
            try:
                user_input = input("\nNavigator> ").strip()
                
                if not user_input:
                    continue
                
                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""
                
                if command in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    break
                elif command == "help":
                    print("Commands: search, pathway, company, predicate, docs, help, quit")
                elif command == "search":
                    if args:
                        self.search(args, top_k=3)
                    else:
                        print("Usage: search <query>")
                elif command == "pathway":
                    if args:
                        self.get_pathway_info(args)
                    else:
                        print("Available pathways: 510k, de_novo, pma, ide, breakthrough, hde")
                elif command == "company":
                    if args:
                        self.get_company_info(args)
                    else:
                        print("Available: blackrock, neuralink, synchron, precision, paradromics, cognixion, neurolutions")
                elif command == "predicate":
                    self.get_predicate_info(args if args else None)
                elif command == "docs":
                    self.list_documents()
                elif command == "rebuild":
                    self.initialize(force_rebuild=True)
                else:
                    # Treat unknown commands as search queries
                    self.search(user_input, top_k=3)
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="BCI Regulatory Pathway Navigator - FDA guidance for brain-computer interfaces",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py                           # Interactive mode
  python cli.py search "510k BCI"         # Search query
  python cli.py pathway 510k              # Pathway details
  python cli.py company blackrock         # Company info
  python cli.py predicate K242618         # Predicate device lookup
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search the knowledge base")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("-n", "--num", type=int, default=5, help="Number of results")
    search_parser.add_argument("--brief", action="store_true", help="Show brief results")
    
    # Pathway command
    pathway_parser = subparsers.add_parser("pathway", help="Get pathway information")
    pathway_parser.add_argument("name", help="Pathway name (510k, de_novo, pma, ide, breakthrough)")
    
    # Company command
    company_parser = subparsers.add_parser("company", help="Get company information")
    company_parser.add_argument("name", help="Company name")
    
    # Predicate command
    predicate_parser = subparsers.add_parser("predicate", help="Get predicate device information")
    predicate_parser.add_argument("k_number", nargs="?", help="510(k) number (optional)")
    
    # Docs command
    subparsers.add_parser("docs", help="List available documents")
    
    # Rebuild command
    subparsers.add_parser("rebuild", help="Rebuild the search index")
    
    args = parser.parse_args()
    
    navigator = RegulatoryNavigator()
    
    if args.command == "search":
        navigator.search(args.query, top_k=args.num, show_full=not args.brief)
    elif args.command == "pathway":
        navigator.get_pathway_info(args.name)
    elif args.command == "company":
        navigator.get_company_info(args.name)
    elif args.command == "predicate":
        navigator.get_predicate_info(args.k_number)
    elif args.command == "docs":
        navigator.list_documents()
    elif args.command == "rebuild":
        navigator.initialize(force_rebuild=True)
    else:
        # Default: interactive mode
        navigator.interactive_mode()


if __name__ == "__main__":
    main()
