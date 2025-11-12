#!/usr/bin/env python3
"""
Dependency Manager for Claude Code Hooks

This module handles dependency detection, installation, and fallback strategies
for Claude Code hooks across different environments and platforms.

Features:
- Optional dependency detection and handling
- Graceful degradation when packages are missing
- Clear error messages and resolution instructions
- Support for different package managers (pip, conda, pipenv)
- Virtual environment handling
- Cross-platform compatibility
"""

import importlib
import shutil
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pkg_resources


@dataclass
class Dependency:
    """Represents a package dependency with installation and fallback options."""

    name: str
    import_name: str | None = None
    min_version: str | None = None
    pip_name: str | None = None
    conda_name: str | None = None
    required: bool = True
    fallback_available: bool = False
    fallback_message: str = ""
    install_instructions: str = ""


class DependencyManager:
    """Manages dependencies for Claude Code hooks."""

    def __init__(self, project_root: Path | None = None):
        """
        Initialize dependency manager.

        Args:
            project_root: Optional project root path
        """
        self.project_root = project_root
        self._available_packages = {}
        self._missing_packages = {}
        self._fallback_handlers = {}

        # Define common dependencies for Claude hooks
        self.common_dependencies = [
            Dependency(
                name="requests",
                pip_name="requests",
                conda_name="requests",
                required=False,
                fallback_available=True,
                fallback_message="HTTP requests will use urllib instead of requests library",
                install_instructions="pip install requests",
            ),
            Dependency(
                name="colorama",
                pip_name="colorama",
                conda_name="colorama",
                required=False,
                fallback_available=True,
                fallback_message="Console output will not be colored",
                install_instructions="pip install colorama",
            ),
            Dependency(
                name="rich",
                pip_name="rich",
                conda_name="rich",
                required=False,
                fallback_available=True,
                fallback_message="Console output will use basic formatting",
                install_instructions="pip install rich",
            ),
            Dependency(
                name="gitpython",
                import_name="git",
                pip_name="GitPython",
                conda_name="gitpython",
                required=False,
                fallback_available=True,
                fallback_message="Git operations will use subprocess calls",
                install_instructions="pip install GitPython",
            ),
        ]

    def check_dependencies(
        self, dependencies: list[Dependency] | None = None
    ) -> dict[str, Any]:
        """
        Check the availability of dependencies.

        Args:
            dependencies: List of dependencies to check. If None, uses common_dependencies.

        Returns:
            Dictionary with dependency status information
        """
        if dependencies is None:
            dependencies = self.common_dependencies

        result = {
            "available": {},
            "missing": {},
            "versions": {},
            "can_install": {},
            "fallbacks_available": {},
            "all_required_available": True,
            "install_commands": {},
        }

        for dep in dependencies:
            import_name = dep.import_name or dep.name
            is_available = self._check_package_availability(import_name)

            result["available"][dep.name] = is_available
            result["fallbacks_available"][dep.name] = dep.fallback_available

            if is_available:
                version = self._get_package_version(import_name)
                result["versions"][dep.name] = version

                # Check version compatibility if required
                if dep.min_version and version:
                    if not self._is_version_compatible(version, dep.min_version):
                        result["missing"][dep.name] = (
                            f"Version {version} < required {dep.min_version}"
                        )
                        if dep.required:
                            result["all_required_available"] = False
            else:
                result["missing"][dep.name] = "Package not found"
                if dep.required and not dep.fallback_available:
                    result["all_required_available"] = False

            # Generate install commands
            install_cmd = self._generate_install_command(dep)
            if install_cmd:
                result["install_commands"][dep.name] = install_cmd

        return result

    def install_missing_dependencies(
        self,
        dependencies: list[Dependency] | None = None,
        interactive: bool = True,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """
        Attempt to install missing dependencies.

        Args:
            dependencies: List of dependencies to install
            interactive: Whether to prompt user for confirmation
            dry_run: If True, only show what would be installed

        Returns:
            Dictionary with installation results
        """
        if dependencies is None:
            dependencies = self.common_dependencies

        result = {
            "attempted": [],
            "successful": [],
            "failed": [],
            "skipped": [],
            "commands_run": [],
        }

        dep_status = self.check_dependencies(dependencies)

        for dep in dependencies:
            if (
                dep.name in dep_status["missing"]
                and dep.name in dep_status["install_commands"]
            ):
                if interactive and not dry_run:
                    answer = input(
                        f"\nInstall {dep.name}? ({dep.install_instructions}) [y/N]: "
                    )
                    if answer.lower() not in ["y", "yes"]:
                        result["skipped"].append(dep.name)
                        continue

                install_cmd = dep_status["install_commands"][dep.name]
                result["attempted"].append(dep.name)
                result["commands_run"].append(install_cmd)

                if dry_run:
                    print(f"Would run: {install_cmd}")
                    result["successful"].append(dep.name)
                else:
                    success = self._run_install_command(install_cmd)
                    if success:
                        result["successful"].append(dep.name)
                    else:
                        result["failed"].append(dep.name)

        return result

    def get_fallback_handlers(self) -> dict[str, Callable]:
        """Get registered fallback handlers for missing packages."""
        return self._fallback_handlers.copy()

    def register_fallback_handler(self, package_name: str, handler: Callable):
        """
        Register a fallback handler for a missing package.

        Args:
            package_name: Name of the package
            handler: Callable that provides fallback functionality
        """
        self._fallback_handlers[package_name] = handler

    def safe_import(self, package_name: str, fallback_handler: Callable | None = None):
        """
        Safely import a package with fallback handling.

        Args:
            package_name: Name of package to import
            fallback_handler: Optional fallback function if import fails

        Returns:
            Imported module or fallback result
        """
        try:
            return importlib.import_module(package_name)
        except ImportError:
            if fallback_handler:
                return fallback_handler()
            elif package_name in self._fallback_handlers:
                return self._fallback_handlers[package_name]()
            else:
                return None

    def generate_dependency_report(
        self, dependencies: list[Dependency] | None = None
    ) -> str:
        """Generate a comprehensive dependency report."""
        if dependencies is None:
            dependencies = self.common_dependencies

        dep_status = self.check_dependencies(dependencies)

        report = []
        report.append("=" * 60)
        report.append("CLAUDE CODE HOOKS - DEPENDENCY REPORT")
        report.append("=" * 60)

        # Overall status
        if dep_status["all_required_available"]:
            report.append("\n✅ All required dependencies are available")
        else:
            report.append("\n⚠️  Some required dependencies are missing")

        # Available packages
        available = [name for name, status in dep_status["available"].items() if status]
        if available:
            report.append(f"\n📦 Available Packages ({len(available)}):")
            for name in available:
                version = dep_status["versions"].get(name, "unknown")
                report.append(f"   ✅ {name} (version: {version})")

        # Missing packages
        missing = list(dep_status["missing"].keys())
        if missing:
            report.append(f"\n❌ Missing Packages ({len(missing)}):")
            for name in missing:
                dep = next((d for d in dependencies if d.name == name), None)
                status_msg = dep_status["missing"][name]

                if dep:
                    required_text = "Required" if dep.required else "Optional"
                    fallback_text = (
                        "Fallback available"
                        if dep.fallback_available
                        else "No fallback"
                    )
                    report.append(f"   ❌ {name} ({required_text}, {fallback_text})")
                    report.append(f"      Status: {status_msg}")

                    if dep.fallback_available and dep.fallback_message:
                        report.append(f"      Fallback: {dep.fallback_message}")

                    if name in dep_status["install_commands"]:
                        report.append(
                            f"      Install: {dep_status['install_commands'][name]}"
                        )
                else:
                    report.append(f"   ❌ {name}: {status_msg}")

        # Installation commands
        install_commands = dep_status["install_commands"]
        if install_commands:
            report.append("\n🔧 Installation Commands:")
            for name, cmd in install_commands.items():
                report.append(f"   {name}: {cmd}")

        # Package manager detection
        report.append("\n🛠️  Package Manager Information:")
        managers = self._detect_package_managers()
        for manager, info in managers.items():
            status = "Available" if info["available"] else "Not found"
            report.append(f"   • {manager}: {status}")
            if info["available"] and info.get("version"):
                report.append(f"     Version: {info['version']}")

        report.append("\n" + "=" * 60)
        return "\n".join(report)

    def _check_package_availability(self, package_name: str) -> bool:
        """Check if a package is available for import."""
        if package_name in self._available_packages:
            return self._available_packages[package_name]

        try:
            importlib.import_module(package_name)
            self._available_packages[package_name] = True
            return True
        except ImportError:
            self._available_packages[package_name] = False
            return False

    def _get_package_version(self, package_name: str) -> str | None:
        """Get the version of an installed package."""
        try:
            # Try pkg_resources first
            return pkg_resources.get_distribution(package_name).version
        except (pkg_resources.DistributionNotFound, Exception):
            try:
                # Try importlib.metadata (Python 3.8+)
                if sys.version_info >= (3, 8):
                    import importlib.metadata

                    return importlib.metadata.version(package_name)
            except Exception:
                pass

            try:
                # Try importing and checking __version__
                module = importlib.import_module(package_name)
                if hasattr(module, "__version__"):
                    return module.__version__
            except Exception:
                pass

        return None

    def _is_version_compatible(self, current_version: str, min_version: str) -> bool:
        """Check if current version meets minimum requirement."""
        try:
            from packaging import version

            return version.parse(current_version) >= version.parse(min_version)
        except ImportError:
            # Fallback to simple string comparison
            current_parts = [int(x) for x in current_version.split(".") if x.isdigit()]
            min_parts = [int(x) for x in min_version.split(".") if x.isdigit()]

            # Pad shorter version with zeros
            max_len = max(len(current_parts), len(min_parts))
            current_parts.extend([0] * (max_len - len(current_parts)))
            min_parts.extend([0] * (max_len - len(min_parts)))

            return current_parts >= min_parts

    def _generate_install_command(self, dependency: Dependency) -> str | None:
        """Generate installation command for a dependency."""
        managers = self._detect_package_managers()

        # Prefer conda if available and conda_name is specified
        if managers["conda"]["available"] and dependency.conda_name:
            return f"conda install {dependency.conda_name}"

        # Use pip if available
        if managers["pip"]["available"] or managers["pip3"]["available"]:
            pip_cmd = "pip3" if managers["pip3"]["available"] else "pip"
            package_name = dependency.pip_name or dependency.name
            return f"{pip_cmd} install {package_name}"

        return None

    def _run_install_command(self, command: str) -> bool:
        """Run an installation command."""
        try:
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )
            return result.returncode == 0
        except (
            subprocess.TimeoutExpired,
            subprocess.SubprocessError,
            FileNotFoundError,
        ):
            return False

    def _detect_package_managers(self) -> dict[str, dict[str, Any]]:
        """Detect available package managers."""
        managers = {
            "pip": {"available": False, "version": None},
            "pip3": {"available": False, "version": None},
            "conda": {"available": False, "version": None},
            "pipenv": {"available": False, "version": None},
        }

        for manager in managers.keys():
            if shutil.which(manager):
                managers[manager]["available"] = True

                # Try to get version
                try:
                    result = subprocess.run(
                        [manager, "--version"],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    if result.returncode == 0:
                        managers[manager]["version"] = result.stdout.strip()
                except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                    pass

        return managers


# Fallback implementations for common packages
class FallbackImplementations:
    """Provides fallback implementations for common packages."""

    @staticmethod
    def requests_fallback():
        """Fallback for requests library using urllib."""
        import json
        import urllib.error
        import urllib.parse
        import urllib.request

        class FallbackRequests:
            @staticmethod
            def get(url, headers=None, timeout=30):
                req = urllib.request.Request(url, headers=headers or {})
                try:
                    with urllib.request.urlopen(req, timeout=timeout) as response:
                        return FallbackResponse(response)
                except urllib.error.URLError as e:
                    raise Exception(f"Request failed: {e}")

            @staticmethod
            def post(url, data=None, json_data=None, headers=None, timeout=30):
                headers = headers or {}

                if json_data is not None:
                    data = json.dumps(json_data).encode("utf-8")
                    headers["Content-Type"] = "application/json"
                elif data:
                    data = data.encode("utf-8") if isinstance(data, str) else data

                req = urllib.request.Request(
                    url, data=data, headers=headers, method="POST"
                )
                try:
                    with urllib.request.urlopen(req, timeout=timeout) as response:
                        return FallbackResponse(response)
                except urllib.error.URLError as e:
                    raise Exception(f"Request failed: {e}")

        class FallbackResponse:
            def __init__(self, response):
                self._response = response
                self.status_code = response.getcode()
                self.headers = dict(response.headers)
                self._text = None

            @property
            def text(self):
                if self._text is None:
                    self._text = self._response.read().decode("utf-8")
                return self._text

            def json(self):
                return json.loads(self.text)

        return FallbackRequests

    @staticmethod
    def colorama_fallback():
        """Fallback for colorama - no coloring."""

        class FallbackColorama:
            class Fore:
                RED = ""
                GREEN = ""
                YELLOW = ""
                BLUE = ""
                MAGENTA = ""
                CYAN = ""
                WHITE = ""
                RESET = ""

            class Back:
                RED = ""
                GREEN = ""
                YELLOW = ""
                BLUE = ""
                MAGENTA = ""
                CYAN = ""
                WHITE = ""
                RESET = ""

            class Style:
                BRIGHT = ""
                DIM = ""
                NORMAL = ""
                RESET_ALL = ""

            @staticmethod
            def init():
                pass

        return FallbackColorama

    @staticmethod
    def rich_fallback():
        """Fallback for rich - basic print functionality."""

        class FallbackConsole:
            def print(self, *args, **kwargs):
                # Remove rich-specific kwargs
                kwargs.pop("style", None)
                kwargs.pop("markup", None)
                kwargs.pop("highlight", None)
                print(*args, **kwargs)

            def log(self, *args, **kwargs):
                print("[LOG]", *args)

        class FallbackRich:
            console = FallbackConsole()

        return FallbackRich

    @staticmethod
    def git_fallback():
        """Fallback for GitPython using subprocess."""
        import subprocess
        from pathlib import Path

        class FallbackGit:
            def __init__(self, repo_path="."):
                self.repo_path = Path(repo_path)

            def git_command(self, *args):
                try:
                    result = subprocess.run(
                        ["git"] + list(args),
                        cwd=self.repo_path,
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    if result.returncode == 0:
                        return result.stdout.strip()
                    else:
                        raise Exception(f"Git command failed: {result.stderr}")
                except (
                    subprocess.TimeoutExpired,
                    subprocess.SubprocessError,
                    FileNotFoundError,
                ) as e:
                    raise Exception(f"Git command failed: {e}")

            def get_current_branch(self):
                return self.git_command("branch", "--show-current")

            def is_dirty(self):
                status = self.git_command("status", "--porcelain")
                return bool(status.strip())

        return FallbackGit


# Register default fallback handlers
def setup_default_fallbacks(manager: DependencyManager):
    """Setup default fallback handlers."""
    manager.register_fallback_handler(
        "requests", FallbackImplementations.requests_fallback
    )
    manager.register_fallback_handler(
        "colorama", FallbackImplementations.colorama_fallback
    )
    manager.register_fallback_handler("rich", FallbackImplementations.rich_fallback)
    manager.register_fallback_handler("git", FallbackImplementations.git_fallback)


# Convenience functions
def check_dependencies(dependencies: list[Dependency] | None = None) -> dict[str, Any]:
    """Quick function to check dependencies."""
    manager = DependencyManager()
    return manager.check_dependencies(dependencies)


def install_missing_dependencies(
    dependencies: list[Dependency] | None = None,
    interactive: bool = True,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Quick function to install missing dependencies."""
    manager = DependencyManager()
    return manager.install_missing_dependencies(dependencies, interactive, dry_run)


def generate_dependency_report(dependencies: list[Dependency] | None = None) -> str:
    """Quick function to generate dependency report."""
    manager = DependencyManager()
    return manager.generate_dependency_report(dependencies)


if __name__ == "__main__":
    # CLI interface for testing
    manager = DependencyManager()
    setup_default_fallbacks(manager)
    print(manager.generate_dependency_report())
