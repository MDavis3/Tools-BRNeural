"""
Document Loader for BCI Regulatory Navigator
Loads and chunks research documents and structured data.
"""
import json
import re
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

from config import RESEARCH_DIR, DATA_DIR, CHUNK_SIZE, CHUNK_OVERLAP, SUPPORTED_EXTENSIONS


@dataclass
class Document:
    """Represents a document chunk for indexing."""
    id: str
    content: str
    source: str
    title: str
    chunk_index: int
    metadata: Dict[str, Any]


def load_markdown_file(file_path: Path) -> str:
    """Load a markdown file and return its content."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def load_json_file(file_path: Path) -> Dict:
    """Load a JSON file and return its content."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_title_from_markdown(content: str) -> str:
    """Extract the first H1 heading from markdown content."""
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "Untitled"


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split text into overlapping chunks.
    Tries to split on paragraph boundaries when possible.
    """
    # Split on double newlines (paragraphs)
    paragraphs = re.split(r'\n\n+', text)
    
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
            
        # If adding this paragraph would exceed chunk size
        if len(current_chunk) + len(para) + 2 > chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
                # Keep overlap from end of current chunk
                if overlap > 0 and len(current_chunk) > overlap:
                    current_chunk = current_chunk[-overlap:]
                else:
                    current_chunk = ""
            
            # If single paragraph is too long, split it
            if len(para) > chunk_size:
                words = para.split()
                temp_chunk = current_chunk
                for word in words:
                    if len(temp_chunk) + len(word) + 1 > chunk_size:
                        if temp_chunk:
                            chunks.append(temp_chunk.strip())
                            temp_chunk = temp_chunk[-overlap:] if overlap > 0 else ""
                    temp_chunk += " " + word if temp_chunk else word
                current_chunk = temp_chunk
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        else:
            current_chunk += "\n\n" + para if current_chunk else para
    
    # Don't forget the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks


def json_to_text(data: Any, prefix: str = "") -> str:
    """Convert JSON data to readable text for indexing."""
    lines = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            key_formatted = key.replace("_", " ").title()
            if isinstance(value, (dict, list)):
                lines.append(f"{prefix}{key_formatted}:")
                lines.append(json_to_text(value, prefix + "  "))
            else:
                lines.append(f"{prefix}{key_formatted}: {value}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, (dict, list)):
                lines.append(json_to_text(item, prefix))
                if i < len(data) - 1:
                    lines.append("")  # Add spacing between items
            else:
                lines.append(f"{prefix}- {item}")
    else:
        lines.append(f"{prefix}{data}")
    
    return "\n".join(lines)


def load_all_documents() -> List[Document]:
    """Load all documents from research and data directories."""
    documents = []
    doc_id = 0
    
    # Load markdown files from research directory
    if RESEARCH_DIR.exists():
        for file_path in sorted(RESEARCH_DIR.glob("*.md")):
            print(f"Loading: {file_path.name}")
            content = load_markdown_file(file_path)
            title = extract_title_from_markdown(content)
            
            # Chunk the content
            chunks = chunk_text(content)
            
            for i, chunk in enumerate(chunks):
                documents.append(Document(
                    id=f"doc_{doc_id}",
                    content=chunk,
                    source=str(file_path.relative_to(RESEARCH_DIR.parent)),
                    title=title,
                    chunk_index=i,
                    metadata={
                        "file_type": "markdown",
                        "total_chunks": len(chunks)
                    }
                ))
                doc_id += 1
    
    # Load JSON files from data directory
    if DATA_DIR.exists():
        for file_path in sorted(DATA_DIR.glob("*.json")):
            print(f"Loading: {file_path.name}")
            data = load_json_file(file_path)
            
            # Convert JSON to text
            text_content = json_to_text(data)
            title = file_path.stem.replace("_", " ").title()
            
            # Chunk the content
            chunks = chunk_text(text_content)
            
            for i, chunk in enumerate(chunks):
                documents.append(Document(
                    id=f"doc_{doc_id}",
                    content=chunk,
                    source=str(file_path.relative_to(DATA_DIR.parent)),
                    title=title,
                    chunk_index=i,
                    metadata={
                        "file_type": "json",
                        "total_chunks": len(chunks)
                    }
                ))
                doc_id += 1
    
    print(f"\nLoaded {len(documents)} document chunks")
    return documents


def get_document_summary() -> Dict[str, Any]:
    """Get a summary of available documents."""
    summary = {
        "research_files": [],
        "data_files": []
    }
    
    if RESEARCH_DIR.exists():
        for file_path in sorted(RESEARCH_DIR.glob("*.md")):
            content = load_markdown_file(file_path)
            title = extract_title_from_markdown(content)
            summary["research_files"].append({
                "file": file_path.name,
                "title": title
            })
    
    if DATA_DIR.exists():
        for file_path in sorted(DATA_DIR.glob("*.json")):
            summary["data_files"].append({
                "file": file_path.name,
                "title": file_path.stem.replace("_", " ").title()
            })
    
    return summary


if __name__ == "__main__":
    # Test loading
    docs = load_all_documents()
    print(f"\nSample document:")
    print(f"  ID: {docs[0].id}")
    print(f"  Title: {docs[0].title}")
    print(f"  Source: {docs[0].source}")
    print(f"  Content preview: {docs[0].content[:200]}...")
