#!/usr/bin/env python3
"""
Environment Detection Utility for Claude Code Hooks

This module provides comprehensive environment detection capabilities
for cross-platform and cross-environment compatibility.

Features:
- Python executable detection (python vs python3)
- Virtual environment detection (venv, conda, pipenv, pyenv)
- Operating system and platform detection
- Project structure analysis
- Dependency availability checking
- Git repository type detection (regular vs submodule)
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


class EnvironmentDetector:
    """Comprehensive environment detection for Claude Code hooks."""

    def __init__(self, project_root: Path | None = None):
        """
        Initialize environment detector.

        Args:
            project_root: Optional project root path. If not provided, will be auto-detected.
        """
        self.project_root = project_root or self._find_project_root()
        self._cache = {}

    def get_environment_info(self) -> dict[str, Any]:
        """
        Get comprehensive environment information.

        Returns:
            Dictionary containing all environment details
        """
        return {
            "platform": self.get_platform_info(),
            "python": self.get_python_info(),
            "virtual_env": self.get_virtual_env_info(),
            "git": self.get_git_info(),
            "project": self.get_project_info(),
            "dependencies": self.get_dependency_info(),
            "claude_structure": self.get_claude_structure_info(),
        }

    def get_platform_info(self) -> dict[str, str]:
        """Get operating system and platform information."""
        if "platform" in self._cache:
            return self._cache["platform"]

        info = {
            "system": platform.system(),  # Windows, Darwin, Linux
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),  # x86_64, arm64, etc.
            "processor": platform.processor(),
            "architecture": platform.architecture()[0],  # 64bit, 32bit
            "python_implementation": platform.python_implementation(),  # CPython, PyPy
            "is_windows": platform.system() == "Windows",
            "is_macos": platform.system() == "Darwin",
            "is_linux": platform.system() == "Linux",
            "path_separator": os.sep,
            "path_list_separator": os.pathsep,
        }

        # Detect Windows Subsystem for Linux (WSL)
        if info["is_linux"]:
            try:
                with open("/proc/version") as f:
                    version_info = f.read().lower()
                    info["is_wsl"] = (
                        "microsoft" in version_info or "wsl" in version_info
                    )
            except (FileNotFoundError, PermissionError):
                info["is_wsl"] = False
        else:
            info["is_wsl"] = False

        self._cache["platform"] = info
        return info

    def get_python_info(self) -> dict[str, Any]:
        """Get Python executable and version information."""
        if "python" in self._cache:
            return self._cache["python"]

        info = {
            "executable": sys.executable,
            "version": sys.version,
            "version_info": {
                "major": sys.version_info.major,
                "minor": sys.version_info.minor,
                "micro": sys.version_info.micro,
            },
            "prefix": sys.prefix,
            "exec_prefix": sys.exec_prefix,
            "path": sys.path.copy(),
            "available_executables": self._find_python_executables(),
        }

        # Check if current executable is python or python3
        exe_name = Path(sys.executable).name.lower()
        info["is_python3"] = "python3" in exe_name or info["version_info"]["major"] >= 3

        self._cache["python"] = info
        return info

    def get_virtual_env_info(self) -> dict[str, Any]:
        """Detect virtual environment type and details."""
        if "virtual_env" in self._cache:
            return self._cache["virtual_env"]

        info = {"is_virtual_env": False, "type": None, "path": None, "name": None}

        # Check for standard venv
        if hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        ):
            info["is_virtual_env"] = True
            info["type"] = "venv"
            info["path"] = sys.prefix
            info["name"] = Path(sys.prefix).name

        # Check for conda
        if "CONDA_DEFAULT_ENV" in os.environ:
            info["is_virtual_env"] = True
            info["type"] = "conda"
            info["name"] = os.environ["CONDA_DEFAULT_ENV"]
            info["path"] = os.environ.get("CONDA_PREFIX", sys.prefix)

        # Check for pipenv
        if "PIPENV_ACTIVE" in os.environ:
            info["is_virtual_env"] = True
            info["type"] = "pipenv"
            info["path"] = os.environ.get("VIRTUAL_ENV", sys.prefix)

        # Check for pyenv
        if "PYENV_VERSION" in os.environ:
            info["pyenv_version"] = os.environ["PYENV_VERSION"]

        # Additional virtual env indicators
        if "VIRTUAL_ENV" in os.environ and not info["is_virtual_env"]:
            info["is_virtual_env"] = True
            info["type"] = "unknown"
            info["path"] = os.environ["VIRTUAL_ENV"]
            info["name"] = Path(os.environ["VIRTUAL_ENV"]).name

        self._cache["virtual_env"] = info
        return info

    def get_git_info(self) -> dict[str, Any]:
        """Get Git repository information."""
        if "git" in self._cache:
            return self._cache["git"]

        info = {
            "is_git_repo": False,
            "is_submodule": False,
            "git_available": shutil.which("git") is not None,
            "root_path": None,
            "current_branch": None,
            "is_dirty": False,
            "submodules": [],
        }

        if not info["git_available"] or not self.project_root:
            self._cache["git"] = info
            return info

        try:
            # Check if we're in a git repository
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=10,
            )

            if result.returncode == 0:
                info["is_git_repo"] = True
                info["root_path"] = Path(result.stdout.strip())

                # Get current branch
                branch_result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                    timeout=5,
                )
                if branch_result.returncode == 0:
                    info["current_branch"] = branch_result.stdout.strip()

                # Check if working directory is dirty
                status_result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                    timeout=5,
                )
                if status_result.returncode == 0:
                    info["is_dirty"] = bool(status_result.stdout.strip())

                # Check for submodules
                submodules_result = subprocess.run(
                    ["git", "submodule", "status"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                    timeout=10,
                )
                if (
                    submodules_result.returncode == 0
                    and submodules_result.stdout.strip()
                ):
                    info["submodules"] = [
                        line.split()[1]
                        for line in submodules_result.stdout.strip().split("\n")
                        if line.strip()
                    ]

                # Check if .claude is a submodule
                claude_dir = self.project_root / ".claude"
                if claude_dir.exists() and ".claude" in info["submodules"]:
                    info["is_submodule"] = True

        except (
            subprocess.TimeoutExpired,
            subprocess.SubprocessError,
            FileNotFoundError,
        ):
            pass

        self._cache["git"] = info
        return info

    def get_project_info(self) -> dict[str, Any]:
        """Get project structure and configuration information."""
        if "project" in self._cache:
            return self._cache["project"]

        info = {
            "root_path": self.project_root,
            "has_claude_md": False,
            "has_claude_local_md": False,
            "has_mcp_json": False,
            "has_package_json": False,
            "has_pyproject_toml": False,
            "has_requirements_txt": False,
            "has_pipfile": False,
            "has_docker_compose": False,
            "has_dockerfile": False,
            "project_type": "unknown",
        }

        if not self.project_root:
            self._cache["project"] = info
            return info

        # Check for various project files
        files_to_check = {
            "has_claude_md": "CLAUDE.md",
            "has_claude_local_md": "CLAUDE.local.md",
            "has_mcp_json": ".mcp.json",
            "has_package_json": "package.json",
            "has_pyproject_toml": "pyproject.toml",
            "has_requirements_txt": "requirements.txt",
            "has_pipfile": "Pipfile",
            "has_docker_compose": "docker-compose.yml",
            "has_dockerfile": "Dockerfile",
        }

        for key, filename in files_to_check.items():
            info[key] = (self.project_root / filename).exists()

        # Determine project type
        if info["has_package_json"]:
            info["project_type"] = "node.js"
        elif info["has_pyproject_toml"]:
            info["project_type"] = "python"
        elif info["has_requirements_txt"]:
            info["project_type"] = "python"
        elif info["has_pipfile"]:
            info["project_type"] = "python"
        elif info["has_docker_compose"]:
            info["project_type"] = "docker"

        self._cache["project"] = info
        return info

    def get_dependency_info(self) -> dict[str, Any]:
        """Check for required dependencies and tools."""
        if "dependencies" in self._cache:
            return self._cache["dependencies"]

        info = {
            "available_tools": {},
            "python_packages": {},
            "missing_requirements": [],
        }

        # Check for common tools
        tools_to_check = ["git", "python3", "python", "pip", "pip3", "conda", "pipenv"]
        for tool in tools_to_check:
            info["available_tools"][tool] = shutil.which(tool) is not None

        # Check for Python packages (only commonly available ones to avoid import errors)
        packages_to_check = ["json", "pathlib", "subprocess", "os", "sys", "platform"]
        for package in packages_to_check:
            try:
                __import__(package)
                info["python_packages"][package] = True
            except ImportError:
                info["python_packages"][package] = False
                info["missing_requirements"].append(package)

        self._cache["dependencies"] = info
        return info

    def get_claude_structure_info(self) -> dict[str, Any]:
        """Get information about Claude directory structure."""
        if "claude_structure" in self._cache:
            return self._cache["claude_structure"]

        info = {
            "claude_dir_exists": False,
            "hooks_dir_exists": False,
            "utils_dir_exists": False,
            "config_dir_exists": False,
            "settings_json_exists": False,
            "settings_sample_exists": False,
            "setup_hooks_exists": False,
            "execute_hook_exists": False,
            "is_complete_installation": False,
        }

        if not self.project_root:
            self._cache["claude_structure"] = info
            return info

        claude_dir = self.project_root / ".claude"
        info["claude_dir_exists"] = claude_dir.exists()

        if info["claude_dir_exists"]:
            hooks_dir = claude_dir / "hooks"
            info["hooks_dir_exists"] = hooks_dir.exists()

            if info["hooks_dir_exists"]:
                info["utils_dir_exists"] = (hooks_dir / "utils").exists()
                info["config_dir_exists"] = (hooks_dir / "config").exists()
                info["setup_hooks_exists"] = (hooks_dir / "setup_hooks.py").exists()
                info["execute_hook_exists"] = (hooks_dir / "execute_hook.py").exists()

            info["settings_json_exists"] = (claude_dir / "settings.json").exists()
            info["settings_sample_exists"] = (
                claude_dir / "settings.json.sample"
            ).exists()

            # Determine if this is a complete installation
            required_components = [
                info["hooks_dir_exists"],
                info["utils_dir_exists"],
                info["setup_hooks_exists"],
                info["execute_hook_exists"],
                info["settings_sample_exists"],
            ]
            info["is_complete_installation"] = all(required_components)

        self._cache["claude_structure"] = info
        return info

    def _find_project_root(self) -> Path | None:
        """Find the project root directory."""
        # Marker files that indicate project root (ordered by priority)
        markers = [
            "CLAUDE.md",  # Most specific to Claude projects
            ".env.dev",  # Development environment marker
            ".env.claude",  # Claude-specific environment
            "CLAUDE.local.md",  # Local Claude configuration
            ".git",  # Git repository root
            "package.json",  # Node.js project
            "pyproject.toml",  # Python project
            "docker-compose.yml",  # Docker project
            ".env",  # General environment file
        ]

        # Start from current directory and this script's location
        start_paths = [
            Path.cwd(),
            Path(__file__).parent.parent.parent if __file__ else Path.cwd(),
        ]

        for start in start_paths:
            try:
                current = start.resolve()

                # Walk up the directory tree
                while current != current.parent:
                    # Check for marker files in priority order
                    for marker in markers:
                        marker_path = current / marker
                        if marker_path.exists():
                            # Verify it's a Claude project by checking for .claude directory
                            claude_dir = current / ".claude"
                            if claude_dir.exists():
                                return current

                    current = current.parent

            except (OSError, PermissionError):
                continue

        return None

    def _find_python_executables(self) -> list[str]:
        """Find all available Python executables."""
        executables = []
        common_names = [
            "python",
            "python3",
            "python3.9",
            "python3.10",
            "python3.11",
            "python3.12",
        ]

        for name in common_names:
            if shutil.which(name):
                executables.append(name)

        return executables

    def get_recommended_python_executable(self) -> str:
        """Get the recommended Python executable for this environment."""
        python_info = self.get_python_info()
        platform_info = self.get_platform_info()

        # On Windows, prefer python over python3
        if platform_info["is_windows"]:
            if "python" in python_info["available_executables"]:
                return "python"
            elif "python3" in python_info["available_executables"]:
                return "python3"
        else:
            # On Unix-like systems, prefer python3 over python
            if "python3" in python_info["available_executables"]:
                return "python3"
            elif "python" in python_info["available_executables"]:
                return "python"

        # Fallback to current executable
        return sys.executable

    def validate_environment(self) -> tuple[bool, list[str]]:
        """
        Validate that the environment is suitable for Claude hooks.

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        env_info = self.get_environment_info()

        # Check Python version
        if env_info["python"]["version_info"]["major"] < 3:
            issues.append("Python 3.x is required, but Python 2.x detected")
        elif env_info["python"]["version_info"]["minor"] < 7:
            issues.append("Python 3.7 or higher is required")

        # Check for project root
        if not self.project_root:
            issues.append("Could not find project root directory")

        # Check for Claude structure
        claude_info = env_info["claude_structure"]
        if not claude_info["claude_dir_exists"]:
            issues.append(".claude directory not found")
        elif not claude_info["is_complete_installation"]:
            missing_components = []
            if not claude_info["hooks_dir_exists"]:
                missing_components.append(".claude/hooks/")
            if not claude_info["utils_dir_exists"]:
                missing_components.append(".claude/hooks/utils/")
            if not claude_info["setup_hooks_exists"]:
                missing_components.append("setup_hooks.py")
            if not claude_info["execute_hook_exists"]:
                missing_components.append("execute_hook.py")
            if not claude_info["settings_sample_exists"]:
                missing_components.append("settings.json.sample")

            issues.append(
                f"Incomplete Claude installation. Missing: {', '.join(missing_components)}"
            )

        # Check for Git (optional but recommended)
        if not env_info["git"]["git_available"]:
            issues.append("Git not found in PATH (optional but recommended)")

        return len(issues) == 0, issues

    def generate_environment_report(self) -> str:
        """Generate a comprehensive environment report."""
        env_info = self.get_environment_info()
        is_valid, issues = self.validate_environment()

        report = []
        report.append("=" * 70)
        report.append("CLAUDE CODE HOOKS - ENVIRONMENT REPORT")
        report.append("=" * 70)

        # Validation status
        report.append(
            f"\n✅ Environment Status: {'VALID' if is_valid else 'ISSUES FOUND'}"
        )
        if issues:
            report.append("\n⚠️  Issues:")
            for issue in issues:
                report.append(f"   • {issue}")

        # Platform information
        platform = env_info["platform"]
        report.append("\n🖥️  Platform Information:")
        report.append(f"   • System: {platform['system']} {platform['release']}")
        report.append(
            f"   • Architecture: {platform['machine']} ({platform['architecture']})"
        )
        if platform.get("is_wsl"):
            report.append("   • WSL Detected: Yes")

        # Python information
        python = env_info["python"]
        report.append("\n🐍 Python Information:")
        report.append(f"   • Current Executable: {python['executable']}")
        report.append(
            f"   • Version: {python['version_info']['major']}.{python['version_info']['minor']}.{python['version_info']['micro']}"
        )
        report.append(
            f"   • Available Executables: {', '.join(python['available_executables'])}"
        )

        # Virtual environment
        venv = env_info["virtual_env"]
        if venv["is_virtual_env"]:
            report.append("\n🔒 Virtual Environment:")
            report.append(f"   • Type: {venv['type']}")
            report.append(f"   • Name: {venv['name']}")
            report.append(f"   • Path: {venv['path']}")
        else:
            report.append("\n🔒 Virtual Environment: Not detected")

        # Git information
        git = env_info["git"]
        report.append("\n📁 Git Repository:")
        report.append(f"   • Git Available: {'Yes' if git['git_available'] else 'No'}")
        if git["is_git_repo"]:
            report.append(f"   • Repository Root: {git['root_path']}")
            report.append(f"   • Current Branch: {git['current_branch']}")
            report.append(
                f"   • Working Directory: {'Dirty' if git['is_dirty'] else 'Clean'}"
            )
            if git["submodules"]:
                report.append(f"   • Submodules: {', '.join(git['submodules'])}")
        else:
            report.append("   • Repository: Not detected")

        # Project information
        project = env_info["project"]
        report.append("\n📦 Project Information:")
        report.append(f"   • Root Path: {project['root_path']}")
        report.append(f"   • Project Type: {project['project_type']}")
        config_files = [k for k, v in project.items() if k.startswith("has_") and v]
        if config_files:
            report.append(
                f"   • Configuration Files: {', '.join([k.replace('has_', '').replace('_', '.') for k in config_files])}"
            )

        # Claude structure
        claude = env_info["claude_structure"]
        report.append("\n🤖 Claude Structure:")
        report.append(
            f"   • Complete Installation: {'Yes' if claude['is_complete_installation'] else 'No'}"
        )
        report.append(
            f"   • Settings Configured: {'Yes' if claude['settings_json_exists'] else 'No'}"
        )

        # Dependencies
        deps = env_info["dependencies"]
        available_tools = [
            tool for tool, available in deps["available_tools"].items() if available
        ]
        report.append(
            f"\n🔧 Available Tools: {', '.join(available_tools) if available_tools else 'None'}"
        )

        report.append("\n" + "=" * 70)

        return "\n".join(report)


# Convenience functions for quick access
def detect_environment(project_root: Path | None = None) -> dict[str, Any]:
    """Quick function to get environment information."""
    detector = EnvironmentDetector(project_root)
    return detector.get_environment_info()


def validate_environment(project_root: Path | None = None) -> tuple[bool, list[str]]:
    """Quick function to validate environment."""
    detector = EnvironmentDetector(project_root)
    return detector.validate_environment()


def generate_environment_report(project_root: Path | None = None) -> str:
    """Quick function to generate environment report."""
    detector = EnvironmentDetector(project_root)
    return detector.generate_environment_report()


if __name__ == "__main__":
    # CLI interface for testing
    detector = EnvironmentDetector()
    print(detector.generate_environment_report())
