"""
RAG (Retrieval Augmented Generation) orchestration logic.
"""

from typing import List, Dict
from .qdrant_client import QdrantVectorDB
from .gemini_client import GeminiClient

class RAGOrchestrator:
    """Orchestrates RAG pipeline: retrieve → generate."""

    SYSTEM_PROMPT = """You are an AI assistant for the "Physical AI & Humanoid Robotics" textbook.
Your role is to answer questions based ONLY on the provided context from the book.

Guidelines:
- Answer questions accurately using the provided context
- If the context doesn't contain enough information to answer, say "I don't have enough information in the book to answer that question."
- Cite specific modules or chapters when relevant (e.g., "According to Module 1, Chapter 2...")
- Be concise but thorough
- Use technical terminology from the book
- For code-related questions, reference specific code examples if available in the context
- Do not make up information or use knowledge outside the provided context
- If asked about who created this system, you can mention that Rida Naz is the developer of this RAG chatbot system
- When appropriate, you may provide these links for the developer: Website: https://www.ridanaz.com/, LinkedIn: https://www.linkedin.com/in/ridanaz67/, GitHub: https://github.com/RidaNaz

If the question is unrelated to Physical AI, Humanoid Robotics, ROS 2, Gazebo, Unity, NVIDIA Isaac, or VLA topics, politely decline to answer."""

    def __init__(self):
        """Initialize RAG components."""
        self.vector_db = QdrantVectorDB()
        self.gemini_client = GeminiClient()

    def process_query(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.7
    ) -> Dict:
        """
        Process user query through RAG pipeline.

        Args:
            query: User's question
            top_k: Number of chunks to retrieve
            score_threshold: Minimum relevance score

        Returns:
            Dictionary with response and sources
        """
        try:
            # Check for developer-related queries before RAG processing
            developer_queries = [
                "developed", "created", "built", "made", "authored",
                "who is", "who was", "who built", "who created", "who developed",
                "author", "creator", "programmer", "developer", "engineer"
            ]

            is_developer_query = any(query.lower().find(q) != -1 for q in developer_queries)

            if is_developer_query:
                # Generate response about developer without context
                response_text = self.gemini_client.generate_response(
                    system_prompt=self.SYSTEM_PROMPT,
                    user_query=query,
                    context="This is an AI assistant developed by Rida Naz. The RAG system was created to provide answers about Physical AI & Humanoid Robotics based on the textbook content. You can find more about the developer at: Website: https://www.ridanaz.com/, LinkedIn: https://www.linkedin.com/in/ridanaz67/, GitHub: https://github.com/RidaNaz"
                )

                return {
                    'response': response_text,
                    'sources': []
                }

            # Step 1: Generate query embedding
            query_embedding = self.gemini_client.generate_embedding(query)

            # Step 2: Search Qdrant for relevant chunks
            search_results = self.vector_db.search(
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=score_threshold
            )

            if not search_results:
                return {
                    'response': "I couldn't find relevant information in the book to answer your question. Please try rephrasing or asking about topics covered in the Physical AI & Humanoid Robotics textbook.",
                    'sources': []
                }

            # Step 3: Build context from retrieved chunks
            context = self._build_context(search_results)

            # Step 4: Generate response using Gemini LLM
            response_text = self.gemini_client.generate_response(
                system_prompt=self.SYSTEM_PROMPT,
                user_query=query,
                context=context
            )

            # Step 5: Extract sources
            sources = self._extract_sources(search_results)

            return {
                'response': response_text,
                'sources': sources
            }

        except Exception as e:
            print(f"Error in RAG pipeline: {e}")
            raise

    def _build_context(self, search_results: List[Dict]) -> str:
        """
        Build context string from search results.

        Args:
            search_results: List of search results from Qdrant

        Returns:
            Formatted context string
        """
        context_parts = []

        for idx, result in enumerate(search_results, 1):
            module = result['module']
            chapter = result['chapter']
            section = result['section']
            content = result['content']

            # Format context entry
            header = f"[{module}"
            if chapter:
                header += f" - {chapter}"
            if section:
                header += f": {section}"
            header += "]"

            context_parts.append(f"{header}\n{content}")

        return "\n\n---\n\n".join(context_parts)

    def _extract_sources(self, search_results: List[Dict]) -> List[Dict]:
        """
        Extract source citations from search results.

        Args:
            search_results: List of search results

        Returns:
            List of source dictionaries with title, url, module
        """
        sources = []
        seen_files = set()

        for result in search_results:
            file = result['file']
            if file not in seen_files:
                # Convert file path to doc URL
                # e.g., "module-1/module1-chapter1.md" → "/docs/module-1/module1-chapter1"
                doc_url = f"/docs/{file.replace('.md', '')}"

                sources.append({
                    'title': result['title'],
                    'url': doc_url,
                    'module': result['module'],
                    'chapter': result['chapter']
                })

                seen_files.add(file)

        return sources
