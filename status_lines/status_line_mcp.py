#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
#     "requests",
# ]
# ///

import json
import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

try:
    from dotenv import load_dotenv
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    load_dotenv()
except ImportError:
    pass  # dependencies are optional

# Import the agent state manager utilities
sys.path.insert(0, str(Path(__file__).parent.parent / "hooks"))
from utils.agent_state_manager import get_current_agent, get_agent_role_from_session


def check_mcp_authentication():
    """Check if .mcp.json token is available for MCP authentication."""
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
                return True, None
            else:
                return False, "No Bearer token found in .mcp.json"
        else:
            return False, ".mcp.json file not found"
    except Exception as e:
        return False, f"Error reading .mcp.json: {str(e)}"


def get_mcp_connection_status():
    """Get MCP server connection status with caching and resilient error handling."""

    # Configuration
    cache_duration = int(os.getenv("MCP_STATUS_CACHE_DURATION", "45"))  # seconds
    connection_timeout = float(os.getenv("MCP_CONNECTION_TIMEOUT", "2.0"))  # seconds

    # Try to get server URL from .mcp.json first
    server_url = "http://localhost:8000"  # default fallback
    try:
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

            # Extract URL from agenthub_http configuration
            agenthub_config = mcp_config.get("mcpServers", {}).get("agenthub_http", {})
            configured_url = agenthub_config.get("url", "")
            if configured_url:
                server_url = configured_url
    except Exception:
        pass  # Fall back to environment variable or default

    # Override with environment variable if set
    server_url = os.getenv("MCP_SERVER_URL", server_url)

    # Cache file location
    cache_file = Path("logs") / "mcp_connection_cache.json"

    try:
        # Check cache first
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
                cache_time = datetime.fromisoformat(cache_data.get("timestamp", ""))

                # Use cached result if still valid
                if datetime.now() - cache_time < timedelta(seconds=cache_duration):
                    cached_status = cache_data.get("status", "❌ Unknown")
                    return cached_status
    except Exception:
        pass  # Ignore cache read errors

    # Test connection
    status = _test_mcp_connection(server_url, connection_timeout)

    # Cache the result
    try:
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_file, 'w') as f:
            json.dump({
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "server_url": server_url
            }, f)
    except Exception:
        pass  # Ignore cache write errors

    return status


def _test_mcp_connection(server_url, timeout):
    """Test actual connection to MCP server."""

    try:
        # Create session with retry strategy
        session = requests.Session()

        # Configure retry strategy for resilience
        retry_strategy = Retry(
            total=1,  # Only 1 retry for fast status checks
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=0.1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Set headers
        session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Status-Line-MCP-Check/1.0"
        })

        # Determine base URL for health check
        # If the URL ends with /mcp, use the base URL for /health
        # Otherwise append /health to the URL
        if server_url.endswith('/mcp'):
            base_url = server_url[:-4]  # Remove '/mcp' suffix
            health_url = f"{base_url}/health"
        else:
            health_url = f"{server_url}/health"

        # First try health endpoint (fast and reliable)
        start_time = time.time()

        response = session.get(
            health_url,
            timeout=timeout
        )

        response_time = int((time.time() - start_time) * 1000)  # ms

        if response.status_code == 200:
            result = response.json()
            status = result.get("status", "unknown")
            server_name = result.get("server", "MCP")

            if status == "healthy":
                # Check if auth is enabled and test accordingly
                auth_enabled = result.get("auth_enabled", True)

                if auth_enabled:
                    # Test authentication status
                    auth_valid, auth_error = check_mcp_authentication()
                    if not auth_valid:
                        return f"❌ Auth Required ({server_url}) | {auth_error}"
                    else:
                        return f"✅ Connected ({server_url}) {response_time}ms"
                else:
                    # Auth disabled - server is healthy and ready
                    return f"✅ Connected ({server_url}) {response_time}ms"
            else:
                return f"❌ Unhealthy ({server_url}) | Status: {status}"
        elif response.status_code == 401:
            return f"❌ Auth Failed ({server_url})"
        elif response.status_code == 404:
            return f"❌ Not Found ({server_url})"
        else:
            return f"❌ HTTP {response.status_code} ({server_url})"

    except requests.exceptions.Timeout:
        return f"❌ Timeout ({server_url})"
    except requests.exceptions.ConnectionError:
        return f"❌ Connection Refused ({server_url})"
    except Exception as e:
        error_msg = str(e)[:30] + "..." if len(str(e)) > 30 else str(e)
        return f"❌ Error ({server_url}) | {error_msg}"


def _get_mcp_token():
    """Get MCP token from .mcp.json file."""
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
    except Exception:
        pass

    return None


def get_project_name():
    """Get project name from git remote origin or directory name."""
    try:
        # Try git remote origin URL first
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            url = result.stdout.strip()
            if url:
                # Extract project name from URL (handle both SSH and HTTPS)
                # Examples: git@github.com:user/repo.git -> repo
                #          https://github.com/user/repo.git -> repo
                project_name = Path(url).stem.replace('.git', '')
                if project_name and project_name != 'origin':
                    return project_name

        # Fallback to current directory name
        return Path.cwd().name
    except Exception:
        # Final fallback to current directory name
        return Path.cwd().name


def get_git_branch():
    """Get current git branch if in a git repository."""
    try:
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            branch = result.stdout.strip()
            if branch:
                return branch
            else:
                # Handle detached HEAD state
                result = subprocess.run(
                    ['git', 'rev-parse', '--short', 'HEAD'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0:
                    return f"detached:{result.stdout.strip()}"
        return "no-git"
    except Exception:
        return "no-git"


def get_git_status():
    """Get git status indicators."""
    try:
        # Check if there are uncommitted changes
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            changes = result.stdout.strip()
            if changes:
                lines = changes.split('\n')
                return f"±{len(lines)}"
    except Exception:
        pass
    return ""


def log_status_line(input_data, status_line_output, error_message=None):
    """Log status line event to logs directory."""
    # Ensure logs directory exists
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "status_line.json"

    # Read existing log data or initialize empty list
    if log_file.exists():
        with open(log_file, "r") as f:
            try:
                log_data = json.load(f)
            except (json.JSONDecodeError, ValueError):
                log_data = []
    else:
        log_data = []

    # Create log entry with input data and generated output
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "version": "v4",
        "input_data": input_data,
        "status_line_output": status_line_output,
    }

    if error_message:
        log_entry["error"] = error_message

    # Append the log entry
    log_data.append(log_entry)

    # Write back to file with formatting
    with open(log_file, "w") as f:
        json.dump(log_data, f, indent=2)


def get_session_data(session_id):
    """Get session data including agent name, prompts, and extras."""
    session_file = Path(f".claude/data/sessions/{session_id}.json")

    if not session_file.exists():
        return None, f"Session file {session_file} does not exist"

    try:
        with open(session_file, "r") as f:
            session_data = json.load(f)
            return session_data, None
    except Exception as e:
        return None, f"Error reading session file: {str(e)}"


def truncate_prompt(prompt, max_length=75):
    """Truncate prompt to specified length."""
    # Remove newlines and excessive whitespace
    prompt = " ".join(prompt.split())

    if len(prompt) > max_length:
        return prompt[: max_length - 3] + "..."
    return prompt


def get_prompt_icon(prompt):
    """Get icon based on prompt type."""
    if prompt.startswith("/"):
        return "⚡"
    elif "?" in prompt:
        return "❓"
    elif any(
        word in prompt.lower()
        for word in ["create", "write", "add", "implement", "build"]
    ):
        return "💡"
    elif any(word in prompt.lower() for word in ["fix", "debug", "error", "issue"]):
        return "🐛"
    elif any(word in prompt.lower() for word in ["refactor", "improve", "optimize"]):
        return "♻️"
    else:
        return "💬"


def format_extras(extras):
    """Format extras dictionary into a compact string."""
    if not extras:
        return None
    
    # Format each key-value pair
    pairs = []
    for key, value in extras.items():
        # Truncate value if too long
        str_value = str(value)
        if len(str_value) > 20:
            str_value = str_value[:17] + "..."
        pairs.append(f"{key}:{str_value}")
    
    return " ".join(pairs)


def generate_status_line(input_data):
    """Generate the status line with project name, git branch, agent name, and MCP connection status."""
    # Extract session ID from input data
    session_id = input_data.get("session_id", "unknown")

    # Get model name
    model_info = input_data.get("model", {})
    model_name = model_info.get("display_name", "Claude")

    # Configuration options from environment variables
    show_project = os.getenv('STATUS_SHOW_PROJECT', 'true').lower() in ('true', '1', 'yes', 'on')
    show_branch = os.getenv('STATUS_SHOW_BRANCH', 'true').lower() in ('true', '1', 'yes', 'on')
    short_project_name = os.getenv('STATUS_SHORT_PROJECT_NAME', 'false').lower() in ('true', '1', 'yes', 'on')

    # Check MCP authentication status first for fallback
    auth_valid, auth_error = check_mcp_authentication()

    # If authentication failed, show prominent error (fallback behavior)
    if not auth_valid:
        error_status = f"\033[91m🔐 MCP AUTH ERROR:\033[0m \033[93m{auth_error}\033[0m \033[90m| Fix .mcp.json configuration\033[0m"
        log_status_line(input_data, error_status, f"MCP Authentication Error: {auth_error}")
        return error_status

    # Get session data
    session_data, error = get_session_data(session_id)

    # Build status line components
    parts = []

    # Model name - should be first
    parts.append(f"\033[1;96m◆ {model_name}\033[0m")  # Bold cyan for model name

    # Project name - prominent display as requested
    if show_project:
        project_name = get_project_name()
        if project_name:
            # Option to show short project name (just the name without path info)
            if short_project_name and len(project_name) > 20:
                project_name = project_name[:17] + "..."
            parts.append(f"\033[1;94m📁 {project_name}\033[0m")  # Bold blue with folder icon

    # Git branch with enhanced display and status
    if show_branch:
        git_branch = get_git_branch()
        if git_branch and git_branch != "no-git":
            git_status = get_git_status()

            # Color code branches by type
            branch_color = "\033[92m"  # Default green
            if git_branch == "main" or git_branch == "master":
                branch_color = "\033[1;92m"  # Bold green for main branches
            elif git_branch.startswith("develop"):
                branch_color = "\033[93m"  # Yellow for develop
            elif git_branch.startswith("feature/"):
                branch_color = "\033[94m"  # Blue for features
            elif git_branch.startswith("hotfix/"):
                branch_color = "\033[91m"  # Red for hotfixes
            elif git_branch.startswith("detached:"):
                branch_color = "\033[95m"  # Magenta for detached HEAD

            if git_status:
                # Modified files indicator
                parts.append(f"{branch_color}🌿 {git_branch}\033[0m \033[93m{git_status}\033[0m")
            else:
                # Clean state
                parts.append(f"{branch_color}🌿 {git_branch}\033[0m")



    # Get real-time MCP connection status
    try:
        mcp_status = get_mcp_connection_status()
    except Exception as e:
        # Fallback to simple status if connection check fails
        mcp_status = f"🔄 MCP Status Error: {str(e)[:20]}..."

    # MCP Connection status - Real-time connection with color coding
    if "✅" in mcp_status:
        # Connected - Green
        parts.append(f"\033[92m🔗 MCP: {mcp_status}\033[0m")
    elif "🔄" in mcp_status:
        # Checking - Yellow
        parts.append(f"\033[93m🔗 MCP: {mcp_status}\033[0m")
    else:
        # Error/Disconnected - Red
        parts.append(f"\033[91m🔗 MCP: {mcp_status}\033[0m")


    # Get current agent from session state for consistent display
    current_agent = get_current_agent(session_id) if session_id else 'master-orchestrator-agent'

    # Active agent display - use current_agent from session state
    parts.append(f"\033[92m🎯 Active: {current_agent}\033[0m")  # Green text showing active role

    # Dynamic agent role display - Based on session state
    agent_role = get_agent_role_from_session(session_id) if session_id else 'Assistant'

    if agent_role and agent_role != 'Assistant':
        # Show dynamic agent role format: [Agent] [Role]
        parts.append(f"\033[94m[Agent] [{agent_role}]\033[0m")  # Blue text for agent role

        # Last prompt display - should be at the end
    if session_data:
        prompts = session_data.get('prompts', [])
        if prompts and len(prompts) > 0:
            # Get the most recent prompt
            last_prompt = prompts[-1] if isinstance(prompts, list) else str(prompts)
            if last_prompt:
                prompt_icon = get_prompt_icon(last_prompt)
                truncated_prompt = truncate_prompt(last_prompt, 75)
                parts.append(f"\033[96m{prompt_icon} {truncated_prompt}\033[0m")  # Cyan for prompt

    # Join with separator (using bullet separator for cleaner look)
    status_line = " • ".join(parts)

    return status_line


def main():
    try:
        # Read JSON input from stdin
        input_data = json.loads(sys.stdin.read())

        # Generate status line
        status_line = generate_status_line(input_data)

        # Log the status line event (without error since it's successful)
        log_status_line(input_data, status_line)

        # Output the status line (first line of stdout becomes the status line)
        print(status_line)

        # Success
        sys.exit(0)

    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully - output basic status
        print("\033[31m[Agent] [Claude] 💭 JSON Error\033[0m")
        sys.exit(0)
    except Exception as e:
        # Handle any other errors gracefully - output basic status
        print(f"\033[31m[Agent] [Claude] 💭 Error: {str(e)}\033[0m")
        sys.exit(0)


if __name__ == "__main__":
    main()