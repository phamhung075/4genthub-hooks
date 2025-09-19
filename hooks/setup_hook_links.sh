#!/bin/bash
#
# Setup script to create symbolic links for hooks in subdirectories
# This allows hooks to be found when Claude is run from any directory
#

# Find project root
find_project_root() {
    local current="$PWD"

    while [ "$current" != "/" ]; do
        if [ -f "$current/CLAUDE.md" ] || [ -d "$current/.git" ]; then
            if [ -d "$current/.claude/hooks" ]; then
                echo "$current"
                return 0
            fi
        fi
        current=$(dirname "$current")
    done

    # Fallback to known path
    if [ -d "/home/daihungpham/__projects__/4genthub/.claude/hooks" ]; then
        echo "/home/daihungpham/__projects__/4genthub"
        return 0
    fi

    return 1
}

PROJECT_ROOT=$(find_project_root)
if [ -z "$PROJECT_ROOT" ]; then
    echo "Error: Could not find project root"
    exit 1
fi

echo "Project root: $PROJECT_ROOT"

# List of directories where Claude might be run from
SUBDIRS=(
    "agenthub_main"
    "agenthub_main/src"
    "agenthub-frontend"
    "docker-system"
    "docker-system/docker"
)

# List of hooks that need to be accessible
HOOKS=(
    "pre_tool_use.py"
    "post_tool_use.py"
    "session_start.py"
    "user_prompt_submit.py"
    "stop.py"
)

# Create .claude/hooks symlink in each subdirectory
for dir in "${SUBDIRS[@]}"; do
    target_dir="$PROJECT_ROOT/$dir"

    if [ -d "$target_dir" ]; then
        echo "Setting up hooks for: $target_dir"

        # Create .claude directory if it doesn't exist
        mkdir -p "$target_dir/.claude"

        # Remove existing hooks link/directory if it exists
        if [ -e "$target_dir/.claude/hooks" ]; then
            rm -rf "$target_dir/.claude/hooks"
        fi

        # Create symlink to the actual hooks directory
        ln -s "$PROJECT_ROOT/.claude/hooks" "$target_dir/.claude/hooks"

        echo "  ✓ Created symlink: $target_dir/.claude/hooks -> $PROJECT_ROOT/.claude/hooks"
    else
        echo "  ⚠ Directory not found: $target_dir"
    fi
done

echo ""
echo "✅ Hook links setup complete!"
echo ""
echo "You can now run Claude from any of these directories:"
for dir in "${SUBDIRS[@]}"; do
    if [ -d "$PROJECT_ROOT/$dir" ]; then
        echo "  - $PROJECT_ROOT/$dir"
    fi
done