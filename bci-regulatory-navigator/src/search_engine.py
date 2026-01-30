"""
Search Engine for BCI Regulatory Navigator
Uses TF-IDF with BM25-style ranking for semantic search.
"""
import json
import math
import pickle
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

from document_loader import Document, load_all_documents
from config import INDEX_FILE, EMBEDDING_FILE, DEFAULT_TOP_K


@dataclass
class SearchResult:
    """Represents a search result."""
    document_id: str
    content: str
    source: str
    title: str
    score: float
    chunk_index: int


class BM25Index:
    """
    BM25-based search index for document retrieval.
    BM25 is a sophisticated ranking function that improves upon TF-IDF.
    """
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        Initialize BM25 index.
        
        Args:
            k1: Term frequency saturation parameter (typically 1.2-2.0)
            b: Document length normalization (0 = no normalization, 1 = full)
        """
        self.k1 = k1
        self.b = b
        
        self.documents: List[Document] = []
        self.doc_lengths: List[int] = []
        self.avg_doc_length: float = 0.0
        self.inverted_index: Dict[str, List[Tuple[int, int]]] = defaultdict(list)
        self.doc_freqs: Dict[str, int] = Counter()
        self.vocab: set = set()
        
        # Stopwords for English
        self.stopwords = set([
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'were', 'will', 'with', 'the', 'this', 'but', 'they',
            'have', 'had', 'what', 'when', 'where', 'who', 'which', 'why', 'how',
            'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other',
            'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
            'than', 'too', 'very', 'can', 'just', 'should', 'now'
        ])
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize and normalize text."""
        # Convert to lowercase
        text = text.lower()
        
        # Extract words (including hyphenated terms and numbers)
        tokens = re.findall(r'\b[a-z0-9][-a-z0-9]*[a-z0-9]\b|\b[a-z0-9]+\b', text)
        
        # Remove stopwords and short tokens
        tokens = [t for t in tokens if t not in self.stopwords and len(t) > 1]
        
        return tokens
    
    def build_index(self, documents: List[Document]) -> None:
        """Build the BM25 index from documents."""
        self.documents = documents
        self.doc_lengths = []
        self.inverted_index = defaultdict(list)
        self.doc_freqs = Counter()
        self.vocab = set()
        
        # First pass: tokenize and build inverted index
        for doc_idx, doc in enumerate(documents):
            tokens = self.tokenize(doc.content)
            self.doc_lengths.append(len(tokens))
            
            # Count term frequencies in this document
            term_freqs = Counter(tokens)
            
            # Update inverted index and document frequencies
            for term, freq in term_freqs.items():
                self.inverted_index[term].append((doc_idx, freq))
                self.vocab.add(term)
            
            # Update document frequencies
            for term in set(tokens):
                self.doc_freqs[term] += 1
        
        # Calculate average document length
        self.avg_doc_length = sum(self.doc_lengths) / len(self.doc_lengths) if self.doc_lengths else 0
        
        print(f"Index built: {len(documents)} documents, {len(self.vocab)} unique terms")
    
    def _bm25_score(self, query_terms: List[str], doc_idx: int, doc_term_freqs: Dict[str, int]) -> float:
        """Calculate BM25 score for a document."""
        score = 0.0
        doc_length = self.doc_lengths[doc_idx]
        num_docs = len(self.documents)
        
        for term in query_terms:
            if term not in doc_term_freqs:
                continue
            
            tf = doc_term_freqs[term]
            df = self.doc_freqs.get(term, 0)
            
            # IDF component (with smoothing)
            idf = math.log((num_docs - df + 0.5) / (df + 0.5) + 1)
            
            # TF component with length normalization
            tf_norm = (tf * (self.k1 + 1)) / (tf + self.k1 * (1 - self.b + self.b * doc_length / self.avg_doc_length))
            
            score += idf * tf_norm
        
        return score
    
    def search(self, query: str, top_k: int = DEFAULT_TOP_K) -> List[SearchResult]:
        """
        Search the index for relevant documents.
        
        Args:
            query: Search query string
            top_k: Number of results to return
            
        Returns:
            List of SearchResult objects sorted by relevance
        """
        query_terms = self.tokenize(query)
        
        if not query_terms:
            return []
        
        # Find candidate documents (documents containing at least one query term)
        candidate_docs: Dict[int, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        for term in query_terms:
            if term in self.inverted_index:
                for doc_idx, freq in self.inverted_index[term]:
                    candidate_docs[doc_idx][term] = freq
        
        # Score candidates
        scored_docs = []
        for doc_idx, term_freqs in candidate_docs.items():
            score = self._bm25_score(query_terms, doc_idx, term_freqs)
            if score > 0:
                scored_docs.append((doc_idx, score))
        
        # Sort by score descending
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        # Build results
        results = []
        for doc_idx, score in scored_docs[:top_k]:
            doc = self.documents[doc_idx]
            results.append(SearchResult(
                document_id=doc.id,
                content=doc.content,
                source=doc.source,
                title=doc.title,
                score=score,
                chunk_index=doc.chunk_index
            ))
        
        return results
    
    def save(self, index_path: Path, embedding_path: Path) -> None:
        """Save the index to disk."""
        index_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save document metadata as JSON
        index_data = {
            'documents': [asdict(doc) for doc in self.documents],
            'k1': self.k1,
            'b': self.b
        }
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2)
        
        # Save index structures as pickle
        index_structures = {
            'doc_lengths': self.doc_lengths,
            'avg_doc_length': self.avg_doc_length,
            'inverted_index': dict(self.inverted_index),
            'doc_freqs': dict(self.doc_freqs),
            'vocab': self.vocab
        }
        with open(embedding_path, 'wb') as f:
            pickle.dump(index_structures, f)
        
        print(f"Index saved to {index_path} and {embedding_path}")
    
    def load(self, index_path: Path, embedding_path: Path) -> bool:
        """Load the index from disk."""
        if not index_path.exists() or not embedding_path.exists():
            return False
        
        # Load document metadata
        with open(index_path, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        self.documents = [Document(**doc) for doc in index_data['documents']]
        self.k1 = index_data['k1']
        self.b = index_data['b']
        
        # Load index structures
        with open(embedding_path, 'rb') as f:
            structures = pickle.load(f)
        
        self.doc_lengths = structures['doc_lengths']
        self.avg_doc_length = structures['avg_doc_length']
        self.inverted_index = defaultdict(list, structures['inverted_index'])
        self.doc_freqs = Counter(structures['doc_freqs'])
        self.vocab = structures['vocab']
        
        print(f"Index loaded: {len(self.documents)} documents, {len(self.vocab)} terms")
        return True


class RegulatorySearchEngine:
    """High-level search interface for regulatory queries."""
    
    def __init__(self):
        self.index = BM25Index()
        self._loaded = False
    
    def initialize(self, force_rebuild: bool = False) -> None:
        """Initialize or load the search index."""
        if not force_rebuild and INDEX_FILE.exists() and EMBEDDING_FILE.exists():
            if self.index.load(INDEX_FILE, EMBEDDING_FILE):
                self._loaded = True
                return
        
        # Build new index
        print("Building search index...")
        documents = load_all_documents()
        self.index.build_index(documents)
        self.index.save(INDEX_FILE, EMBEDDING_FILE)
        self._loaded = True
    
    def search(self, query: str, top_k: int = DEFAULT_TOP_K) -> List[SearchResult]:
        """Search for relevant regulatory information."""
        if not self._loaded:
            self.initialize()
        
        return self.index.search(query, top_k)
    
    def get_related_topics(self, query: str) -> List[str]:
        """Suggest related topics based on the query."""
        results = self.search(query, top_k=10)
        
        # Extract unique document titles
        titles = list(dict.fromkeys(r.title for r in results))
        return titles[:5]


def format_search_results(results: List[SearchResult], show_content: bool = True) -> str:
    """Format search results for display."""
    if not results:
        return "No results found."
    
    output = []
    for i, result in enumerate(results, 1):
        output.append(f"\n{'='*60}")
        output.append(f"Result {i} (Score: {result.score:.2f})")
        output.append(f"Source: {result.source}")
        output.append(f"Title: {result.title}")
        output.append(f"Chunk: {result.chunk_index + 1}")
        if show_content:
            output.append(f"\nContent:\n{result.content}")
    
    return "\n".join(output)


if __name__ == "__main__":
    # Test the search engine
    engine = RegulatorySearchEngine()
    engine.initialize(force_rebuild=True)
    
    test_queries = [
        "510(k) pathway for BCI",
        "Blackrock MoveAgain FDA",
        "Medicare reimbursement BCI",
        "predicate device cortical electrode"
    ]
    
    for query in test_queries:
        print(f"\n{'#'*60}")
        print(f"Query: {query}")
        results = engine.search(query, top_k=3)
        print(format_search_results(results, show_content=False))
