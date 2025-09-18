#!/bin/bash

# Reusable library for finding project root and paths
# Source this file in other scripts: source project_paths.sh

# Function to find project root using git
find_git_root() {
    git rev-parse --show-toplevel 2>/dev/null
}

# Function to find project root using marker files
find_marker_root() {
    local current_dir="$(realpath "${1:-$(pwd)}")"
    local markers=(".git" "package.json" "CLAUDE.md" ".env" "docker-compose.yml" "pyproject.toml" "requirements.txt")

    while [ "$current_dir" != "/" ]; do
        for marker in "${markers[@]}"; do
            if [ -e "$current_dir/$marker" ]; then
                echo "$current_dir"
                return 0
            fi
        done
        current_dir="$(dirname "$current_dir")"
    done
    return 1
}

# Main function to find project root (tries git first, then markers)
get_project_root() {
    local root

    # Try git first (fastest if in git repo)
    root="$(find_git_root)"
    if [ -n "$root" ]; then
        echo "$root"
        return 0
    fi

    # Fall back to marker files
    root="$(find_marker_root)"
    if [ -n "$root" ]; then
        echo "$root"
        return 0
    fi

    return 1
}

# Function to build absolute path from project root
build_path() {
    local project_root="${PROJECT_ROOT:-$(get_project_root)}"
    local relative_path="$1"

    if [ -z "$project_root" ]; then
        echo "Error: Could not find project root" >&2
        return 1
    fi

    # Remove leading slash if present
    relative_path="${relative_path#/}"
    echo "${project_root}/${relative_path}"
}

# Initialize project paths
init_project_paths() {
    # Find and export project root
    export PROJECT_ROOT="$(get_project_root)"

    if [ -z "$PROJECT_ROOT" ]; then
        echo "Error: Could not find project root" >&2
        return 1
    fi

    # Export common project paths
    export PROJECT_HOOKS="$(build_path .claude/hooks)"
    export PROJECT_SCRIPTS="$(build_path scripts)"
    export PROJECT_DOCKER="$(build_path docker-system)"
    export PROJECT_AI_DOCS="$(build_path ai_docs)"
    export PROJECT_BACKEND="$(build_path agenthub_main)"
    export PROJECT_FRONTEND="$(build_path agenthub-frontend)"
    export PROJECT_TESTS="$(build_path agenthub_main/src/tests)"

    return 0
}

# Function to change to project root
cd_project_root() {
    local root="$(get_project_root)"
    if [ -n "$root" ]; then
        cd "$root"
        echo "Changed to project root: $root"
    else
        echo "Error: Could not find project root" >&2
        return 1
    fi
}

# Function to run command from project root
run_from_root() {
    local root="$(get_project_root)"
    if [ -z "$root" ]; then
        echo "Error: Could not find project root" >&2
        return 1
    fi

    (cd "$root" && "$@")
}

# Print all project paths
show_project_paths() {
    if ! init_project_paths; then
        return 1
    fi

    cat <<EOF
Project Paths:
==============
Root:      $PROJECT_ROOT
Hooks:     $PROJECT_HOOKS
Scripts:   $PROJECT_SCRIPTS
Docker:    $PROJECT_DOCKER
AI Docs:   $PROJECT_AI_DOCS
Backend:   $PROJECT_BACKEND
Frontend:  $PROJECT_FRONTEND
Tests:     $PROJECT_TESTS
EOF
}

# Auto-initialize if not being sourced
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    # Script is being run directly
    case "${1:-show}" in
        show|paths)
            show_project_paths
            ;;
        cd|root)
            cd_project_root
            ;;
        init)
            init_project_paths
            echo "Project paths initialized"
            ;;
        *)
            echo "Usage: $0 {show|cd|init}"
            echo "  show - Display all project paths"
            echo "  cd   - Change to project root"
            echo "  init - Initialize environment variables"
            echo ""
            echo "Or source this file to use functions:"
            echo "  source $0"
            ;;
    esac
fi