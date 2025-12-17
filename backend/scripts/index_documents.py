"""
Main document indexing script for RAG system.
Processes all markdown files in docs/ directory and indexes them to Qdrant.
"""

import os
import re
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import uuid

# Import local modules
from lib.chunker import DocumentChunker
from lib.embeddings import EmbeddingGenerator

# Load environment variables
load_dotenv()

class DocumentIndexer:
    """Handles document indexing to Qdrant vector database."""

    def __init__(self):
        """Initialize indexer with Qdrant and Gemini clients."""
        # Qdrant client
        qdrant_url = os.getenv('QDRANT_URL')
        qdrant_api_key = os.getenv('QDRANT_API_KEY')

        if not qdrant_url or not qdrant_api_key:
            raise ValueError("QDRANT_URL and QDRANT_API_KEY must be set in environment variables")

        self.qdrant_client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key,
        )

        self.collection_name = "docs"
        self.embedding_dimension = 768

        # Initialize chunker and embedding generator
        self.chunker = DocumentChunker(target_chunk_size=500, overlap_size=50)
        self.embedder = EmbeddingGenerator()

    def create_collection(self):
        """Create or recreate Qdrant collection."""
        # Check if collection exists
        collections = self.qdrant_client.get_collections().collections
        collection_names = [c.name for c in collections]

        if self.collection_name in collection_names:
            print(f"Collection '{self.collection_name}' already exists. Deleting...")
            self.qdrant_client.delete_collection(self.collection_name)

        # Create new collection
        print(f"Creating collection '{self.collection_name}'...")
        self.qdrant_client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.embedding_dimension,
                distance=Distance.COSINE
            )
        )
        print(f"SUCCESS: Collection '{self.collection_name}' created successfully")

    def parse_frontmatter(self, content: str) -> Dict[str, str]:
        """
        Parse YAML frontmatter from markdown content.

        Args:
            content: Markdown content with frontmatter

        Returns:
            Dictionary of frontmatter key-value pairs
        """
        frontmatter = {}
        frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)

        if frontmatter_match:
            frontmatter_text = frontmatter_match.group(1)
            for line in frontmatter_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip()

        return frontmatter

    def extract_metadata(self, file_path: Path, content: str) -> Dict[str, str]:
        """
        Extract metadata from file path and content.

        Args:
            file_path: Path to markdown file
            content: File content

        Returns:
            Metadata dictionary
        """
        frontmatter = self.parse_frontmatter(content)

        # Remove frontmatter from content
        content_without_fm = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)

        # Extract title from first heading or filename
        title_match = re.search(r'^# (.+)$', content_without_fm, re.MULTILINE)
        title = title_match.group(1) if title_match else file_path.stem.replace('-', ' ').title()

        # Determine module and chapter from path
        parts = file_path.parts
        module = ""
        chapter = ""

        for part in parts:
            if part.startswith('module-'):
                module = part.replace('module-', 'Module ')
            if 'chapter' in part.lower():
                chapter_match = re.search(r'chapter(\d+)', part, re.IGNORECASE)
                if chapter_match:
                    chapter = f"Chapter {chapter_match.group(1)}"

        # Special cases for intro, hardware-architecture, appendices
        if file_path.stem == 'intro':
            title = "Introduction"
        elif file_path.stem == 'hardware-architecture':
            title = "Hardware Architecture"
        elif file_path.stem == 'appendices':
            title = "Appendices"

        # Calculate relative path from docs directory
        # Find the docs directory in the path
        docs_parent = None
        for parent in file_path.parents:
            if parent.name == 'docs':
                docs_parent = parent
                break

        if docs_parent:
            relative_file = file_path.relative_to(docs_parent)
        else:
            # Fallback: just use the filename
            relative_file = file_path.name

        return {
            'file': str(relative_file).replace('\\', '/'),
            'title': title,
            'module': module if module else 'General',
            'chapter': chapter if chapter else title,
            'sidebar_position': frontmatter.get('sidebar_position', ''),
        }

    def index_documents(self, docs_dir: str = '../../docs'):
        """
        Index all markdown files in docs directory.

        Args:
            docs_dir: Path to docs directory (relative to backend/scripts/)
        """
        # Get absolute path relative to this script's location
        script_dir = Path(__file__).parent
        docs_path = (script_dir / docs_dir).resolve()
        if not docs_path.exists():
            raise FileNotFoundError(f"Docs directory not found: {docs_dir}")

        # Find all markdown files
        md_files = list(docs_path.glob('**/*.md'))
        print(f"\nFound {len(md_files)} markdown files to index")

        all_chunks = []
        all_texts = []

        # Process each file
        for idx, file_path in enumerate(md_files, 1):
            print(f"\n[{idx}/{len(md_files)}] Processing: {file_path.relative_to(docs_path)}")

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Remove frontmatter from content for chunking
            content_clean = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)

            # Extract metadata
            metadata = self.extract_metadata(file_path, content)

            # Chunk document
            chunks = self.chunker.chunk_document(content_clean, metadata)

            # Extract code blocks for metadata
            code_languages = self.chunker.extract_code_blocks(content_clean)
            for chunk in chunks:
                chunk['metadata']['code_blocks'] = code_languages

            print(f"  → Created {len(chunks)} chunks")

            # Store chunks and texts for batch embedding
            all_chunks.extend(chunks)
            all_texts.extend([chunk['content'] for chunk in chunks])

        print(f"\nSUCCESS: Processed {len(md_files)} files into {len(all_chunks)} chunks")

        # Generate embeddings in batch
        print("\nGenerating embeddings...")
        embeddings = self.embedder.generate_batch_embeddings(all_texts, batch_size=50, delay_between_batches=0.5)

        # Upload to Qdrant in batches
        print("\nUploading to Qdrant...")
        batch_size = 100
        total_batches = (len(all_chunks) + batch_size - 1) // batch_size

        for i in range(0, len(all_chunks), batch_size):
            batch_chunks = all_chunks[i:i + batch_size]
            batch_embeddings = embeddings[i:i + batch_size]
            batch_num = i // batch_size + 1

            points = []
            for chunk, embedding in zip(batch_chunks, batch_embeddings):
                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={
                        'content': chunk['content'],
                        'file': chunk['metadata']['file'],
                        'title': chunk['metadata']['title'],
                        'module': chunk['metadata']['module'],
                        'chapter': chunk['metadata']['chapter'],
                        'section': chunk['metadata'].get('section', ''),
                        'chunk_index': chunk['metadata']['chunk_index'],
                        'total_chunks': chunk['metadata']['total_chunks'],
                        'code_blocks': chunk['metadata'].get('code_blocks', []),
                    }
                )
                points.append(point)

            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=points
            )

            print(f"  Batch {batch_num}/{total_batches}: Uploaded {len(points)} points")

        print(f"\nSUCCESS: Successfully indexed {len(all_chunks)} chunks to Qdrant!")

        # Verify collection
        collection_info = self.qdrant_client.get_collection(self.collection_name)
        print(f"\nCollection info:")
        print(f"  Name: {collection_info.config.params.vectors.size}")
        print(f"  Points count: {collection_info.points_count}")
        print(f"  Vector dimension: {collection_info.config.params.vectors.size}")


def main():
    """Main entry point."""
    print("=" * 60)
    print("Document Indexing Script for RAG Chatbot")
    print("=" * 60)

    try:
        indexer = DocumentIndexer()

        # Create collection
        indexer.create_collection()

        # Index documents
        indexer.index_documents()

        print("\n" + "=" * 60)
        print("SUCCESS: Indexing completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\nERROR: Error during indexing: {e}")
        raise


if __name__ == "__main__":
    main()
