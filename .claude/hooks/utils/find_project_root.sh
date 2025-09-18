#!/bin/bash

# Script to find project root dynamically and construct paths
# Works from any subdirectory within the project

# Function to find project root by looking for marker files
find_project_root() {
    local current_dir="$(pwd)"
    local marker_files=(".git" "package.json" "CLAUDE.md" ".env" "docker-compose.yml")

    # Start from current directory and go up
    while [ "$current_dir" != "/" ]; do
        # Check for any of the marker files
        for marker in "${marker_files[@]}"; do
            if [ -e "$current_dir/$marker" ]; then
                echo "$current_dir"
                return 0
            fi
        done
        # Go up one directory
        current_dir="$(dirname "$current_dir")"
    done

    # If no project root found
    echo "Error: Could not find project root" >&2
    return 1
}

# Function to construct absolute path from project root
get_absolute_path() {
    local relative_path="$1"
    local project_root="$(find_project_root)"

    if [ $? -eq 0 ]; then
        # Remove leading slash from relative path if present
        relative_path="${relative_path#/}"
        echo "${project_root}/${relative_path}"
    else
        return 1
    fi
}

# Main script execution
main() {
    # Find project root
    PROJECT_ROOT="$(find_project_root)"

    if [ $? -ne 0 ]; then
        echo "Failed to find project root"
        exit 1
    fi

    echo "Project Root: $PROJECT_ROOT"

    # Example usage - construct various paths relative to project root
    HOOKS_DIR="$(get_absolute_path ".claude/hooks")"
    SCRIPTS_DIR="$(get_absolute_path "scripts")"
    DOCKER_DIR="$(get_absolute_path "docker-system")"
    AI_DOCS_DIR="$(get_absolute_path "ai_docs")"
    BACKEND_DIR="$(get_absolute_path "agenthub_main")"
    FRONTEND_DIR="$(get_absolute_path "agenthub-frontend")"

    # Display the paths
    echo "Hooks Directory: $HOOKS_DIR"
    echo "Scripts Directory: $SCRIPTS_DIR"
    echo "Docker Directory: $DOCKER_DIR"
    echo "AI Docs Directory: $AI_DOCS_DIR"
    echo "Backend Directory: $BACKEND_DIR"
    echo "Frontend Directory: $FRONTEND_DIR"

    # Export for use in other scripts
    export PROJECT_ROOT
    export HOOKS_DIR
    export SCRIPTS_DIR
    export DOCKER_DIR
    export AI_DOCS_DIR
    export BACKEND_DIR
    export FRONTEND_DIR
}

# If script is being sourced, don't run main
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi