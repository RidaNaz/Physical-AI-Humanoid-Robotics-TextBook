"""
FastAPI application for RAG chatbot backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Import routers
from routers import chat, health

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="RAG Chatbot API",
    description="Backend API for Physical AI & Humanoid Robotics RAG Chatbot",
    version="1.0.0"
)

# Configure CORS - Allow all origins for Vercel serverless
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (needed for Vercel serverless)
    allow_credentials=False,  # Must be False when allow_origins is "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(health.router, prefix="/api", tags=["health"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "RAG Chatbot API",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
