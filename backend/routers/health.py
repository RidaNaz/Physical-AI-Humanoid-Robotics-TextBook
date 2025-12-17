"""
Health check endpoint for RAG chatbot API.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import time

# Import clients
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.qdrant_client import QdrantVectorDB
from lib.gemini_client import GeminiClient

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    qdrant: bool
    gemini: bool
    timestamp: int


@router.options("/health")
async def health_options():
    """Handle CORS preflight for health endpoint."""
    return {"status": "ok"}


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check API health status.

    Verifies connectivity to:
    - Qdrant vector database
    - Google Gemini API

    Returns status: 'healthy', 'degraded', or 'down'
    """
    try:
        # Check Qdrant
        qdrant_healthy = False
        try:
            vector_db = QdrantVectorDB()
            qdrant_healthy = vector_db.health_check()
        except Exception as e:
            print(f"Qdrant health check error: {e}")

        # Check Gemini
        gemini_healthy = False
        try:
            gemini = GeminiClient()
            gemini_healthy = gemini.health_check()
        except Exception as e:
            print(f"Gemini health check error: {e}")

        # Determine overall status
        if qdrant_healthy and gemini_healthy:
            status = 'healthy'
        elif qdrant_healthy or gemini_healthy:
            status = 'degraded'
        else:
            status = 'down'

        return HealthResponse(
            status=status,
            qdrant=qdrant_healthy,
            gemini=gemini_healthy,
            timestamp=int(time.time())
        )

    except Exception as e:
        print(f"Error in health endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error": str(e)
            }
        )
