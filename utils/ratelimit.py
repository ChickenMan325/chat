import time
from collections import defaultdict
from utils.logutils import log_info, log_warning

class RateLimiter:
    """
    Rate limiting utility to prevent abuse of API endpoints
    
    Tracks requests by key (e.g., IP address) and enforces
    a maximum number of requests within a time window
    """
    def __init__(self, limit=5, window=60):
        """
        Initialize rate limiter
        
        Args:
            limit: Maximum number of requests allowed in the window
            window: Time window in seconds
        """
        self.limit = limit
        self.window = window
        self.requests = defaultdict(list)
        
    def is_rate_limited(self, key):
        """
        Check if a key is rate limited
        
        Args:
            key: Identifier for the client (e.g., IP address)
            
        Returns:
            Boolean indicating if the request should be limited
        """
        now = time.time()
        # Clean up old requests
        self.requests[key] = [t for t in self.requests[key] if now - t < self.window]
        
        if len(self.requests[key]) >= self.limit:
            log_warning(f"Rate limit exceeded for {key}")
            return True
            
        self.requests[key].append(now)
        return False

# Singleton instances for different API endpoints
login_limiter = RateLimiter(5, 60)  # 5 attempts per minute
