"""
Chat endpoint for RAG chatbot.
Handles POST requests with user queries.
"""

import json
import os
from http.server import BaseHTTPRequestHandler
from dotenv import load_dotenv
from lib.rag import RAGOrchestrator
from lib.utils import RateLimiter, validate_query, format_error_response

# Load environment variables
load_dotenv()

# Initialize rate limiter (10 requests per minute)
rate_limiter = RateLimiter(max_requests=10, window_seconds=60)


class handler(BaseHTTPRequestHandler):
    """Serverless function handler for Vercel."""

    def do_POST(self):
        """Handle POST requests."""
        try:
            # Get client IP for rate limiting
            client_ip = self.headers.get('X-Forwarded-For', self.client_address[0])

            # Check rate limit
            if not rate_limiter.is_allowed(client_ip):
                self.send_response(429)
                self.send_header('Content-type', 'application/json')
                self.send_header('Retry-After', '60')
                self.end_headers()
                response = format_error_response(
                    'Too many requests. Please try again later.',
                    'RATE_LIMIT'
                )
                self.wfile.write(json.dumps(response).encode())
                return

            # Parse request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')

            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = format_error_response('Invalid JSON', 'INVALID_REQUEST')
                self.wfile.write(json.dumps(response).encode())
                return

            # Extract query
            query = data.get('query', '').strip()

            # Validate query
            validation = validate_query(query)
            if not validation['valid']:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = format_error_response(
                    validation['error'],
                    'INVALID_QUERY'
                )
                self.wfile.write(json.dumps(response).encode())
                return

            # Process query through RAG
            rag = RAGOrchestrator()
            result = rag.process_query(query)

            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            print(f"Error in chat endpoint: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = format_error_response(
                'Internal server error. Please try again.',
                'API_ERROR'
            )
            self.wfile.write(json.dumps(response).encode())

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
