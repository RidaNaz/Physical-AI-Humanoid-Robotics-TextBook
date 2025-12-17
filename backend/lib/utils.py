"""
Utility functions for API endpoints.
"""

import time
from typing import Dict
from collections import defaultdict

class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)

    def is_allowed(self, identifier: str) -> bool:
        """
        Check if request is allowed.

        Args:
            identifier: Unique identifier (e.g., IP address)

        Returns:
            True if allowed, False if rate limited
        """
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > window_start
        ]

        # Check limit
        if len(self.requests[identifier]) >= self.max_requests:
            return False

        # Add current request
        self.requests[identifier].append(now)
        return True


def validate_query(query: str, max_length: int = 500) -> Dict:
    """
    Validate user query.

    Args:
        query: User query string
        max_length: Maximum query length

    Returns:
        Dictionary with 'valid' boolean and 'error' message
    """
    if not query or not query.strip():
        return {'valid': False, 'error': 'Query cannot be empty'}

    if len(query) > max_length:
        return {'valid': False, 'error': f'Query too long (max {max_length} characters)'}

    # Basic injection prevention
    suspicious_patterns = [
        'ignore previous instructions',
        'ignore all previous',
        'disregard previous',
        'forget previous'
    ]

    query_lower = query.lower()
    for pattern in suspicious_patterns:
        if pattern in query_lower:
            return {'valid': False, 'error': 'Invalid query format'}

    return {'valid': True, 'error': None}


def format_error_response(error_message: str, error_code: str = 'ERROR') -> Dict:
    """
    Format error response.

    Args:
        error_message: Error message
        error_code: Error code

    Returns:
        Error response dictionary
    """
    return {
        'error': error_message,
        'code': error_code
    }
