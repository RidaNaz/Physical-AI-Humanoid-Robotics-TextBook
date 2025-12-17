"""
Qdrant client initialization and vector search.
"""

import os
from typing import List, Dict
from qdrant_client import QdrantClient
from qdrant_client.models import ScoredPoint

class QdrantVectorDB:
    """Handles Qdrant vector database operations."""

    def __init__(self):
        """Initialize Qdrant client."""
        qdrant_url = os.getenv('QDRANT_URL')
        qdrant_api_key = os.getenv('QDRANT_API_KEY')

        if not qdrant_url or not qdrant_api_key:
            raise ValueError("QDRANT_URL and QDRANT_API_KEY must be set")

        self.client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key,
        )
        self.collection_name = "docs"

    def search(
        self,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: float = 0.7
    ) -> List[Dict]:
        """
        Search for similar vectors in Qdrant.

        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results
            score_threshold: Minimum similarity score

        Returns:
            List of search results with content and metadata
        """
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold
            )

            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'content': result.payload.get('content', ''),
                    'file': result.payload.get('file', ''),
                    'title': result.payload.get('title', ''),
                    'module': result.payload.get('module', ''),
                    'chapter': result.payload.get('chapter', ''),
                    'section': result.payload.get('section', ''),
                    'score': result.score
                })

            return formatted_results

        except Exception as e:
            print(f"Error searching Qdrant: {e}")
            raise

    def health_check(self) -> bool:
        """
        Check if Qdrant is accessible.

        Returns:
            True if healthy, False otherwise
        """
        try:
            collections = self.client.get_collections()
            return any(c.name == self.collection_name for c in collections.collections)
        except Exception as e:
            print(f"Qdrant health check failed: {e}")
            return False
