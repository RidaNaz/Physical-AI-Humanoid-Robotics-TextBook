"""
Google Gemini API client for LLM and embeddings.
"""

import os
from typing import List
import google.generativeai as genai

class GeminiClient:
    """Handles Gemini API operations."""

    def __init__(self):
        """Initialize Gemini client."""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY must be set")

        genai.configure(api_key=api_key)
        self.embedding_model = "models/text-embedding-004"
        self.llm_model = "gemini-1.5-pro-latest"

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (768 dimensions)
        """
        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_query"
            )
            return result['embedding']
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise

    def generate_response(
        self,
        system_prompt: str,
        user_query: str,
        context: str,
        max_tokens: int = 500,
        temperature: float = 0.3
    ) -> str:
        """
        Generate response using Gemini LLM.

        Args:
            system_prompt: System instructions
            user_query: User's question
            context: Retrieved context from RAG
            max_tokens: Maximum output tokens
            temperature: Sampling temperature (0-1)

        Returns:
            Generated response text
        """
        try:
            # Combine system prompt, context, and query
            full_prompt = f"{system_prompt}\n\nContext:\n{context}\n\nQuestion: {user_query}\n\nAnswer:"

            model = genai.GenerativeModel(self.llm_model)
            response = model.generate_content(
                full_prompt,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                )
            )

            return response.text

        except Exception as e:
            print(f"Error generating response: {e}")
            raise

    def health_check(self) -> bool:
        """
        Check if Gemini API is accessible.

        Returns:
            True if healthy, False otherwise
        """
        try:
            # Try a simple embedding call
            result = genai.embed_content(
                model=self.embedding_model,
                content="test",
                task_type="retrieval_query"
            )
            return len(result['embedding']) == 768
        except Exception as e:
            print(f"Gemini health check failed: {e}")
            return False
