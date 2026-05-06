"""
Search Engine - Semantic search with sentence-transformers and ChromaDB
GPU-accelerated embeddings for fast similarity search
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Lazy imports for heavy ML libraries
_embedding_model = None
_chroma_client = None


def _get_embedding_model():
    """Lazy load sentence-transformers model (all-MiniLM-L6-v2) with GPU support."""
    global _embedding_model
    if _embedding_model is None:
        import torch
        from sentence_transformers import SentenceTransformer

        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Loading embedding model on device: {device}")

        _embedding_model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2",
            device=device,
        )
    return _embedding_model


def _get_chroma_client(host: str = "localhost", port: int = 8000, token: str | None = None):
    """Get or create ChromaDB client."""
    global _chroma_client
    if _chroma_client is None:
        import chromadb
        from chromadb.config import Settings
        
        settings = Settings(
            chroma_client_auth_provider="chromadb.auth.token.TokenAuthClientProvider",
            chroma_client_auth_credentials=token,
            anonymized_telemetry=False,
        )
        
        try:
            _chroma_client = chromadb.HttpClient(
                host=host,
                port=port,
                settings=settings if token else None,
            )
            logger.info(f"Connected to ChromaDB at {host}:{port}")
        except Exception as e:
            logger.warning(f"ChromaDB connection failed, using in-memory: {e}")
            _chroma_client = chromadb.Client()
    
    return _chroma_client


@dataclass
class SearchResult:
    """A single search result."""
    id: str
    content: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)
    highlight: str | None = None


@dataclass
class SearchResponse:
    """Response from a search query."""
    query: str
    results: list[SearchResult]
    total_results: int
    search_time_ms: float
    embedding_time_ms: float


@dataclass
class IndexStats:
    """Statistics about a search index."""
    name: str
    document_count: int
    embedding_dimension: int
    metadata_fields: list[str]


class SearchEngine:
    """
    Semantic search engine using sentence-transformers and ChromaDB.
    Supports full-text search with vector similarity.
    """

    def __init__(
        self,
        collection_name: str = "dataset_embeddings",
        chromadb_host: str = "localhost",
        chromadb_port: int = 8000,
        chromadb_token: str | None = None,
        embedding_batch_size: int = 64,
    ):
        """
        Initialize the search engine (spec: collection "dataset_embeddings",
        all-MiniLM-L6-v2, one document per dataset).
        """
        self.collection_name = collection_name
        self.chromadb_host = chromadb_host
        self.chromadb_port = chromadb_port
        self.chromadb_token = chromadb_token
        self.embedding_batch_size = embedding_batch_size
        self._collection = None

    def _get_collection(self):
        """Get or create the ChromaDB collection."""
        if self._collection is None:
            client = _get_chroma_client(
                self.chromadb_host,
                self.chromadb_port,
                self.chromadb_token,
            )
            self._collection = client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    async def index_dataset(
        self,
        dataset_id: int,
        text: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Index a single dataset per spec: one document per dataset with id=dataset_id.
        Caller builds text from name + description + column names + tag values.
        """
        import time
        if not text.strip():
            logger.warning(f"Empty text for dataset {dataset_id}, skipping index")
            return
        collection = self._get_collection()
        model = _get_embedding_model()
        doc_id = str(dataset_id)
        meta = metadata or {}
        meta["dataset_id"] = dataset_id
        start = time.time()
        embedding = model.encode(
            text,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        # ChromaDB expects list of lists for embeddings
        collection.upsert(
            ids=[doc_id],
            embeddings=[embedding.tolist()],
            documents=[text],
            metadatas=[{k: v for k, v in meta.items() if isinstance(v, (str, int, float, bool))}],
        )
        logger.info(f"Indexed dataset {dataset_id} in {(time.time()-start)*1000:.0f}ms")

    async def index_dataframe(
        self,
        data: pd.DataFrame,
        text_columns: list[str] | None = None,
        id_column: str | None = None,
        metadata_columns: list[str] | None = None,
    ) -> int:
        """
        Index a DataFrame for semantic search.

        Args:
            data: DataFrame to index
            text_columns: Columns to combine for text content (default: all string columns)
            id_column: Column to use as document ID (default: row index)
            metadata_columns: Columns to store as metadata

        Returns:
            Number of documents indexed
        """
        import time
        
        logger.info(f"Indexing {len(data)} rows into collection '{self.collection_name}'")
        
        # Determine text columns
        if text_columns is None:
            text_columns = data.select_dtypes(include=["object", "string"]).columns.tolist()
        
        if not text_columns:
            raise ValueError("No text columns found for indexing")

        # Determine metadata columns
        if metadata_columns is None:
            metadata_columns = [c for c in data.columns if c not in text_columns]

        collection = self._get_collection()
        model = _get_embedding_model()

        # Prepare documents
        documents = []
        ids = []
        metadatas = []

        for idx, row in data.iterrows():
            # Combine text columns
            text_parts = [str(row[col]) for col in text_columns if pd.notna(row[col])]
            text = " | ".join(text_parts)
            
            if not text.strip():
                continue

            # Generate ID
            if id_column and id_column in row:
                doc_id = str(row[id_column])
            else:
                doc_id = hashlib.md5(f"{idx}:{text[:100]}".encode()).hexdigest()

            # Collect metadata
            meta = {"row_index": int(idx)}
            for col in metadata_columns:
                if col in row and pd.notna(row[col]):
                    val = row[col]
                    # ChromaDB only supports str, int, float, bool
                    if isinstance(val, (str, int, float, bool)):
                        meta[col] = val
                    else:
                        meta[col] = str(val)

            documents.append(text)
            ids.append(doc_id)
            metadatas.append(meta)

        if not documents:
            logger.warning("No documents to index")
            return 0

        # Generate embeddings in batches
        start_time = time.time()
        embeddings = []
        
        for i in range(0, len(documents), self.embedding_batch_size):
            batch = documents[i:i + self.embedding_batch_size]
            batch_embeddings = model.encode(
                batch,
                convert_to_numpy=True,
                show_progress_bar=False,
            )
            embeddings.extend(batch_embeddings.tolist())

        embedding_time = (time.time() - start_time) * 1000
        logger.info(f"Generated {len(embeddings)} embeddings in {embedding_time:.0f}ms")

        # Upsert to ChromaDB
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

        logger.info(f"Indexed {len(documents)} documents")
        return len(documents)

    async def search(
        self,
        query: str,
        top_k: int = 10,
        filter_metadata: dict[str, Any] | None = None,
        include_content: bool = True,
    ) -> SearchResponse:
        """
        Perform semantic search.

        Args:
            query: Search query text
            top_k: Number of results to return
            filter_metadata: Metadata filters (ChromaDB where clause)
            include_content: Whether to include full document content

        Returns:
            SearchResponse with ranked results
        """
        import time

        collection = self._get_collection()
        model = _get_embedding_model()

        # Generate query embedding
        embed_start = time.time()
        query_embedding = model.encode(
            query,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        embedding_time_ms = (time.time() - embed_start) * 1000

        # Search ChromaDB
        search_start = time.time()
        results = collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            where=filter_metadata,
            include=["documents", "metadatas", "distances"],
        )
        search_time_ms = (time.time() - search_start) * 1000

        # Process results
        search_results = []
        if results and results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                # Convert distance to similarity score (cosine distance to similarity)
                distance = results["distances"][0][i] if results["distances"] else 0
                score = 1 - distance  # For cosine distance

                content = results["documents"][0][i] if results["documents"] else ""
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}

                # Generate highlight snippet
                highlight = self._generate_highlight(content, query) if content else None

                search_results.append(SearchResult(
                    id=doc_id,
                    content=content if include_content else "",
                    score=round(score, 4),
                    metadata=metadata,
                    highlight=highlight,
                ))

        return SearchResponse(
            query=query,
            results=search_results,
            total_results=len(search_results),
            search_time_ms=round(search_time_ms, 2),
            embedding_time_ms=round(embedding_time_ms, 2),
        )

    async def search_similar(
        self,
        document_id: str,
        top_k: int = 10,
        exclude_self: bool = True,
    ) -> SearchResponse:
        """
        Find documents similar to a given document.

        Args:
            document_id: ID of the source document
            top_k: Number of similar documents to return
            exclude_self: Whether to exclude the source document

        Returns:
            SearchResponse with similar documents
        """
        import time

        collection = self._get_collection()

        # Get the document's embedding
        doc = collection.get(ids=[document_id], include=["embeddings", "documents"])
        
        if not doc["embeddings"] or not doc["embeddings"][0]:
            raise ValueError(f"Document {document_id} not found or has no embedding")

        embedding = doc["embeddings"][0]
        
        # Search for similar
        search_start = time.time()
        
        n_results = top_k + 1 if exclude_self else top_k
        results = collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )
        search_time_ms = (time.time() - search_start) * 1000

        # Process results
        search_results = []
        if results and results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                if exclude_self and doc_id == document_id:
                    continue
                if len(search_results) >= top_k:
                    break

                distance = results["distances"][0][i] if results["distances"] else 0
                score = 1 - distance

                search_results.append(SearchResult(
                    id=doc_id,
                    content=results["documents"][0][i] if results["documents"] else "",
                    score=round(score, 4),
                    metadata=results["metadatas"][0][i] if results["metadatas"] else {},
                ))

        return SearchResponse(
            query=f"similar_to:{document_id}",
            results=search_results,
            total_results=len(search_results),
            search_time_ms=round(search_time_ms, 2),
            embedding_time_ms=0,
        )

    async def delete_collection(self) -> bool:
        """Delete the entire collection."""
        try:
            client = _get_chroma_client(
                self.chromadb_host,
                self.chromadb_port,
                self.chromadb_token,
            )
            client.delete_collection(self.collection_name)
            self._collection = None
            logger.info(f"Deleted collection '{self.collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            return False

    async def get_stats(self) -> IndexStats:
        """Get statistics about the search index."""
        collection = self._get_collection()
        count = collection.count()
        
        # Get sample to determine metadata fields
        sample = collection.peek(limit=1)
        metadata_fields = []
        if sample["metadatas"] and sample["metadatas"][0]:
            metadata_fields = list(sample["metadatas"][0].keys())

        model = _get_embedding_model()
        embedding_dim = model.get_sentence_embedding_dimension()

        return IndexStats(
            name=self.collection_name,
            document_count=count,
            embedding_dimension=embedding_dim,
            metadata_fields=metadata_fields,
        )

    def _generate_highlight(self, content: str, query: str, max_length: int = 200) -> str:
        """Generate a highlighted snippet from content."""
        query_terms = query.lower().split()
        content_lower = content.lower()
        
        # Find best starting position
        best_pos = 0
        best_score = 0
        
        words = content.split()
        for i in range(len(words)):
            window = " ".join(words[i:i+20]).lower()
            score = sum(1 for term in query_terms if term in window)
            if score > best_score:
                best_score = score
                best_pos = i

        # Extract snippet
        start = max(0, best_pos - 5)
        snippet_words = words[start:start + 30]
        snippet = " ".join(snippet_words)
        
        if len(snippet) > max_length:
            snippet = snippet[:max_length] + "..."
        
        if start > 0:
            snippet = "..." + snippet
        
        return snippet

    async def hybrid_search(
        self,
        query: str,
        text_weight: float = 0.5,
        semantic_weight: float = 0.5,
        top_k: int = 10,
    ) -> SearchResponse:
        """
        Perform hybrid search combining keyword and semantic matching.

        Args:
            query: Search query
            text_weight: Weight for keyword matching (0-1)
            semantic_weight: Weight for semantic matching (0-1)
            top_k: Number of results

        Returns:
            SearchResponse with combined ranking
        """
        # Get semantic results
        semantic_response = await self.search(query, top_k=top_k * 2)
        
        # Re-rank with hybrid scoring
        query_terms = set(query.lower().split())
        
        for result in semantic_response.results:
            content_terms = set(result.content.lower().split())
            keyword_overlap = len(query_terms & content_terms) / len(query_terms) if query_terms else 0
            
            # Combine scores
            result.score = (
                result.score * semantic_weight +
                keyword_overlap * text_weight
            )
        
        # Sort by combined score
        semantic_response.results.sort(key=lambda r: r.score, reverse=True)
        semantic_response.results = semantic_response.results[:top_k]
        semantic_response.total_results = len(semantic_response.results)
        
        return semantic_response
