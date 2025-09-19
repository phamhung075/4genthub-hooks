#!/usr/bin/env python3
"""
Utility script to generate inline Python commands for Claude hooks.

This script creates the inline Python commands that replace the wrapper-based
approach, providing a solution that works with symlinked .claude directories
from any subdirectory without requiring external wrapper files.

Usage:
    python3 generate_inline_commands.py <hook_name> [args...]

Examples:
    python3 generate_inline_commands.py status_line_mcp.py
    python3 generate_inline_commands.py user_prompt_submit.py --log-only --store-last-prompt

The generated command can be used directly in Claude Code settings.json.
"""

import sys
import shlex


def generate_inline_command(hook_name, *args):
    """
    Generate an inline Python command for executing a Claude hook.

    Args:
        hook_name: Name of the hook script to execute
        *args: Additional arguments to pass to the hook

    Returns:
        Complete command string suitable for use in settings.json
    """
    # Core inline Python logic that:
    # 1. Finds project root by searching for marker files
    # 2. Resolves .claude symlink if it exists
    # 3. Executes the hook with proper arguments
    inline_logic = (
        "import os,sys,subprocess;from pathlib import Path;"
        "current=Path.cwd().resolve();"
        "paths=[current]+list(current.parents);"
        "root=next((p for p in paths if any((p/m).exists() for m in ['CLAUDE.md','.git','package.json']) and (p/'.claude').exists()), None);"
        "claude_dir=root/'.claude' if root else None;"
        "real_claude=claude_dir.resolve() if claude_dir and claude_dir.is_symlink() else claude_dir;"
        "hook_path=real_claude/'hooks'/'execute_hook.py' if real_claude else None;"
        "subprocess.run([sys.executable, str(hook_path)] + sys.argv[1:]) if hook_path and hook_path.exists() else sys.exit(1)"
    )

    # Build the complete command with hook name and arguments
    hook_args = [hook_name] + list(args)
    hook_args_str = ' '.join(shlex.quote(arg) for arg in hook_args)

    # Return the complete command
    return f'python3 -c "{inline_logic}" {hook_args_str}'


def generate_for_settings_json(hook_name, *args):
    """
    Generate command string properly escaped for use in JSON settings.

    Args:
        hook_name: Name of the hook script to execute
        *args: Additional arguments to pass to the hook

    Returns:
        JSON-escaped command string for settings.json
    """
    command = generate_inline_command(hook_name, *args)
    # Escape quotes for JSON
    return command.replace('"', '\\"')


def main():
    """Main function for command-line usage."""
    if len(sys.argv) < 2:
        print("Usage: python3 generate_inline_commands.py <hook_name> [args...]")
        print()
        print("Examples:")
        print("  python3 generate_inline_commands.py status_line_mcp.py")
        print("  python3 generate_inline_commands.py user_prompt_submit.py --log-only")
        print()
        print("Options:")
        print("  --json    Output JSON-escaped version for settings.json")
        sys.exit(1)

    # Check for JSON output flag
    if "--json" in sys.argv:
        sys.argv.remove("--json")
        json_output = True
    else:
        json_output = False

    hook_name = sys.argv[1]
    hook_args = sys.argv[2:] if len(sys.argv) > 2 else []

    if json_output:
        command = generate_for_settings_json(hook_name, *hook_args)
        print(f'"command": "{command}"')
    else:
        command = generate_inline_command(hook_name, *hook_args)
        print(command)


if __name__ == "__main__":
    main()