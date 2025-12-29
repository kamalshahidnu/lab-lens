#!/usr/bin/env python3
"""
Vector Database Wrapper for RAG System
Provides persistent storage for document embeddings using ChromaDB
"""

import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.utils.error_handling import ErrorHandler, safe_execute
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

try:
    import chromadb
    from chromadb.config import Settings

    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("chromadb not available. Install with: pip install chromadb. " "Falling back to in-memory storage.")


class VectorDatabase:
    """
    Vector database wrapper for persistent document storage
    Uses ChromaDB for embedding storage and retrieval
    """

    def __init__(
        self, persist_directory: str = "models/vector_db", collection_name: str = "documents", embedding_function=None
    ):
        """
        Initialize vector database

        Args:
          persist_directory: Directory to persist ChromaDB data
          collection_name: Name of the collection to use
          embedding_function: Optional embedding function (if None, uses ChromaDB's default)
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError("chromadb is required. Install with: pip install chromadb")

        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        self.collection_name = collection_name
        self.embedding_function = embedding_function

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory), settings=Settings(anonymized_telemetry=False, allow_reset=True)
        )

        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name, embedding_function=embedding_function)
            logger.info(f"Loaded existing collection: {collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                embedding_function=embedding_function,
                metadata={"created_at": datetime.now().isoformat()},
            )
            logger.info(f"Created new collection: {collection_name}")

    @safe_execute("add_documents", logger, ErrorHandler(logger))
    def add_documents(
        self, texts: List[str], embeddings: List[List[float]], metadatas: List[Dict[str, Any]], ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add documents to the vector database

        Args:
          texts: List of text chunks
          embeddings: List of embedding vectors
          metadatas: List of metadata dictionaries
          ids: Optional list of document IDs (auto-generated if None)

        Returns:
          List of document IDs
        """
        if not texts or not embeddings:
            raise ValueError("texts and embeddings cannot be empty")

        if len(texts) != len(embeddings) or len(texts) != len(metadatas):
            raise ValueError("texts, embeddings, and metadatas must have the same length")

        # Generate IDs if not provided
        if ids is None:
            ids = []
            for i, (text, metadata) in enumerate(zip(texts, metadatas)):
                # Create unique ID from text and metadata
                id_str = f"{metadata.get('document_name', 'doc')}_{i}_{hashlib.md5(text.encode()).hexdigest()[:8]}"
                ids.append(id_str)

        # Add to collection
        self.collection.add(embeddings=embeddings, documents=texts, metadatas=metadatas, ids=ids)

        logger.info(f"Added {len(texts)} documents to collection '{self.collection_name}'")
        return ids

    @safe_execute("query", logger, ErrorHandler(logger))
    def query(
        self,
        query_embeddings: List[List[float]],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        min_score: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Query the vector database

        Args:
          query_embeddings: Query embedding(s) as list of lists
          n_results: Number of results to return
          where: Optional metadata filter
          min_score: Minimum similarity score threshold

        Returns:
          Dictionary with 'ids', 'documents', 'metadatas', 'distances'
        """
        results = self.collection.query(query_embeddings=query_embeddings, n_results=n_results, where=where)

        # Filter by minimum score (ChromaDB uses distances, so we need to convert)
        # For cosine similarity: score = 1 - distance (for normalized embeddings)
        if results["distances"] and len(results["distances"]) > 0:
            filtered_results = {"ids": [], "documents": [], "metadatas": [], "distances": []}

            for i, distance_list in enumerate(results["distances"]):
                filtered_ids = []
                filtered_docs = []
                filtered_metas = []
                filtered_dists = []

                for j, distance in enumerate(distance_list):
                    # Convert distance to similarity score (assuming cosine similarity)
                    score = 1.0 - distance
                    if score >= min_score:
                        filtered_ids.append(results["ids"][i][j])
                        filtered_docs.append(results["documents"][i][j])
                        filtered_metas.append(results["metadatas"][i][j])
                        filtered_dists.append(distance)

                filtered_results["ids"].append(filtered_ids)
                filtered_results["documents"].append(filtered_docs)
                filtered_results["metadatas"].append(filtered_metas)
                filtered_results["distances"].append(filtered_dists)

            return filtered_results

        return results

    @safe_execute("delete", logger, ErrorHandler(logger))
    def delete(self, ids: Optional[List[str]] = None, where: Optional[Dict[str, Any]] = None):
        """
        Delete documents from the collection

        Args:
          ids: Optional list of document IDs to delete
          where: Optional metadata filter for deletion
        """
        if ids is None and where is None:
            raise ValueError("Either ids or where must be provided")

        self.collection.delete(ids=ids, where=where)
        logger.info(f"Deleted documents from collection '{self.collection_name}'")

    @safe_execute("get_collection_info", logger, ErrorHandler(logger))
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection

        Returns:
          Dictionary with collection statistics
        """
        count = self.collection.count()
        return {"name": self.collection_name, "count": count, "persist_directory": str(self.persist_directory)}

    @safe_execute("reset_collection", logger, ErrorHandler(logger))
    def reset_collection(self):
        """Reset/clear the entire collection"""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function,
            metadata={"created_at": datetime.now().isoformat()},
        )
        logger.info(f"Reset collection '{self.collection_name}'")

    def create_user_collection(self, user_id: str) -> "VectorDatabase":
        """
        Create a new collection for a specific user

        Args:
          user_id: Unique user identifier

        Returns:
          New VectorDatabase instance for the user
        """
        collection_name = f"{self.collection_name}_{user_id}"
        return VectorDatabase(
            persist_directory=str(self.persist_directory),
            collection_name=collection_name,
            embedding_function=self.embedding_function,
        )


