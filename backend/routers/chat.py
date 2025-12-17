"""
Chat endpoint for RAG chatbot.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Dict
import time
from collections import defaultdict

# Import RAG components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.rag import RAGOrchestrator
from lib.utils import validate_query, RateLimiter

router = APIRouter()

# Initialize rate limiter (10 requests per minute)
rate_limiter = RateLimiter(max_requests=10, window_seconds=60)


# Pydantic models
class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="User's question")


class Source(BaseModel):
    title: str
    url: str
    module: str
    chapter: str = ""


class ChatResponse(BaseModel):
    response: str
    sources: List[Source]


class ErrorResponse(BaseModel):
    error: str
    code: str


@router.post("/chat", response_model=ChatResponse, responses={
    400: {"model": ErrorResponse},
    429: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def chat(request: ChatRequest, req: Request):
    """
    Process a chat query using RAG pipeline.

    - **query**: User's question (max 500 characters)

    Returns the AI-generated response with source citations.
    """
    try:
        # Get client IP for rate limiting
        client_ip = req.client.host

        # Check rate limit
        if not rate_limiter.is_allowed(client_ip):
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Too many requests. Please try again later.",
                    "code": "RATE_LIMIT"
                }
            )

        # Validate query
        validation = validate_query(request.query)
        if not validation['valid']:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": validation['error'],
                    "code": "INVALID_QUERY"
                }
            )

        # Process query through RAG
        rag = RAGOrchestrator()
        result = rag.process_query(request.query)

        # Format sources
        sources = [
            Source(
                title=s['title'],
                url=s['url'],
                module=s['module'],
                chapter=s.get('chapter', '')
            )
            for s in result['sources']
        ]

        return ChatResponse(
            response=result['response'],
            sources=sources
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error. Please try again.",
                "code": "API_ERROR"
            }
        )
