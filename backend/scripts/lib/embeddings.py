"""
Gemini embedding generation wrapper.
Handles batch embedding generation for document chunks.
"""

import os
import time
from typing import List, Dict
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EmbeddingGenerator:
    """Handles embedding generation using Google Gemini API."""

    def __init__(self, api_key: str = None, model: str = "models/text-embedding-004"):
        """
        Initialize embedding generator.

        Args:
            api_key: Gemini API key (defaults to env var GEMINI_API_KEY)
            model: Embedding model to use (default: text-embedding-004)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        genai.configure(api_key=self.api_key)
        self.model = model
        self.embedding_dimension = 768  # text-embedding-004 dimension

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (768 dimensions)
        """
        try:
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_document"  # Optimized for document retrieval
            )
            return result['embedding']
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise

    def generate_batch_embeddings(
        self,
        texts: List[str],
        batch_size: int = 100,
        delay_between_batches: float = 1.0
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.

        Args:
            texts: List of texts to embed
            batch_size: Number of texts per batch (max 100 for Gemini)
            delay_between_batches: Delay in seconds between batches

        Returns:
            List of embedding vectors
        """
        embeddings = []
        total_batches = (len(texts) + batch_size - 1) // batch_size

        print(f"Generating embeddings for {len(texts)} texts in {total_batches} batches...")

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_num = i // batch_size + 1

            print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} texts)...")

            try:
                # Generate embeddings for batch
                for text in batch:
                    embedding = self.generate_embedding(text)
                    embeddings.append(embedding)

                # Delay between batches to avoid rate limiting
                if i + batch_size < len(texts):
                    time.sleep(delay_between_batches)

            except Exception as e:
                print(f"Error in batch {batch_num}: {e}")
                raise

        print(f"✓ Generated {len(embeddings)} embeddings successfully")
        return embeddings

    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a search query.

        Args:
            query: Search query text

        Returns:
            Embedding vector (768 dimensions)
        """
        try:
            result = genai.embed_content(
                model=self.model,
                content=query,
                task_type="retrieval_query"  # Optimized for query retrieval
            )
            return result['embedding']
        except Exception as e:
            print(f"Error generating query embedding: {e}")
            raise
