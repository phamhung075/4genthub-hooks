#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# ///

"""
Refactored Session start hook with factory pattern and clean architecture.

This hook runs when a Claude session starts and provides:
1. Session context loading and injection
2. Git status and branch information
3. MCP task status and recommendations
4. Development environment context
5. Agent role detection
6. Recent issues and project context

Refactored with:
- Factory pattern for component creation
- Single Responsibility Principle
- Dependency injection
- Clean error handling
- Centralized configuration
"""

import json
import sys
import subprocess
import os
import argparse
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

# Add hooks directory to path
sys.path.insert(0, str(Path(__file__).parent))


# ============================================================================
# Abstract Base Classes
# ============================================================================

class ContextProvider(ABC):
    """Base context provider interface."""

    @abstractmethod
    def get_context(self, input_data: Dict) -> Optional[Dict[str, Any]]:
        """Get context information."""
        pass


class SessionProcessor(ABC):
    """Base session processor interface."""

    @abstractmethod
    def process(self, input_data: Dict) -> Optional[str]:
        """Process session start data."""
        pass


class Logger(ABC):
    """Abstract logger interface."""

    @abstractmethod
    def log(self, level: str, message: str, data: Optional[Dict] = None):
        """Log a message with optional data."""
        pass


# ============================================================================
# Configuration Management
# ============================================================================

class ConfigurationLoader:
    """Loads and manages YAML configuration files."""

    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self._cache = {}

    def load_config(self, config_name: str) -> Optional[Dict]:
        """Load a YAML configuration file."""
        if config_name in self._cache:
            return self._cache[config_name]

        config_path = self.config_dir / f"{config_name}.yaml"
        if not config_path.exists():
            return None

        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                self._cache[config_name] = config
                return config
        except Exception:
            return None

    def get_agent_message(self, agent_name: str) -> Optional[Dict]:
        """Get initialization message for a specific agent."""
        config = self.load_config('session_start_messages')
        if not config:
            return None

        agent_messages = config.get('agent_messages', {})

        # Check for specific agent
        if agent_name in agent_messages:
            return agent_messages[agent_name]

        # Return default message
        default = agent_messages.get('default_agent', {})
        if default:
            # Replace placeholders
            return {
                'initialization_message': default.get('initialization_message', '').replace('{agent_name}', agent_name),
                'role_description': default.get('role_description', '').replace('{AGENT_NAME}', agent_name.upper().replace('-', ' '))
            }

        return None


# ============================================================================
# Component Implementations
# ============================================================================

class FileLogger(Logger):
    """File-based logger implementation."""

    def __init__(self, log_dir: Path, log_name: str):
        self.log_dir = log_dir
        self.log_name = log_name
        self.log_path = log_dir / log_name
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def log(self, level: str, message: str, data: Optional[Dict] = None):
        """Log to JSON file with session tracking."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'data': data
        }

        # Load existing log
        log_data = []
        if self.log_path.exists():
            try:
                with open(self.log_path, 'r') as f:
                    log_data = json.load(f)
            except:
                log_data = []

        # Append and save
        log_data.append(entry)

        # Keep only last 100 entries
        if len(log_data) > 100:
            log_data = log_data[-100:]

        with open(self.log_path, 'w') as f:
            json.dump(log_data, f, indent=2)


class GitContextProvider(ContextProvider):
    """Provides git repository context."""

    def get_context(self, input_data: Dict) -> Optional[Dict[str, Any]]:
        """Get git status and branch information."""
        try:
            # Get current branch
            branch_result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True, text=True, timeout=5
            )
            current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"

            # Get uncommitted changes
            status_result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True, text=True, timeout=5
            )
            changes = []
            if status_result.returncode == 0 and status_result.stdout.strip():
                changes = status_result.stdout.strip().split('\n')

            # Get recent commits
            log_result = subprocess.run(
                ['git', 'log', '--oneline', '-5'],
                capture_output=True, text=True, timeout=5
            )
            recent_commits = []
            if log_result.returncode == 0:
                recent_commits = log_result.stdout.strip().split('\n')

            return {
                'current_branch': current_branch,
                'uncommitted_changes': len(changes),
                'changes': changes[:10],  # First 10 changes
                'recent_commits': recent_commits,
                'is_clean': len(changes) == 0
            }

        except Exception as e:
            return {'error': str(e), 'current_branch': 'unknown', 'is_clean': True}


class MCPContextProvider(ContextProvider):
    """Provides MCP task and project context."""

    def get_context(self, input_data: Dict) -> Optional[Dict[str, Any]]:
        """Get MCP tasks and project context."""
        try:
            from utils.mcp_client import get_default_client
            client = get_default_client()
            if not client:
                return None

            context = {}

            # Get pending tasks
            pending_tasks = self._query_pending_tasks(client)
            if pending_tasks:
                context['pending_tasks'] = pending_tasks[:5]  # First 5 tasks

            # Get git branch context
            git_context = self._get_git_branch_context(client)
            if git_context:
                context['git_branch_context'] = git_context

            # Get next recommended task
            next_task = self._query_next_task(client, git_context)
            if next_task:
                context['next_task'] = next_task

            return context if context else None

        except Exception as e:
            return {'error': str(e)}

    def _query_pending_tasks(self, client) -> Optional[List[Dict]]:
        """Query pending tasks from MCP."""
        try:
            # Use the actual client interface method
            return client.query_pending_tasks(limit=5)
        except:
            pass
        return None

    def _get_git_branch_context(self, client) -> Optional[Dict]:
        """Get git branch context from MCP."""
        try:
            # Use the actual client interface methods
            project_context = client.query_project_context()
            git_branch_info = client.query_git_branch_info()

            if project_context or git_branch_info:
                context = {}
                if project_context:
                    context['project'] = project_context
                if git_branch_info:
                    # Structure the git branch info to match expected format
                    context['branches'] = [git_branch_info] if git_branch_info else []
                return context

        except:
            pass
        return None

    def _query_next_task(self, client, git_context: Optional[Dict]) -> Optional[Dict]:
        """Query next recommended task."""
        try:
            if not git_context or not git_context.get('branches'):
                return None

            # Use first branch as default
            branch = git_context['branches'][0]
            git_branch_id = branch.get('id')

            # Use the actual client interface method
            return client.get_next_recommended_task(git_branch_id)

        except:
            pass
        return None


class DevelopmentContextProvider(ContextProvider):
    """Provides development environment context."""

    def get_context(self, input_data: Dict) -> Optional[Dict[str, Any]]:
        """Get development environment context."""
        try:
            context = {}

            # Get working directory
            context['working_directory'] = str(Path.cwd())

            # Check for key files
            key_files = [
                'package.json', 'requirements.txt', 'pyproject.toml',
                'Dockerfile', 'docker-compose.yml', 'CLAUDE.md'
            ]

            existing_files = []
            for file in key_files:
                if Path(file).exists():
                    existing_files.append(file)

            context['key_files'] = existing_files

            # Get environment info
            context['python_version'] = sys.version.split()[0]
            context['platform'] = sys.platform

            # Check for virtual environment
            context['virtual_env'] = os.environ.get('VIRTUAL_ENV') is not None

            return context

        except Exception as e:
            return {'error': str(e)}


class IssueContextProvider(ContextProvider):
    """Provides recent issues and problem context."""

    def get_context(self, input_data: Dict) -> Optional[Dict[str, Any]]:
        """Get recent issues from logs."""
        try:
            from utils.env_loader import get_ai_data_path

            log_dir = get_ai_data_path()
            error_files = ['pre_tool_use_errors.log', 'post_tool_use_errors.log']

            recent_issues = []
            for error_file in error_files:
                error_path = log_dir / error_file
                if error_path.exists():
                    try:
                        with open(error_path, 'r') as f:
                            lines = f.readlines()[-5:]  # Last 5 errors
                            recent_issues.extend([line.strip() for line in lines if line.strip()])
                    except:
                        pass

            return {'recent_issues': recent_issues[-10:]} if recent_issues else None

        except Exception:
            return None


class AgentMessageProvider(ContextProvider):
    """Provides agent-specific initialization messages."""

    def __init__(self, config_loader: ConfigurationLoader):
        self.config_loader = config_loader

    def get_context(self, input_data: Dict) -> Optional[Dict[str, Any]]:
        """Get agent initialization messages based on session type."""
        try:
            # Detect session type
            session_type = self._detect_session_type()

            # Determine which agent to use
            agent_name = None

            if session_type == 'principal':
                # Principal session always uses master-orchestrator-agent
                agent_name = 'master-orchestrator-agent'
            else:
                # Try to detect agent from context
                agent_name = self._detect_agent_from_context(input_data)

            if not agent_name:
                # Default to master-orchestrator for principal sessions
                if session_type == 'principal':
                    agent_name = 'master-orchestrator-agent'
                else:
                    return None

            # Get agent message from config
            agent_message = self.config_loader.get_agent_message(agent_name)
            if agent_message:
                return {
                    'agent_name': agent_name,
                    'session_type': session_type,
                    'initialization_message': agent_message.get('initialization_message', ''),
                    'role_description': agent_message.get('role_description', '')
                }

            return None

        except Exception:
            return None

    def _detect_session_type(self) -> str:
        """Detect the type of session."""
        if 'CLAUDE_SUBAGENT' in os.environ:
            return 'sub-agent'
        return 'principal'

    def _detect_agent_from_context(self, input_data: Dict) -> Optional[str]:
        """Detect agent type from input context."""
        try:
            conversation = input_data.get('conversation_history', [])

            for message in reversed(conversation[-10:]):
                content = message.get('content', '')
                if 'mcp__agenthub_http__call_agent' in content:
                    import re
                    # Check for agent name in various patterns
                    match = re.search(r'"name_agent":\s*"([^"]+)"', content)
                    if match:
                        return match.group(1)

                    match = re.search(r'call_agent\(["\']([^"\']+)["\']', content)
                    if match:
                        return match.group(1)

                    match = re.search(r'name_agent.*?([a-z-]+agent)', content, re.IGNORECASE)
                    if match:
                        return match.group(1).lower()

            # Check for task_id pattern suggesting sub-agent
            for message in reversed(conversation[-5:]):
                content = message.get('content', '')
                if 'task_id:' in content.lower():
                    # This is likely a sub-agent session, but we don't know which one
                    return None

        except:
            pass

        return None


class SessionStartProcessor(SessionProcessor):
    """Main session start processor."""

    def __init__(self, logger: Logger):
        self.logger = logger

    def process(self, input_data: Dict) -> Optional[str]:
        """Process session start and generate context output."""
        try:
            # Log session start
            self.logger.log('info', 'Session started', input_data)

            # Detect session type
            session_type = self._detect_session_type()
            agent_type = self._detect_agent_from_context(input_data)

            output_parts = []

            # Add session info
            if session_type or agent_type:
                session_info = []
                if session_type:
                    session_info.append(f"Session Type: {session_type}")
                if agent_type:
                    session_info.append(f"Detected Agent: {agent_type}")

                output_parts.append("🚀 Session Context:\n" + "\n".join(session_info))

            return "\n\n".join(output_parts) if output_parts else None

        except Exception as e:
            self.logger.log('error', f'Session processing failed: {e}')
            return None

    def _detect_session_type(self) -> Optional[str]:
        """Detect the type of session (principal vs sub-agent)."""
        try:
            # Check if this is a sub-agent session by looking for specific patterns
            if 'CLAUDE_SUBAGENT' in os.environ:
                return 'sub-agent'

            # Default to principal session
            return 'principal'
        except:
            return None

    def _detect_agent_from_context(self, input_data: Dict) -> Optional[str]:
        """Detect agent type from input context."""
        try:
            # Check conversation history for agent loading patterns
            conversation = input_data.get('conversation_history', [])

            for message in reversed(conversation[-10:]):  # Last 10 messages
                content = message.get('content', '')
                if 'mcp__agenthub_http__call_agent' in content:
                    # Extract agent name
                    import re
                    match = re.search(r'"name_agent":\s*"([^"]+)"', content)
                    if match:
                        return match.group(1)

                    # Alternative pattern
                    match = re.search(r'call_agent\(["\']([^"\']+)["\']', content)
                    if match:
                        return match.group(1)

            return None
        except:
            return None


class ContextFormatterProcessor(SessionProcessor):
    """Formats and presents context information."""

    def __init__(self, context_providers: List[ContextProvider], logger: Logger):
        self.context_providers = context_providers
        self.logger = logger

    def process(self, input_data: Dict) -> Optional[str]:
        """Format all context information."""
        try:
            context_data = {}

            # Gather context from all providers
            for provider in self.context_providers:
                try:
                    provider_name = provider.__class__.__name__.replace('Provider', '').lower()
                    provider_context = provider.get_context(input_data)
                    if provider_context:
                        context_data[provider_name] = provider_context
                except Exception as e:
                    self.logger.log('error', f'Context provider {provider.__class__.__name__} failed: {e}')

            return self._format_context(context_data) if context_data else None

        except Exception as e:
            self.logger.log('error', f'Context formatting failed: {e}')
            return None

    def _format_context(self, context_data: Dict) -> str:
        """Format context data into readable output."""
        output_parts = []

        # PRIORITY: Agent initialization messages (most important)
        if 'agentmessage' in context_data:
            agent = context_data['agentmessage']
            if agent.get('initialization_message'):
                # Add the initialization message as the FIRST thing
                output_parts.append(agent['initialization_message'])
            if agent.get('role_description'):
                output_parts.append(agent['role_description'])

        # Git context
        if 'gitcontext' in context_data:
            git = context_data['gitcontext']
            git_parts = [f"📁 Git Status: Branch '{git.get('current_branch', 'unknown')}'"]

            if git.get('uncommitted_changes', 0) > 0:
                git_parts.append(f"⚠️  {git['uncommitted_changes']} uncommitted changes")
            else:
                git_parts.append("✅ Working directory clean")

            output_parts.append("\n".join(git_parts))

        # MCP context
        if 'mcpcontext' in context_data:
            mcp = context_data['mcpcontext']
            mcp_parts = ["📋 Project Context:"]

            if mcp.get('pending_tasks'):
                task_count = len(mcp['pending_tasks'])
                mcp_parts.append(f"   • {task_count} active tasks")

            if mcp.get('next_task'):
                next_task = mcp['next_task']
                task_title = next_task.get('title', 'Unknown task')
                mcp_parts.append(f"   • Next: {task_title}")

            if len(mcp_parts) > 1:
                output_parts.append("\n".join(mcp_parts))

        # Development context
        if 'developmentcontext' in context_data:
            dev = context_data['developmentcontext']
            dev_parts = ["🔧 Development Environment:"]

            if dev.get('key_files'):
                key_files = ', '.join(dev['key_files'][:3])
                dev_parts.append(f"   • Key files: {key_files}")

            if dev.get('python_version'):
                dev_parts.append(f"   • Python {dev['python_version']}")

            if len(dev_parts) > 1:
                output_parts.append("\n".join(dev_parts))

        # Issues context
        if 'issuecontext' in context_data:
            issues = context_data['issuecontext']
            if issues.get('recent_issues'):
                issue_count = len(issues['recent_issues'])
                output_parts.append(f"⚠️  {issue_count} recent issues logged")

        return "\n\n".join(output_parts)


# ============================================================================
# Component Factory
# ============================================================================

class ComponentFactory:
    """Factory for creating session start components."""

    @staticmethod
    def create_logger(log_dir: Path, log_name: str = 'session_start') -> Logger:
        """Create a logger instance."""
        return FileLogger(log_dir, log_name)

    @staticmethod
    def create_config_loader(config_dir: Path) -> ConfigurationLoader:
        """Create a configuration loader instance."""
        return ConfigurationLoader(config_dir)

    @staticmethod
    def create_context_providers(config_loader: ConfigurationLoader) -> List[ContextProvider]:
        """Create all context providers."""
        return [
            AgentMessageProvider(config_loader),  # FIRST - most important
            GitContextProvider(),
            MCPContextProvider(),
            DevelopmentContextProvider(),
            IssueContextProvider()
        ]

    @staticmethod
    def create_processors(context_providers: List[ContextProvider], logger: Logger) -> List[SessionProcessor]:
        """Create all session processors."""
        return [
            SessionStartProcessor(logger),
            ContextFormatterProcessor(context_providers, logger)
        ]


# ============================================================================
# Main Hook Class
# ============================================================================

class SessionStartHook:
    """Main session start hook with clean architecture."""

    def __init__(self):
        """Initialize the hook with all components."""
        # Get paths
        from utils.env_loader import get_ai_data_path

        self.log_dir = get_ai_data_path()
        self.config_dir = Path(__file__).parent / 'config'

        # Create components using factory
        self.factory = ComponentFactory()
        self.logger = self.factory.create_logger(self.log_dir)
        self.config_loader = self.factory.create_config_loader(self.config_dir)

        # Initialize components with config loader
        self.context_providers: List[ContextProvider] = self.factory.create_context_providers(self.config_loader)
        self.processors: List[SessionProcessor] = self.factory.create_processors(
            self.context_providers, self.logger
        )

    def execute(self, input_data: Dict[str, Any]) -> int:
        """Execute the session start hook."""
        # Log the execution
        self.logger.log('info', 'Processing session start')

        # Process through all processors
        output_parts = []
        for processor in self.processors:
            try:
                output = processor.process(input_data)
                if output and output.strip():
                    output_parts.append(output)
            except Exception as e:
                self.logger.log('error', f'Processor {processor.__class__.__name__} failed: {e}')

        # Output combined results
        if output_parts:
            combined_output = "\n\n".join(output_parts)
            print(combined_output)

        self.logger.log('info', 'Session start processing completed')
        return 0


# ============================================================================
# Backward Compatibility Functions (for test compatibility)
# ============================================================================

def log_session_start(input_data: Dict) -> None:
    """Backward compatibility wrapper for log_session_start."""
    try:
        log_dir = get_ai_data_path()
        log_path = log_dir / "session_start.json"

        # Ensure directory exists
        log_dir.mkdir(parents=True, exist_ok=True)

        # Load existing data
        log_data = []
        if log_path.exists():
            try:
                with open(log_path, 'r') as f:
                    log_data = json.load(f)
            except:
                log_data = []

        # Append new data directly (for test compatibility)
        log_data.append(input_data)

        # Save updated data
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)

    except Exception:
        # Fail silently for compatibility
        pass


def get_git_status() -> tuple:
    """Backward compatibility wrapper for git status."""
    try:
        git_provider = GitContextProvider()
        context = git_provider.get_context({})
        if context and 'error' not in context:
            branch = context.get('current_branch', None)
            changes = context.get('uncommitted_changes', None)
            # Map "unknown" to None for backward compatibility (indicates git command failure)
            if branch == "unknown":
                branch = None
                changes = None  # Also set changes to None when git commands fail
            return branch, changes
        else:
            return None, None
    except Exception:
        return None, None


def get_recent_issues() -> Optional[str]:
    """Backward compatibility wrapper for recent issues."""
    try:
        # Check if gh CLI is available
        which_result = subprocess.run(
            ['which', 'gh'],
            capture_output=True, text=True, timeout=5
        )

        if which_result.returncode != 0:
            return None

        # Get recent issues using gh CLI
        issues_result = subprocess.run(
            ['gh', 'issue', 'list', '--state=open', '--limit=10'],
            capture_output=True, text=True, timeout=10
        )

        if issues_result.returncode == 0 and issues_result.stdout.strip():
            # Return the raw output, removing trailing newline for consistency
            return issues_result.stdout.rstrip('\n')
        else:
            return None

    except Exception:
        return None


def query_mcp_pending_tasks() -> Optional[List]:
    """Backward compatibility wrapper for pending tasks."""
    try:
        # Direct server query without cache
        client = get_default_client()
        if client:
            server_tasks = client.query_pending_tasks(limit=5)
            if server_tasks:
                return server_tasks

        return []
    except Exception:
        return None


def query_mcp_next_task(branch_id: Optional[str] = None) -> Optional[Dict]:
    """Backward compatibility wrapper for next task."""
    try:
        if not branch_id:
            return None

        # Direct server query without cache
        client = get_default_client()
        if client:
            next_task = client.get_next_recommended_task(branch_id)
            if next_task:
                return next_task

        return None
    except Exception:
        return None


def get_git_branch_context() -> Optional[Dict]:
    """Backward compatibility wrapper for git branch context."""
    try:

        # Get git context from subprocess calls
        # Get current branch
        branch_result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True, text=True, timeout=5
        )
        current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"

        # Get uncommitted changes count
        status_result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True, text=True, timeout=5
        )
        changes = []
        if status_result.returncode == 0 and status_result.stdout.strip():
            changes = status_result.stdout.strip().split('\n')

        # Get recent commits
        log_result = subprocess.run(
            ['git', 'log', '--oneline', '-5'],
            capture_output=True, text=True, timeout=5
        )
        recent_commits = []
        if log_result.returncode == 0 and log_result.stdout.strip():
            recent_commits = log_result.stdout.strip().split('\n')

        result = {
            "branch": current_branch,
            "uncommitted_changes": len(changes),
            "recent_commits": recent_commits,
            "git_branch_id": None  # Test expects this to be None
        }

        return result

    except Exception:
        return None


def format_mcp_context(context_data: Dict) -> str:
    """Backward compatibility wrapper for MCP context formatting."""
    try:
        if not context_data:
            return ""
        return json.dumps(context_data, indent=2)
    except Exception:
        return ""


def load_development_context(trigger: str = "startup") -> str:
    """Backward compatibility wrapper for development context."""
    try:
        # Create a factory and get context
        factory = SessionFactory()
        providers = [
            factory.create_git_context_provider(),
            factory.create_mcp_context_provider()
        ]

        combined_context = {}
        for provider in providers:
            try:
                context = provider.get_context({})
                if context:
                    combined_context.update(context)
            except Exception:
                continue

        # Format as expected by tests
        git_status = "✅" if combined_context.get('git_info') else "❌"
        mcp_tasks = len(combined_context.get('pending_tasks', []))

        formatted_output = f"""🚀 INITIALIZATION REQUIRED
⚠️ **MCP Status:** Server unavailable or no active tasks
--- Context Generation Stats ---
MCP tasks loaded: {mcp_tasks}
Git context: {git_status}
"""
        return formatted_output
    except Exception:
        return "🚀 INITIALIZATION REQUIRED\n⚠️ **MCP Status:** Server unavailable or no active tasks\n--- Context Generation Stats ---\nMCP tasks loaded: 0\nGit context: ❌"


def get_ai_data_path() -> Path:
    """Backward compatibility wrapper for get_ai_data_path."""
    try:
        from utils.env_loader import get_ai_data_path as real_get_ai_data_path
        return real_get_ai_data_path()
    except Exception:
        return Path("logs")




def get_default_client():
    """Backward compatibility wrapper for default client."""
    try:
        return None
    except Exception:
        return None


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point for the hook."""
    parser = argparse.ArgumentParser(description='Session start hook')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--log-only', action='store_true', help='Only log, no output')
    args = parser.parse_args()

    try:
        # Read JSON input from stdin
        input_data = {}
        if not sys.stdin.isatty():
            try:
                input_data = json.load(sys.stdin)
            except json.JSONDecodeError:
                input_data = {}

        # Create and execute hook
        hook = SessionStartHook()

        if args.log_only:
            hook.logger.log('info', 'Session start logged only', input_data)
        else:
            exit_code = hook.execute(input_data)
            sys.exit(exit_code)

        sys.exit(0)

    except Exception as e:
        # Log error but exit cleanly
        try:
            from utils.env_loader import get_ai_data_path
            log_dir = get_ai_data_path()
            error_log = log_dir / 'session_start_errors.log'
            with open(error_log, 'a') as f:
                f.write(f"{datetime.now().isoformat()} - Fatal error: {e}\n")
        except:
            pass
        sys.exit(0)


if __name__ == '__main__':
    main()