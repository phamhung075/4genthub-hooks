#!/bin/bash

# Example script showing how to use the project path utilities
# This script can be run from anywhere within the project

# Source the project paths library
SCRIPT_DIR="$(dirname "$(realpath "$0")")"
source "$SCRIPT_DIR/project_paths.sh"

echo "=== Example 1: Basic Usage ==="
# Initialize project paths (sets environment variables)
init_project_paths

echo "Project root is: $PROJECT_ROOT"
echo "Running from: $(pwd)"
echo ""

echo "=== Example 2: Building Paths ==="
# Build paths relative to project root
hooks_script="$(build_path .claude/hooks/pre_tool_use.py)"
config_file="$(build_path .env)"

echo "Hooks script: $hooks_script"
echo "Config file: $config_file"
echo ""

echo "=== Example 3: Running Commands from Root ==="
# Run a command from project root without changing current directory
echo "Files in project root:"
run_from_root ls -la | head -5
echo ""

echo "=== Example 4: Working with Different Projects ==="
# This same script works for ANY project with marker files
# Just run it from within that project's directory structure

echo "=== Example 5: Python Integration ==="
# You can also call the Python version
python3 "$PROJECT_SCRIPTS/find_project_root.py"

echo ""
echo "=== Example 6: Use in Your Scripts ==="
cat <<'EOF'

To use in your own scripts, add this at the top:

    #!/bin/bash
    # Find the project paths library
    for dir in "$(dirname "$0")" "$(pwd)" "$(pwd)/scripts"; do
        if [ -f "$dir/project_paths.sh" ]; then
            source "$dir/project_paths.sh"
            break
        fi
    done

    # Now you can use:
    init_project_paths
    my_file="$(build_path path/to/my/file.txt)"
    cd_project_root
    # etc...

EOF