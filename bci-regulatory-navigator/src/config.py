"""
BCI Regulatory Navigator Configuration
"""
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
RESEARCH_DIR = PROJECT_ROOT / "research"
DATA_DIR = PROJECT_ROOT / "data"

# Index settings
INDEX_FILE = PROJECT_ROOT / "index" / "document_index.json"
EMBEDDING_FILE = PROJECT_ROOT / "index" / "embeddings.pkl"

# Search settings
DEFAULT_TOP_K = 5
CHUNK_SIZE = 500  # characters per chunk
CHUNK_OVERLAP = 50  # overlap between chunks

# Supported file types
SUPPORTED_EXTENSIONS = [".md", ".json", ".txt"]
