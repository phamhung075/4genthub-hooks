#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# ///

"""
Refactored User prompt submit hook with factory pattern and clean architecture.

This hook runs when a user submits a prompt and provides:
1. Prompt validation and security checking
2. Session data management and tracking
3. Agent name generation
4. Context injection for prompts
5. Logging and audit trail

Refactored with:
- Factory pattern for component creation
- Single Responsibility Principle
- Dependency injection
- Clean error handling
- Centralized configuration
"""

import json
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from abc import ABC, abstractmethod

# Add hooks directory to path
sys.path.insert(0, str(Path(__file__).parent))


# ============================================================================
# Abstract Base Classes
# ============================================================================

class Validator(ABC):
    """Base validator interface."""

    @abstractmethod
    def validate(self, prompt: str, session_data: Dict) -> Tuple[bool, Optional[str]]:
        """
        Validate the prompt.

        Returns:
            Tuple of (is_valid, error_message)
        """
        pass


class Processor(ABC):
    """Base processor interface."""

    @abstractmethod
    def process(self, prompt: str, session_data: Dict) -> Optional[str]:
        """
        Process the prompt and return any context.

        Returns:
            Optional context string
        """
        pass


class SessionManager(ABC):
    """Base session manager interface."""

    @abstractmethod
    def load_session(self, session_id: str) -> Dict[str, Any]:
        """Load session data."""
        pass

    @abstractmethod
    def save_session(self, session_id: str, session_data: Dict):
        """Save session data."""
        pass


class Logger(ABC):
    """Abstract logger interface."""

    @abstractmethod
    def log(self, level: str, message: str, data: Optional[Dict] = None):
        """Log a message with optional data."""
        pass


# ============================================================================
# Component Implementations
# ============================================================================

class FileLogger(Logger):
    """File-based logger implementation."""

    def __init__(self, log_dir: Path, log_name: str):
        self.log_dir = log_dir
        self.log_name = log_name
        self.log_path = log_dir / f"{log_name}.json"
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def log(self, level: str, message: str, data: Optional[Dict] = None):
        """Log to JSON file."""
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


class JSONSessionManager(SessionManager):
    """JSON-based session manager."""

    def __init__(self, sessions_dir: Path):
        self.sessions_dir = sessions_dir
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def load_session(self, session_id: str) -> Dict[str, Any]:
        """Load session data from JSON file."""
        session_file = self.sessions_dir / f"{session_id}.json"

        if session_file.exists():
            try:
                with open(session_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, ValueError):
                pass

        return {"session_id": session_id, "prompts": []}

    def save_session(self, session_id: str, session_data: Dict):
        """Save session data to JSON file."""
        session_file = self.sessions_dir / f"{session_id}.json"
        try:
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
        except Exception:
            # Silently fail if we can't write
            pass


class SecurityValidator(Validator):
    """Validates prompts for security issues."""

    def __init__(self):
        self.blocked_patterns = [
            # Add dangerous patterns here
            ('rm -rf /', 'Dangerous filesystem command detected'),
            ('sudo rm', 'Dangerous sudo command detected'),
            # Add more patterns as needed
        ]

    def validate(self, prompt: str, session_data: Dict) -> Tuple[bool, Optional[str]]:
        """Validate prompt for security violations."""
        prompt_lower = prompt.lower()

        for pattern, reason in self.blocked_patterns:
            if pattern.lower() in prompt_lower:
                return False, reason

        return True, None


class ContentValidator(Validator):
    """Validates prompts for content policy violations."""

    def validate(self, prompt: str, session_data: Dict) -> Tuple[bool, Optional[str]]:
        """Validate prompt content."""
        # Add content validation logic here
        # For now, just check length
        if len(prompt.strip()) == 0:
            return False, "Empty prompt not allowed"

        # Could add more sophisticated content checks
        return True, None


class PromptLogger(Processor):
    """Logs prompts for audit trail."""

    def __init__(self, logger: Logger):
        self.logger = logger

    def process(self, prompt: str, session_data: Dict) -> Optional[str]:
        """Log the prompt submission."""
        session_id = session_data.get('session_id', 'unknown')

        self.logger.log('info', f'Prompt submitted for session {session_id}', {
            'session_id': session_id,
            'prompt_length': len(prompt),
            'prompt_preview': prompt[:100] + '...' if len(prompt) > 100 else prompt
        })

        return None  # No context to add


class SessionTracker(Processor):
    """Tracks session data and prompts."""

    def __init__(self, session_manager: SessionManager, logger: Logger, store_last_prompt: bool = False):
        self.session_manager = session_manager
        self.logger = logger
        self.store_last_prompt = store_last_prompt

    def process(self, prompt: str, session_data: Dict) -> Optional[str]:
        """Update session tracking data."""
        try:
            session_id = session_data.get('session_id', 'unknown')

            # Update the session_data that was passed in
            if 'prompts' not in session_data:
                session_data['prompts'] = []

            # Add the new prompt to session_data
            if self.store_last_prompt:
                session_data['prompts'].append(prompt)
                session_data['last_prompt'] = prompt
                session_data['last_updated'] = datetime.now().isoformat()

                # Keep only last 50 prompts
                if len(session_data['prompts']) > 50:
                    session_data['prompts'] = session_data['prompts'][-50:]

                self.logger.log('info', f'Stored prompt for session {session_id}', {
                    'prompt_length': len(prompt),
                    'total_prompts': len(session_data['prompts'])
                })

            return None  # No context to add

        except Exception as e:
            self.logger.log('error', f'Session tracking failed: {e}')
            return None


class AgentNameGenerator(Processor):
    """Generates agent names for sessions."""

    def __init__(self, logger: Logger, enabled: bool = False):
        self.logger = logger
        self.enabled = enabled

    def process(self, prompt: str, session_data: Dict) -> Optional[str]:
        """Generate agent name if requested and not present."""
        if not self.enabled:
            return None

        session_id = session_data.get('session_id', 'unknown')

        # Check if agent name already exists
        if session_data.get('agent_name'):
            return None

        try:
            agent_name = self._generate_name()
            if agent_name:
                session_data['agent_name'] = agent_name
                self.logger.log('info', f'Generated agent name: {agent_name}', {
                    'session_id': session_id,
                    'agent_name': agent_name
                })
                return f"🤖 Agent name: {agent_name}"

        except Exception as e:
            self.logger.log('error', f'Agent name generation failed: {e}')

        return None

    def _generate_name(self) -> Optional[str]:
        """Generate an agent name using LLM services."""
        # Try Ollama first (local)
        try:
            result = subprocess.run(
                ["uv", "run", ".claude/hooks/utils/llm/ollama.py", "--agent-name"],
                capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0 and result.stdout.strip():
                agent_name = result.stdout.strip()
                if self._validate_name(agent_name):
                    return agent_name
        except:
            pass

        # Try Anthropic as fallback
        try:
            result = subprocess.run(
                ["uv", "run", ".claude/hooks/utils/llm/anth.py", "--agent-name"],
                capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0 and result.stdout.strip():
                agent_name = result.stdout.strip()
                if self._validate_name(agent_name):
                    return agent_name
        except:
            pass

        return None

    def _validate_name(self, name: str) -> bool:
        """Validate the generated agent name."""
        return (len(name.split()) == 1 and
                name.isalnum() and
                3 <= len(name) <= 20)


class ContextInjector(Processor):
    """Injects context information into prompts."""

    def __init__(self, logger: Logger):
        self.logger = logger

    def process(self, prompt: str, session_data: Dict) -> Optional[str]:
        """Add contextual information to the prompt."""
        try:
            context_parts = []

            # Add timestamp
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            context_parts.append(f"⏰ Current time: {current_time}")

            # Add session info
            session_id = session_data.get('session_id', 'unknown')
            prompt_count = len(session_data.get('prompts', [])) + 1  # +1 for current prompt
            context_parts.append(f"📝 Session: {session_id} (prompt #{prompt_count})")

            # Add working directory
            cwd = str(Path.cwd())
            context_parts.append(f"📁 Working directory: {cwd}")

            return "\n".join(context_parts)

        except Exception as e:
            self.logger.log('error', f'Context injection failed: {e}')
            return None


# ============================================================================
# Component Factory
# ============================================================================

class ComponentFactory:
    """Factory for creating user prompt submit components."""

    @staticmethod
    def create_logger(log_dir: Path, log_name: str = 'user_prompt_submit') -> Logger:
        """Create a logger instance."""
        return FileLogger(log_dir, log_name)

    @staticmethod
    def create_session_manager(sessions_dir: Path) -> SessionManager:
        """Create session manager."""
        return JSONSessionManager(sessions_dir)

    @staticmethod
    def create_validators() -> List[Validator]:
        """Create all validators."""
        return [
            SecurityValidator(),
            ContentValidator()
        ]

    @staticmethod
    def create_processors(session_manager: SessionManager, logger: Logger,
                         enable_agent_name: bool = False, store_last_prompt: bool = False) -> List[Processor]:
        """Create all processors."""
        return [
            PromptLogger(logger),
            SessionTracker(session_manager, logger, store_last_prompt),
            AgentNameGenerator(logger, enable_agent_name),
            ContextInjector(logger)
        ]


# ============================================================================
# Main Hook Class
# ============================================================================

class UserPromptSubmitHook:
    """Main user prompt submit hook with clean architecture."""

    def __init__(self, enable_validation: bool = False,
                 log_only: bool = False, enable_agent_name: bool = False,
                 store_last_prompt: bool = False):
        """Initialize the hook with all components."""
        # Get paths
        from utils.env_loader import get_ai_data_path

        self.log_dir = get_ai_data_path()
        self.sessions_dir = Path(".claude/data/sessions")

        # Configuration
        self.enable_validation = enable_validation
        self.log_only = log_only
        self.enable_agent_name = enable_agent_name
        self.store_last_prompt = store_last_prompt

        # Create components using factory
        self.factory = ComponentFactory()
        self.logger = self.factory.create_logger(self.log_dir)
        self.session_manager = self.factory.create_session_manager(self.sessions_dir)

        # Initialize components
        self.validators: List[Validator] = self.factory.create_validators()
        self.processors: List[Processor] = self.factory.create_processors(
            self.session_manager, self.logger, self.enable_agent_name, self.store_last_prompt
        )

    def execute(self, input_data: Dict[str, Any]) -> int:
        """Execute the user prompt submit hook."""
        session_id = input_data.get('session_id', 'unknown')
        prompt = input_data.get('prompt', '')

        # Log the execution
        self.logger.log('info', f'Processing prompt submission for session {session_id}')

        # Load session data
        session_data = self.session_manager.load_session(session_id)

        # Run validators if enabled
        if self.enable_validation and not self.log_only:
            for validator in self.validators:
                try:
                    is_valid, error_message = validator.validate(prompt, session_data)
                    if not is_valid and error_message:
                        print(f"Prompt blocked: {error_message}", file=sys.stderr)
                        self.logger.log('warning', f'Prompt validation failed: {validator.__class__.__name__}',
                                      {'session_id': session_id, 'error': error_message})
                        return 2  # Block prompt
                except Exception as e:
                    self.logger.log('error', f'Validator {validator.__class__.__name__} failed: {e}')

        # Run processors for logging and context
        context_parts = []
        for processor in self.processors:
            try:
                context = processor.process(prompt, session_data)
                if context and context.strip():
                    context_parts.append(context)
            except Exception as e:
                self.logger.log('error', f'Processor {processor.__class__.__name__} failed: {e}')

        # Output context if any
        if context_parts and not self.log_only:
            combined_context = "\n\n".join(context_parts)
            print(combined_context)

        # Save updated session data
        if self.store_last_prompt or self.enable_agent_name:
            self.session_manager.save_session(session_id, session_data)

        self.logger.log('info', 'Prompt processing completed successfully')
        return 0


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point for the hook."""
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description='User prompt submit hook')
        parser.add_argument('--validate', action='store_true',
                          help='Enable prompt validation')
        parser.add_argument('--log-only', action='store_true',
                          help='Only log prompts, no validation or blocking')
        parser.add_argument('--store-last-prompt', action='store_true',
                          help='Store the last prompt for status line display')
        parser.add_argument('--name-agent', action='store_true',
                          help='Generate an agent name for the session')
        args = parser.parse_args()

        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        # Create and execute hook
        hook = UserPromptSubmitHook(
            enable_validation=args.validate,
            log_only=args.log_only,
            enable_agent_name=args.name_agent,
            store_last_prompt=args.store_last_prompt
        )

        exit_code = hook.execute(input_data)
        sys.exit(exit_code)

    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception as e:
        # Log error but exit cleanly
        try:
            from utils.env_loader import get_ai_data_path
            log_dir = get_ai_data_path()
            error_log = log_dir / 'user_prompt_submit_errors.log'
            with open(error_log, 'a') as f:
                f.write(f"{datetime.now().isoformat()} - Fatal error: {e}\n")
        except:
            pass
        sys.exit(0)


if __name__ == '__main__':
    main()