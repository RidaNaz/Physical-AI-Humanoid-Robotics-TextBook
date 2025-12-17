"""
Content chunking logic for RAG document processing.
Splits markdown documents into semantic chunks while preserving context.
"""

import re
from typing import List, Dict

class DocumentChunker:
    """Handles semantic chunking of markdown documents."""

    def __init__(self, target_chunk_size: int = 500, overlap_size: int = 50):
        """
        Initialize chunker with size parameters.

        Args:
            target_chunk_size: Target tokens per chunk (default: 500)
            overlap_size: Token overlap between chunks (default: 50)
        """
        self.target_chunk_size = target_chunk_size
        self.overlap_size = overlap_size

    def chunk_document(self, content: str, metadata: Dict[str, str]) -> List[Dict[str, any]]:
        """
        Split a markdown document into semantic chunks.

        Args:
            content: Markdown content to chunk
            metadata: Document metadata (file, title, module, chapter)

        Returns:
            List of chunk dictionaries with content and metadata
        """
        chunks = []

        # Split by ## headers (h2)
        sections = re.split(r'(?=^## )', content, flags=re.MULTILINE)
        sections = [s.strip() for s in sections if s.strip()]

        for section in sections:
            # Extract section header
            header_match = re.match(r'^## (.+)$', section, re.MULTILINE)
            section_title = header_match.group(1) if header_match else ""

            # Split section into chunks
            section_chunks = self._chunk_section(section, section_title)

            for idx, chunk_content in enumerate(section_chunks):
                chunk = {
                    'content': chunk_content.strip(),
                    'metadata': {
                        **metadata,
                        'section': section_title,
                        'chunk_index': len(chunks),
                        'total_chunks': 0  # Will be updated after processing all chunks
                    }
                }
                chunks.append(chunk)

        # Update total_chunks count
        total = len(chunks)
        for chunk in chunks:
            chunk['metadata']['total_chunks'] = total

        return chunks

    def _chunk_section(self, section: str, header: str) -> List[str]:
        """
        Chunk a section into smaller pieces.

        Args:
            section: Section content
            header: Section header

        Returns:
            List of chunk strings
        """
        chunks = []

        # Split by paragraphs (double newline)
        paragraphs = re.split(r'\n\n+', section)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        current_chunk = ""

        for para in paragraphs:
            # Preserve code blocks intact
            if para.strip().startswith('```'):
                # If adding code block would exceed limit, save current chunk
                if current_chunk and self._estimate_tokens(current_chunk + '\n\n' + para) > self.target_chunk_size * 1.5:
                    chunks.append(current_chunk)
                    # Start new chunk with overlap (last paragraph)
                    current_chunk = para
                else:
                    current_chunk += ('\n\n' if current_chunk else '') + para
            else:
                # Regular paragraph
                if self._estimate_tokens(current_chunk + '\n\n' + para) > self.target_chunk_size:
                    if current_chunk:
                        chunks.append(current_chunk)
                        # Add overlap from previous chunk
                        current_chunk = self._get_overlap(current_chunk) + '\n\n' + para
                    else:
                        current_chunk = para
                else:
                    current_chunk += ('\n\n' if current_chunk else '') + para

        # Add remaining content
        if current_chunk.strip():
            chunks.append(current_chunk)

        return chunks if chunks else [section]  # Return original if no chunks created

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count (rough approximation).

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        # Rough estimate: ~4 characters per token
        return len(text) // 4

    def _get_overlap(self, chunk: str) -> str:
        """
        Get overlap text from end of chunk.

        Args:
            chunk: Chunk to extract overlap from

        Returns:
            Overlap text
        """
        # Get last N tokens for overlap
        words = chunk.split()
        overlap_words = words[-self.overlap_size:] if len(words) > self.overlap_size else words
        return ' '.join(overlap_words)

    def extract_code_blocks(self, content: str) -> List[str]:
        """
        Extract programming languages from code blocks.

        Args:
            content: Markdown content

        Returns:
            List of programming languages found
        """
        code_block_pattern = r'```(\w+)?'
        matches = re.findall(code_block_pattern, content)
        return [lang for lang in matches if lang]  # Filter out empty matches
