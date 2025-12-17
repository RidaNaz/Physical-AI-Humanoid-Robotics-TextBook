"""
Health check endpoint for RAG chatbot API.
Verifies Qdrant and Gemini connectivity.
"""

import json
from http.server import BaseHTTPRequestHandler
from dotenv import load_dotenv
from lib.qdrant_client import QdrantVectorDB
from lib.gemini_client import GeminiClient

# Load environment variables
load_dotenv()


class handler(BaseHTTPRequestHandler):
    """Serverless function handler for Vercel."""

    def do_GET(self):
        """Handle GET requests."""
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
                http_status = 200
            elif qdrant_healthy or gemini_healthy:
                status = 'degraded'
                http_status = 200
            else:
                status = 'down'
                http_status = 503

            # Send response
            self.send_response(http_status)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            response = {
                'status': status,
                'qdrant': qdrant_healthy,
                'gemini': gemini_healthy,
                'timestamp': int(__import__('time').time())
            }

            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            print(f"Error in health endpoint: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'status': 'error',
                'error': str(e)
            }
            self.wfile.write(json.dumps(response).encode())

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
