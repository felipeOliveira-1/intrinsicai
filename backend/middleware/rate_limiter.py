from fastapi import Request, HTTPException
import time
from typing import Dict, Tuple
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = {}
        
    def _clean_old_requests(self, client_id: str):
        """Remove requests older than 1 minute"""
        if client_id in self.requests:
            current_time = time.time()
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if current_time - req_time < 60
            ]

    async def check_rate_limit(self, request: Request) -> bool:
        client_id = request.client.host
        current_time = time.time()
        
        # Initialize request list for new clients
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Clean old requests
        self._clean_old_requests(client_id)
        
        # Check rate limit
        if len(self.requests[client_id]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for client {client_id}")
            reset_time = self.requests[client_id][0] + 60
            reset_seconds = int(reset_time - current_time)
            
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "reset_in_seconds": reset_seconds,
                    "reset_time": datetime.fromtimestamp(reset_time).isoformat()
                }
            )
        
        # Add new request
        self.requests[client_id].append(current_time)
        return True

async def rate_limit_middleware(request: Request, call_next):
    rate_limiter = RateLimiter()
    await rate_limiter.check_rate_limit(request)
    response = await call_next(request)
    return response
