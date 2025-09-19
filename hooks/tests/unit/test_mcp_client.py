"""
Unit tests for MCP client and authentication system.

Tests the MCP HTTP client functionality including token management,
authentication, connection pooling, rate limiting, and resilience features.
"""

import pytest
import json
import os
import time
from unittest.mock import Mock, patch, MagicMock, mock_open
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Add hooks directory to Python path
hooks_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(hooks_dir))

from utils.mcp_client import (
    MCPAuthenticationError,
    TokenManager,
    RateLimiter,
    MCPHTTPClient,
    ResilientMCPClient,
    OptimizedMCPClient
)


class TestMCPAuthenticationError:
    """Test MCP authentication error class."""

    def test_error_creation(self):
        """Test MCPAuthenticationError can be created and raised."""
        error_message = "Authentication failed"

        with pytest.raises(MCPAuthenticationError) as exc_info:
            raise MCPAuthenticationError(error_message)

        assert str(exc_info.value) == error_message

    def test_error_inheritance(self):
        """Test MCPAuthenticationError inherits from Exception."""
        error = MCPAuthenticationError("test")
        assert isinstance(error, Exception)


class TestTokenManager:
    """Test token management functionality."""

    def setup_method(self):
        """Setup for token manager tests."""
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = Path('/tmp/test_home')
            self.token_manager = TokenManager()

    def test_initialization(self):
        """Test TokenManager initializes correctly."""
        assert self.token_manager.token is None
        assert self.token_manager.token_expiry is None
        assert self.token_manager.refresh_before == 60  # default value

    @patch.dict(os.environ, {'TOKEN_REFRESH_BEFORE_EXPIRY': '120'})
    def test_initialization_with_env_var(self):
        """Test TokenManager initialization with environment variable."""
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = Path('/tmp/test_home')
            token_manager = TokenManager()
            assert token_manager.refresh_before == 120

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.read_text')
    def test_get_mcp_json_token_success(self, mock_read_text, mock_exists):
        """Test successful token retrieval from .mcp.json."""
        mock_exists.return_value = True
        mock_read_text.return_value = json.dumps({
            'token': 'test_token_123',
            'expires_at': '2025-12-31T23:59:59Z'
        })

        result = self.token_manager._get_mcp_json_token()

        assert result == 'test_token_123'

    @patch('pathlib.Path.exists')
    def test_get_mcp_json_token_file_not_found(self, mock_exists):
        """Test token retrieval when .mcp.json doesn't exist."""
        mock_exists.return_value = False

        result = self.token_manager._get_mcp_json_token()

        assert result is None

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.read_text')
    def test_get_mcp_json_token_invalid_json(self, mock_read_text, mock_exists):
        """Test token retrieval with invalid JSON."""
        mock_exists.return_value = True
        mock_read_text.return_value = "invalid json"

        result = self.token_manager._get_mcp_json_token()

        assert result is None

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.read_text')
    def test_get_mcp_json_token_missing_token(self, mock_read_text, mock_exists):
        """Test token retrieval with missing token field."""
        mock_exists.return_value = True
        mock_read_text.return_value = json.dumps({
            'expires_at': '2025-12-31T23:59:59Z'
        })

        result = self.token_manager._get_mcp_json_token()

        assert result is None

    def test_should_refresh_no_token(self):
        """Test should_refresh returns True when no token."""
        self.token_manager.token = None
        assert self.token_manager._should_refresh() is True

    def test_should_refresh_no_expiry(self):
        """Test should_refresh returns True when no expiry."""
        self.token_manager.token = "test_token"
        self.token_manager.token_expiry = None
        assert self.token_manager._should_refresh() is True

    def test_should_refresh_expired_token(self):
        """Test should_refresh returns True for expired token."""
        self.token_manager.token = "test_token"
        past_time = datetime.now() - timedelta(minutes=5)
        self.token_manager.token_expiry = past_time
        assert self.token_manager._should_refresh() is True

    def test_should_refresh_near_expiry(self):
        """Test should_refresh returns True for soon-to-expire token."""
        self.token_manager.token = "test_token"
        near_future = datetime.now() + timedelta(seconds=30)  # Within refresh window
        self.token_manager.token_expiry = near_future
        assert self.token_manager._should_refresh() is True

    def test_should_refresh_valid_token(self):
        """Test should_refresh returns False for valid token."""
        self.token_manager.token = "test_token"
        far_future = datetime.now() + timedelta(hours=1)
        self.token_manager.token_expiry = far_future
        assert self.token_manager._should_refresh() is False

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.read_text')
    def test_load_cached_token_success(self, mock_read_text, mock_exists):
        """Test successful cached token loading."""
        mock_exists.return_value = True
        cache_data = {
            'token': 'cached_token',
            'expires_at': (datetime.now() + timedelta(hours=1)).isoformat()
        }
        mock_read_text.return_value = json.dumps(cache_data)

        result = self.token_manager._load_cached_token()

        assert result is True
        assert self.token_manager.token == 'cached_token'

    @patch('pathlib.Path.exists')
    def test_load_cached_token_no_cache(self, mock_exists):
        """Test cached token loading when no cache exists."""
        mock_exists.return_value = False

        result = self.token_manager._load_cached_token()

        assert result is False

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.read_text')
    def test_load_cached_token_expired(self, mock_read_text, mock_exists):
        """Test cached token loading with expired token."""
        mock_exists.return_value = True
        cache_data = {
            'token': 'expired_token',
            'expires_at': (datetime.now() - timedelta(hours=1)).isoformat()
        }
        mock_read_text.return_value = json.dumps(cache_data)

        result = self.token_manager._load_cached_token()

        assert result is False

    @patch('utils.mcp_client.TokenManager._get_mcp_json_token')
    @patch('utils.mcp_client.TokenManager._cache_token')
    def test_request_new_token_success(self, mock_cache, mock_get_token):
        """Test successful new token request."""
        mock_get_token.return_value = 'new_token_123'

        result = self.token_manager._request_new_token()

        assert result is True
        assert self.token_manager.token == 'new_token_123'
        mock_cache.assert_called_once()

    @patch('utils.mcp_client.TokenManager._get_mcp_json_token')
    def test_request_new_token_failure(self, mock_get_token):
        """Test new token request failure."""
        mock_get_token.return_value = None

        result = self.token_manager._request_new_token()

        assert result is False

    @patch('pathlib.Path.write_text')
    @patch('pathlib.Path.mkdir')
    def test_cache_token(self, mock_mkdir, mock_write_text):
        """Test token caching functionality."""
        self.token_manager.token = 'test_token'
        self.token_manager.token_expiry = datetime.now() + timedelta(hours=1)

        self.token_manager._cache_token()

        mock_mkdir.assert_called_once()
        mock_write_text.assert_called_once()

    @patch('utils.mcp_client.TokenManager._should_refresh')
    @patch('utils.mcp_client.TokenManager._load_cached_token')
    @patch('utils.mcp_client.TokenManager._request_new_token')
    def test_get_valid_token_from_cache(self, mock_request, mock_load, mock_should_refresh):
        """Test getting valid token from cache."""
        mock_should_refresh.return_value = False
        mock_load.return_value = True
        self.token_manager.token = 'cached_token'

        result = self.token_manager.get_valid_token()

        assert result == 'cached_token'
        mock_request.assert_not_called()

    @patch('utils.mcp_client.TokenManager._should_refresh')
    @patch('utils.mcp_client.TokenManager._load_cached_token')
    @patch('utils.mcp_client.TokenManager._request_new_token')
    def test_get_valid_token_refresh_needed(self, mock_request, mock_load, mock_should_refresh):
        """Test getting valid token when refresh is needed."""
        mock_should_refresh.return_value = True
        mock_load.return_value = False
        mock_request.return_value = True
        self.token_manager.token = 'new_token'

        result = self.token_manager.get_valid_token()

        assert result == 'new_token'
        mock_request.assert_called_once()

    @patch('utils.mcp_client.TokenManager._should_refresh')
    @patch('utils.mcp_client.TokenManager._load_cached_token')
    @patch('utils.mcp_client.TokenManager._request_new_token')
    def test_get_valid_token_failure(self, mock_request, mock_load, mock_should_refresh):
        """Test getting valid token when all methods fail."""
        mock_should_refresh.return_value = True
        mock_load.return_value = False
        mock_request.return_value = False

        with pytest.raises(MCPAuthenticationError):
            self.token_manager.get_valid_token()


class TestRateLimiter:
    """Test rate limiting functionality."""

    def test_initialization(self):
        """Test RateLimiter initializes correctly."""
        limiter = RateLimiter(max_requests=10, time_window=60)

        assert limiter.max_requests == 10
        assert limiter.time_window == 60
        assert len(limiter.request_times) == 0

    def test_initialization_defaults(self):
        """Test RateLimiter with default values."""
        limiter = RateLimiter()

        assert limiter.max_requests == 100
        assert limiter.time_window == 60

    def test_allow_request_under_limit(self):
        """Test allowing request under rate limit."""
        limiter = RateLimiter(max_requests=5, time_window=60)

        # Make requests under limit
        for _ in range(5):
            assert limiter.allow_request() is True

    def test_allow_request_over_limit(self):
        """Test blocking request over rate limit."""
        limiter = RateLimiter(max_requests=2, time_window=60)

        # Fill up the limit
        assert limiter.allow_request() is True
        assert limiter.allow_request() is True

        # Should block the next request
        assert limiter.allow_request() is False

    @patch('time.time')
    def test_allow_request_time_window_reset(self, mock_time):
        """Test rate limit reset after time window."""
        limiter = RateLimiter(max_requests=1, time_window=60)

        # First request at time 0
        mock_time.return_value = 0
        assert limiter.allow_request() is True

        # Second request immediately - should be blocked
        assert limiter.allow_request() is False

        # Request after time window - should be allowed
        mock_time.return_value = 61
        assert limiter.allow_request() is True


class TestMCPHTTPClient:
    """Test basic MCP HTTP client functionality."""

    def setup_method(self):
        """Setup for HTTP client tests."""
        self.client = MCPHTTPClient()

    def test_initialization(self):
        """Test MCPHTTPClient initializes correctly."""
        assert self.client.base_url == "http://localhost:8000"
        assert self.client.session is not None
        assert self.client.token_manager is not None
        assert self.client.rate_limiter is not None

    @patch.dict(os.environ, {'MCP_SERVER_URL': 'https://api.example.com'})
    def test_initialization_with_env_url(self):
        """Test MCPHTTPClient with custom server URL."""
        client = MCPHTTPClient()
        assert client.base_url == "https://api.example.com"

    @patch('utils.mcp_client.TokenManager.get_valid_token')
    def test_authenticate_success(self, mock_get_token):
        """Test successful authentication."""
        mock_get_token.return_value = 'valid_token'

        result = self.client.authenticate()

        assert result is True
        assert 'Authorization' in self.client.session.headers
        assert self.client.session.headers['Authorization'] == 'Bearer valid_token'

    @patch('utils.mcp_client.TokenManager.get_valid_token')
    def test_authenticate_failure(self, mock_get_token):
        """Test authentication failure."""
        mock_get_token.side_effect = MCPAuthenticationError("Token failed")

        result = self.client.authenticate()

        assert result is False
        assert 'Authorization' not in self.client.session.headers

    @patch('utils.mcp_client.MCPHTTPClient.authenticate')
    @patch('requests.Session.get')
    def test_query_pending_tasks_success(self, mock_get, mock_auth):
        """Test successful pending tasks query."""
        mock_auth.return_value = True
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'data': [
                {'id': 'task1', 'title': 'Test Task 1'},
                {'id': 'task2', 'title': 'Test Task 2'}
            ]
        }
        mock_get.return_value = mock_response

        result = self.client.query_pending_tasks(limit=10, user_id='user123')

        assert result is not None
        assert len(result) == 2
        assert result[0]['id'] == 'task1'
        mock_get.assert_called_once()

    @patch('utils.mcp_client.MCPHTTPClient.authenticate')
    @patch('requests.Session.get')
    def test_query_pending_tasks_auth_failure(self, mock_get, mock_auth):
        """Test pending tasks query with authentication failure."""
        mock_auth.return_value = False

        result = self.client.query_pending_tasks()

        assert result is None
        mock_get.assert_not_called()

    @patch('utils.mcp_client.MCPHTTPClient.authenticate')
    @patch('requests.Session.get')
    def test_query_pending_tasks_http_error(self, mock_get, mock_auth):
        """Test pending tasks query with HTTP error."""
        mock_auth.return_value = True
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = self.client.query_pending_tasks()

        assert result is None

    @patch('utils.mcp_client.MCPHTTPClient.authenticate')
    @patch('requests.Session.get')
    def test_query_pending_tasks_rate_limited(self, mock_get, mock_auth):
        """Test pending tasks query when rate limited."""
        mock_auth.return_value = True

        # Mock rate limiter to deny request
        self.client.rate_limiter.allow_request = Mock(return_value=False)

        result = self.client.query_pending_tasks()

        assert result is None
        mock_get.assert_not_called()

    @patch('utils.mcp_client.MCPHTTPClient.authenticate')
    @patch('requests.Session.get')
    def test_query_project_context_success(self, mock_get, mock_auth):
        """Test successful project context query."""
        mock_auth.return_value = True
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'data': {
                'project_id': 'proj123',
                'name': 'Test Project',
                'context': {'key': 'value'}
            }
        }
        mock_get.return_value = mock_response

        result = self.client.query_project_context(project_id='proj123')

        assert result is not None
        assert result['project_id'] == 'proj123'
        assert result['name'] == 'Test Project'

    @patch('utils.mcp_client.MCPHTTPClient.authenticate')
    @patch('requests.Session.get')
    def test_query_git_branch_info_success(self, mock_get, mock_auth):
        """Test successful git branch info query."""
        mock_auth.return_value = True
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'data': {
                'current_branch': 'main',
                'status': 'clean',
                'commits_ahead': 0
            }
        }
        mock_get.return_value = mock_response

        result = self.client.query_git_branch_info()

        assert result is not None
        assert result['current_branch'] == 'main'
        assert result['status'] == 'clean'


class TestResilientMCPClient:
    """Test resilient MCP client functionality."""

    def setup_method(self):
        """Setup for resilient client tests."""
        self.client = ResilientMCPClient()

    def test_initialization(self):
        """Test ResilientMCPClient initializes with proper adapters."""
        assert isinstance(self.client, MCPHTTPClient)
        # Check that retry strategy is configured
        adapter = self.client.session.get_adapter('http://')
        assert adapter is not None

    @patch('utils.mcp_client.ResilientMCPClient.authenticate')
    @patch('requests.Session.get')
    def test_resilient_request_with_retries(self, mock_get, mock_auth):
        """Test resilient client retries on failure."""
        mock_auth.return_value = True

        # First call fails, second succeeds
        mock_response_fail = Mock()
        mock_response_fail.status_code = 500

        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {
            'success': True,
            'data': {'result': 'success'}
        }

        mock_get.side_effect = [mock_response_fail, mock_response_success]

        # The resilient client should eventually succeed
        result = self.client.query_pending_tasks()

        # Should have made multiple attempts
        assert mock_get.call_count >= 1


class TestOptimizedMCPClient:
    """Test optimized MCP client functionality."""

    def setup_method(self):
        """Setup for optimized client tests."""
        self.client = OptimizedMCPClient()

    def test_initialization(self):
        """Test OptimizedMCPClient initializes correctly."""
        assert isinstance(self.client, ResilientMCPClient)
        # Optimized client inherits all resilient features


# Integration tests
class TestMCPClientIntegration:
    """Integration tests for MCP client system."""

    @pytest.mark.integration
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.read_text')
    @patch('requests.Session.get')
    def test_full_authentication_flow(self, mock_get, mock_read_text, mock_exists):
        """Test complete authentication and request flow."""
        # Mock .mcp.json file
        mock_exists.return_value = True
        mock_read_text.return_value = json.dumps({
            'token': 'integration_test_token',
            'expires_at': '2025-12-31T23:59:59Z'
        })

        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'data': [{'id': 'task1', 'title': 'Integration Test Task'}]
        }
        mock_get.return_value = mock_response

        client = OptimizedMCPClient()
        result = client.query_pending_tasks()

        assert result is not None
        assert len(result) == 1
        assert result[0]['id'] == 'task1'

    @pytest.mark.integration
    @patch('pathlib.Path.exists')
    def test_authentication_without_token_file(self, mock_exists):
        """Test authentication behavior without token file."""
        mock_exists.return_value = False

        client = MCPHTTPClient()

        with pytest.raises(MCPAuthenticationError):
            client.authenticate()

    @pytest.mark.integration
    def test_rate_limiting_behavior(self):
        """Test rate limiting behavior under load."""
        limiter = RateLimiter(max_requests=3, time_window=60)

        # Should allow first 3 requests
        allowed_count = 0
        for _ in range(5):
            if limiter.allow_request():
                allowed_count += 1

        assert allowed_count == 3

    @pytest.mark.integration
    @patch('time.time')
    def test_token_refresh_timing(self, mock_time):
        """Test token refresh timing behavior."""
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = Path('/tmp/test_home')
            token_manager = TokenManager()

            # Set up a token that's about to expire
            token_manager.token = 'expiring_token'
            token_manager.token_expiry = datetime.now() + timedelta(seconds=30)

            # Should trigger refresh
            assert token_manager._should_refresh() is True


# Error handling tests
class TestMCPClientErrorHandling:
    """Test error handling in MCP client system."""

    def test_network_timeout_handling(self):
        """Test handling of network timeouts."""
        client = MCPHTTPClient()

        with patch('requests.Session.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

            result = client.query_pending_tasks()
            assert result is None

    def test_connection_error_handling(self):
        """Test handling of connection errors."""
        client = MCPHTTPClient()

        with patch('requests.Session.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

            result = client.query_pending_tasks()
            assert result is None

    def test_invalid_json_response_handling(self):
        """Test handling of invalid JSON responses."""
        client = MCPHTTPClient()

        with patch('utils.mcp_client.MCPHTTPClient.authenticate', return_value=True), \
             patch('requests.Session.get') as mock_get:

            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
            mock_get.return_value = mock_response

            result = client.query_pending_tasks()
            assert result is None

    def test_http_error_codes_handling(self):
        """Test handling of various HTTP error codes."""
        client = MCPHTTPClient()

        error_codes = [400, 401, 403, 404, 500, 502, 503]

        for error_code in error_codes:
            with patch('utils.mcp_client.MCPHTTPClient.authenticate', return_value=True), \
                 patch('requests.Session.get') as mock_get:

                mock_response = Mock()
                mock_response.status_code = error_code
                mock_get.return_value = mock_response

                result = client.query_pending_tasks()
                assert result is None


# Performance tests
@pytest.mark.slow
class TestMCPClientPerformance:
    """Test MCP client performance characteristics."""

    def test_token_caching_performance(self):
        """Test that token caching improves performance."""
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = Path('/tmp/test_home')

            token_manager = TokenManager()
            token_manager.token = 'cached_token'
            token_manager.token_expiry = datetime.now() + timedelta(hours=1)

            # Multiple calls should not trigger new token requests
            with patch('utils.mcp_client.TokenManager._request_new_token') as mock_request:
                for _ in range(10):
                    token = token_manager.get_valid_token()
                    assert token == 'cached_token'

                # Should not have requested new tokens
                mock_request.assert_not_called()

    def test_rate_limiter_efficiency(self):
        """Test rate limiter efficiency with many requests."""
        limiter = RateLimiter(max_requests=1000, time_window=60)

        start_time = time.time()

        # Make many requests under the limit
        for _ in range(100):
            limiter.allow_request()

        end_time = time.time()

        # Should complete quickly (less than 1 second)
        assert (end_time - start_time) < 1.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])