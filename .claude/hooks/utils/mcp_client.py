"""
MCP HTTP Client Module - Authentication, Connection Pooling, and Resilience

This module implements HTTP clients for communicating with the MCP server with
authentication, connection pooling, rate limiting, and resilience features.

Architecture Reference: Section 15.2 in mcp-auto-injection-architecture.md
Task ID: bd70c110-c43b-4ec9-b5bc-61cdb03a0833
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import sys
import os
from pathlib import Path

# Add the hooks directory to the path for importing
hooks_dir = Path(__file__).parent.parent
sys.path.insert(0, str(hooks_dir))

# Define exception locally since core_clean_arch was removed
class MCPAuthenticationError(Exception):
    """MCP Authentication error."""
    pass

# Configure logging
logger = logging.getLogger(__name__)


class TokenManager:
    """Manages JWT tokens for hook-to-MCP communication with automatic refresh."""
    
    def __init__(self):
        self.token_cache_file = Path.home() / ".claude" / ".mcp_token_cache"
        self.token = None
        self.token_expiry = None
        self.refresh_before = int(os.getenv("TOKEN_REFRESH_BEFORE_EXPIRY", "60"))
    
    def get_valid_token(self) -> str:
        """Get a valid JWT token from .mcp.json file."""

        # Check if token needs refresh
        if self._should_refresh():
            self._refresh_token()

        if not self.token:
            raise MCPAuthenticationError(
                "No .mcp.json token found. Ensure Claude Code is properly configured with MCP server authentication."
            )

        return self.token
    
    def _should_refresh(self) -> bool:
        """Check if token should be refreshed."""
        if not self.token or not self.token_expiry:
            return True
        
        time_until_expiry = self.token_expiry.timestamp() - time.time()
        return time_until_expiry < self.refresh_before
    
    def _refresh_token(self):
        """Refresh token using client credentials."""
        
        # Try to load from cache file first
        if self._load_cached_token():
            return
        
        # Get new token from .mcp.json
        self._request_new_token()
    
    def _load_cached_token(self) -> bool:
        """Load token from cache if valid."""
        if not self.token_cache_file.exists():
            return False
        
        try:
            with open(self.token_cache_file, 'r') as f:
                cache_data = json.load(f)
                expiry = datetime.fromisoformat(cache_data["expiry"])
                
                if datetime.now() < expiry - timedelta(seconds=self.refresh_before):
                    self.token = cache_data["token"]
                    self.token_expiry = expiry
                    return True
        except Exception as e:
            logger.warning(f"Failed to load cached token: {e}")
        
        return False
    
    def _request_new_token(self) -> bool:
        """Get token from .mcp.json file only."""

        # Try to use token from .mcp.json file
        mcp_token = self._get_mcp_json_token()
        if mcp_token:
            logger.info("Using token from .mcp.json file")
            self.token = mcp_token
            # Set a long expiry for .mcp.json tokens (30 days)
            self.token_expiry = datetime.now() + timedelta(days=30)
            self._cache_token()
            return True

        # No token found
        logger.error("No .mcp.json token found")
        return False
    
    def _get_mcp_json_token(self) -> Optional[str]:
        """Extract Bearer token from .mcp.json file if available."""
        try:
            # Look for .mcp.json in project root
            project_root = Path.cwd()
            mcp_json_path = project_root / ".mcp.json"
            
            if not mcp_json_path.exists():
                # Try parent directories up to 3 levels
                for _ in range(3):
                    project_root = project_root.parent
                    mcp_json_path = project_root / ".mcp.json"
                    if mcp_json_path.exists():
                        break
            
            if mcp_json_path.exists():
                with open(mcp_json_path, 'r') as f:
                    mcp_config = json.load(f)
                    
                # Extract token from agenthub_http configuration
                agenthub_config = mcp_config.get("mcpServers", {}).get("agenthub_http", {})
                auth_header = agenthub_config.get("headers", {}).get("Authorization", "")
                
                if auth_header.startswith("Bearer "):
                    return auth_header.replace("Bearer ", "")
        except Exception as e:
            logger.debug(f"Could not read .mcp.json token: {e}")
        
        return None
    
    def _cache_token(self):
        """Cache token to file for reuse."""
        try:
            self.token_cache_file.parent.mkdir(exist_ok=True)
            with open(self.token_cache_file, 'w') as f:
                json.dump({
                    "token": self.token,
                    "expiry": self.token_expiry.isoformat()
                }, f)
            # Secure the file
            os.chmod(self.token_cache_file, 0o600)
        except Exception as e:
            logger.warning(f"Failed to cache token: {e}")


class RateLimiter:
    """Simple rate limiter for HTTP requests."""
    
    def __init__(self, max_requests: int = 100, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def allow_request(self) -> bool:
        """Check if request is allowed under rate limit."""
        current_time = time.time()
        
        # Remove old requests outside time window
        self.requests = [req_time for req_time in self.requests 
                        if current_time - req_time < self.time_window]
        
        # Check if under limit
        if len(self.requests) < self.max_requests:
            self.requests.append(current_time)
            return True
        
        return False


class MCPHTTPClient:
    """HTTP client for communicating with MCP server."""
    
    def __init__(self):
        self.base_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
        self.token_manager = TokenManager()
        self.session = requests.Session()
        self.timeout = int(os.getenv("MCP_SERVER_TIMEOUT", "10"))
        self.max_retries = int(os.getenv("MCP_MAX_RETRIES", "3"))
        self.retry_delay = float(os.getenv("MCP_RETRY_DELAY", "1.0"))
        
        # Configure session with required headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": "Claude-Hooks-MCP-Client/1.0"
        })
    
    def authenticate(self) -> bool:
        """Authenticate with .mcp.json token."""
        try:
            token = self.token_manager.get_valid_token()
            self.session.headers.update({
                "Authorization": f"Bearer {token}"
            })
            return True
        except MCPAuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def query_pending_tasks(self, limit: int = 5, user_id: Optional[str] = None) -> Optional[List[Dict]]:
        """Query MCP server for pending tasks via MCP protocol over HTTP."""
        try:
            # Prepare MCP JSON-RPC request
            mcp_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "manage_task",
                    "arguments": {
                        "action": "list",
                        "status": "todo",
                        "limit": limit
                    }
                },
                "id": 1
            }
            
            if user_id:
                mcp_request["params"]["arguments"]["user_id"] = user_id
            
            # Authenticate and send MCP request
            if self.authenticate():
                # Update headers for MCP protocol
                self.session.headers.update({
                    "Accept": "application/json, text/event-stream"
                })
                
                response = self.session.post(
                    f"{self.base_url}/mcp",
                    json=mcp_request,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Handle MCP JSON-RPC response
                    if "result" in result:
                        mcp_result = result["result"]
                        if isinstance(mcp_result, dict):
                            # Extract tasks from MCP response
                            if "data" in mcp_result and isinstance(mcp_result["data"], dict):
                                tasks = mcp_result["data"].get("tasks", [])
                                logger.info(f"Successfully retrieved {len(tasks)} tasks via MCP protocol")
                                return tasks
                            elif "tasks" in mcp_result:
                                tasks = mcp_result["tasks"]
                                logger.info(f"Successfully retrieved {len(tasks)} tasks via MCP protocol")
                                return tasks
                    elif "error" in result:
                        logger.warning(f"MCP error: {result['error']}")
                else:
                    logger.warning(f"MCP request returned: {response.status_code}")
            else:
                logger.warning("Authentication failed for MCP request")
                
        except Exception as e:
            logger.warning(f"Failed to query tasks via MCP: {e}")
        
        return None
    
    def query_project_context(self, project_id: Optional[str] = None) -> Optional[Dict]:
        """Query project context via MCP protocol."""
        if not self.authenticate():
            return None
        
        try:
            # Prepare MCP JSON-RPC request for project context
            mcp_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "manage_context",
                    "arguments": {
                        "action": "get",
                        "level": "project"
                    }
                },
                "id": 3
            }
            
            if project_id:
                mcp_request["params"]["arguments"]["project_id"] = project_id
            
            # Update headers for MCP protocol
            self.session.headers.update({
                "Accept": "application/json, text/event-stream"
            })
            
            response = self.session.post(
                f"{self.base_url}/mcp",
                json=mcp_request,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Handle MCP JSON-RPC response
                if "result" in result:
                    mcp_result = result["result"]
                    if isinstance(mcp_result, dict):
                        logger.info("Retrieved project context successfully")
                        return mcp_result
                elif "error" in result:
                    logger.warning(f"MCP error getting project context: {result['error']}")
        except Exception as e:
            logger.warning(f"Failed to get project context via MCP: {e}")
        
        return None
    
    def query_git_branch_info(self) -> Optional[Dict]:
        """Query git branch information via MCP protocol."""
        if not self.authenticate():
            return None
        
        try:
            # Prepare MCP JSON-RPC request for git branch info
            mcp_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "manage_git_branch",
                    "arguments": {
                        "action": "list",
                        "limit": 5
                    }
                },
                "id": 4
            }
            
            # Update headers for MCP protocol
            self.session.headers.update({
                "Accept": "application/json, text/event-stream"
            })
            
            response = self.session.post(
                f"{self.base_url}/mcp",
                json=mcp_request,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Handle MCP JSON-RPC response
                if "result" in result:
                    mcp_result = result["result"]
                    if isinstance(mcp_result, dict):
                        logger.info("Retrieved git branch info successfully")
                        return mcp_result
                elif "error" in result:
                    logger.warning(f"MCP error getting git branch info: {result['error']}")
        except Exception as e:
            logger.warning(f"Failed to get git branch info via MCP: {e}")
        
        return None
    
    def get_next_recommended_task(self, git_branch_id: str, user_id: Optional[str] = None) -> Optional[Dict]:
        """Get next recommended task via MCP protocol."""
        if not self.authenticate():
            return None
        
        try:
            # Prepare MCP JSON-RPC request
            mcp_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "manage_task",
                    "arguments": {
                        "action": "next",
                        "git_branch_id": git_branch_id,
                        "include_context": True
                    }
                },
                "id": 2
            }
            
            if user_id:
                mcp_request["params"]["arguments"]["user_id"] = user_id
            
            # Update headers for MCP protocol
            self.session.headers.update({
                "Accept": "application/json, text/event-stream"
            })
            
            response = self.session.post(
                f"{self.base_url}/mcp",
                json=mcp_request,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Handle MCP JSON-RPC response
                if "result" in result:
                    mcp_result = result["result"]
                    if isinstance(mcp_result, dict):
                        # Extract task from MCP response
                        if "data" in mcp_result and isinstance(mcp_result["data"], dict):
                            task = mcp_result["data"].get("task")
                            if task:
                                logger.info(f"Retrieved next task: {task.get('title', 'Unknown')}")
                                return task
                        elif "task" in mcp_result:
                            task = mcp_result["task"]
                            logger.info(f"Retrieved next task: {task.get('title', 'Unknown')}")
                            return task
                elif "error" in result:
                    logger.warning(f"MCP error: {result['error']}")
        except Exception as e:
            logger.warning(f"Failed to get next task via MCP: {e}")
        
        return None
    
    def _execute_with_retry(self, func, *args, **kwargs) -> Optional[Any]:
        """Execute a function with retry logic for resilience."""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                result = func(*args, **kwargs)
                if result is not None:
                    return result
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{self.max_retries})")
                last_error = "timeout"
                
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error (attempt {attempt + 1}/{self.max_retries})")
                last_error = "connection"
                
            except Exception as e:
                logger.warning(f"Request failed: {e} (attempt {attempt + 1}/{self.max_retries})")
                last_error = str(e)
            
            # Wait before retry (exponential backoff)
            if attempt < self.max_retries - 1:
                wait_time = self.retry_delay * (2 ** attempt)
                logger.debug(f"Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
        
        logger.error(f"All retries exhausted. Last error: {last_error}")
        return None
    
    def make_request(self, endpoint: str, payload: dict) -> Optional[dict]:
        """Make authenticated HTTP request to MCP server with retry."""
        if not self.authenticate():
            return None
        
        def _request():
            try:
                response = self.session.post(
                    f"{self.base_url}{endpoint}",
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 401:
                    # Token expired, try to refresh and retry once
                    logger.info("Token expired, attempting refresh")
                    self.token_manager._request_new_token()
                    if self.authenticate():
                        response = self.session.post(
                            f"{self.base_url}{endpoint}",
                            json=payload,
                            timeout=self.timeout
                        )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Request failed: {response.status_code}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"HTTP request failed: {e}")
                raise
        
        return self._execute_with_retry(_request)


class ResilientMCPClient(MCPHTTPClient):
    """HTTP client for MCP server - uses hook endpoint directly."""
    
    def __init__(self):
        super().__init__()
    
    def query_pending_tasks(self, limit: int = 5, user_id: Optional[str] = None) -> Optional[List[Dict]]:
        """Query pending tasks via hook endpoint."""
        return super().query_pending_tasks(limit=limit, user_id=user_id)
    
    def get_next_recommended_task(self, git_branch_id: str, user_id: Optional[str] = None) -> Optional[Dict]:
        """Get next recommended task via hook endpoint."""
        return super().get_next_recommended_task(git_branch_id=git_branch_id, user_id=user_id)


class OptimizedMCPClient(ResilientMCPClient):
    """HTTP client with connection pooling and rate limiting."""
    
    def __init__(self):
        super().__init__()
        self.rate_limiter = RateLimiter(
            max_requests=int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "100")),
            time_window=60
        )
        
        # Configure connection pooling with retry strategy
        retry_strategy = Retry(
            total=int(os.getenv("HTTP_MAX_RETRIES", "3")),
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "OPTIONS"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(
            pool_connections=int(os.getenv("HTTP_POOL_CONNECTIONS", "10")),
            pool_maxsize=int(os.getenv("HTTP_POOL_MAXSIZE", "10")),
            max_retries=retry_strategy,
            pool_block=False
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def make_request(self, endpoint: str, payload: dict) -> Optional[dict]:
        """Make rate-limited request with connection pooling."""
        
        # Check rate limit
        if not self.rate_limiter.allow_request():
            logger.warning("Rate limit exceeded, request throttled")
            return None
        
        # Use parent class method with enhanced session
        return super().make_request(endpoint, payload)


# Convenience functions for easy import
def create_mcp_client(client_type: str = "optimized") -> MCPHTTPClient:
    """Factory function to create MCP client instances."""
    
    if client_type == "basic":
        return MCPHTTPClient()
    elif client_type == "resilient":
        return ResilientMCPClient()
    elif client_type == "optimized":
        return OptimizedMCPClient()
    else:
        raise ValueError(f"Unknown client type: {client_type}")


def get_default_client() -> OptimizedMCPClient:
    """Get default optimized MCP client."""
    return OptimizedMCPClient()


# Example usage and testing functions
def test_mcp_connection() -> bool:
    """Test MCP server connection."""
    client = get_default_client()
    
    try:
        # Test authentication
        if not client.authenticate():
            print("❌ Authentication failed")
            return False
        
        print("✅ Authentication successful")
        
        # Test basic connection
        result = client.make_request("/mcp/manage_connection", {"include_details": True})
        if result:
            print("✅ MCP server connection successful")
            return True
        else:
            print("❌ MCP server connection failed")
            return False
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False


if __name__ == "__main__":
    # Run connection test when executed directly
    print("🔌 Testing MCP HTTP Client Connection...")
    success = test_mcp_connection()
    exit(0 if success else 1)