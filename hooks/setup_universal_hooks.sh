#!/bin/bash
# Setup Universal Hook Links for Claude Code Projects
#
# This script creates the necessary files to enable universal hook execution
# that works with symlinked .claude directories across all projects.
#
# Usage:
#   ./setup_universal_hooks.sh [target_project_dir]
#
# If no target directory is provided, it sets up links in the current project.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_HOOKS_DIR="$SCRIPT_DIR"

# Target directory - default to current project if not specified
if [[ $# -gt 0 ]]; then
    TARGET_PROJECT="$1"
    if [[ ! -d "$TARGET_PROJECT" ]]; then
        echo "Error: Target directory does not exist: $TARGET_PROJECT" >&2
        exit 1
    fi
else
    # Find current project root
    TARGET_PROJECT="$PWD"
    while [[ "$TARGET_PROJECT" != "/" ]]; do
        if [[ -f "$TARGET_PROJECT/CLAUDE.md" ]] || [[ -d "$TARGET_PROJECT/.git" ]]; then
            break
        fi
        TARGET_PROJECT="$(dirname "$TARGET_PROJECT")"
    done

    if [[ "$TARGET_PROJECT" == "/" ]]; then
        echo "Error: Could not find project root (no CLAUDE.md or .git found)" >&2
        exit 1
    fi
fi

TARGET_CLAUDE_DIR="$TARGET_PROJECT/.claude"
TARGET_HOOKS_DIR="$TARGET_CLAUDE_DIR/hooks"

echo "Setting up universal hooks for project: $TARGET_PROJECT"
echo "Source hooks directory: $SOURCE_HOOKS_DIR"
echo "Target .claude directory: $TARGET_CLAUDE_DIR"

# Create .claude directory if it doesn't exist
if [[ ! -d "$TARGET_CLAUDE_DIR" ]]; then
    echo "Creating .claude directory..."
    mkdir -p "$TARGET_CLAUDE_DIR"
fi

# Create hooks directory if it doesn't exist
if [[ ! -d "$TARGET_HOOKS_DIR" ]]; then
    echo "Creating hooks directory..."
    mkdir -p "$TARGET_HOOKS_DIR"
fi

# Copy the universal hook executor
echo "Copying universal hook executor..."
cp "$SOURCE_HOOKS_DIR/claude_hook_exec" "$TARGET_HOOKS_DIR/"
chmod +x "$TARGET_HOOKS_DIR/claude_hook_exec"

# Copy or create settings.json template if it doesn't exist
if [[ ! -f "$TARGET_CLAUDE_DIR/settings.json" ]]; then
    echo "Creating settings.json template..."
    cp "$SOURCE_HOOKS_DIR/../settings.json" "$TARGET_CLAUDE_DIR/"
else
    echo "settings.json already exists - not overwriting"
    echo "To use the universal hooks, update your settings.json commands to use:"
    echo "  ./.claude/hooks/claude_hook_exec <hook_name> [args...]"
    echo "instead of:"
    echo "  python3 ./.claude/hooks/execute_hook.py <hook_name> [args...]"
fi

# If target is different from source, create symlinks to actual hooks
if [[ "$TARGET_HOOKS_DIR" != "$SOURCE_HOOKS_DIR" ]]; then
    echo "Creating symlinks to hook files..."

    # Essential hook files to link
    HOOK_FILES=(
        "execute_hook.py"
        "session_start.py"
        "user_prompt_submit.py"
        "pre_tool_use.py"
        "post_tool_use.py"
        "notification.py"
        "stop.py"
        "subagent_stop.py"
        "pre_compact.py"
    )

    for hook_file in "${HOOK_FILES[@]}"; do
        if [[ -f "$SOURCE_HOOKS_DIR/$hook_file" ]]; then
            if [[ ! -f "$TARGET_HOOKS_DIR/$hook_file" ]]; then
                echo "  Linking $hook_file..."
                ln -s "$SOURCE_HOOKS_DIR/$hook_file" "$TARGET_HOOKS_DIR/$hook_file"
            else
                echo "  $hook_file already exists - skipping"
            fi
        fi
    done

    # Link utilities directory if it exists
    if [[ -d "$SOURCE_HOOKS_DIR/utils" ]] && [[ ! -d "$TARGET_HOOKS_DIR/utils" ]]; then
        echo "  Linking utils directory..."
        ln -s "$SOURCE_HOOKS_DIR/utils" "$TARGET_HOOKS_DIR/utils"
    fi

    # Link status_lines directory if it exists
    if [[ -d "$SOURCE_HOOKS_DIR/../status_lines" ]] && [[ ! -d "$TARGET_CLAUDE_DIR/status_lines" ]]; then
        echo "  Linking status_lines directory..."
        ln -s "$SOURCE_HOOKS_DIR/../status_lines" "$TARGET_CLAUDE_DIR/status_lines"
    fi
fi

echo ""
echo "✅ Universal hooks setup complete!"
echo ""
echo "The universal hook system is now ready. Key benefits:"
echo "  • Works with symlinked .claude directories"
echo "  • No need to modify settings.json for different projects"
echo "  • Consistent hook execution across all project subdirectories"
echo ""
echo "To test, try running:"
echo "  $TARGET_HOOKS_DIR/claude_hook_exec session_start.py --help"
echo ""
echo "Your settings.json should use commands like:"
echo "  ./.claude/hooks/claude_hook_exec <hook_name> [args...]"