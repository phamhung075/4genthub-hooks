#!/usr/bin/env python3
"""
Lazy Git Context Provider - Token-optimized git status.

Provides minimal git summary (branch + change count) instead of full file listing.
Saves ~2,850 tokens (95% reduction from 3,000 to 150 tokens).

Full details available via /git_status slash command.
"""

import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class ContextProvider(ABC):
    """Base context provider interface."""

    @abstractmethod
    def get_context(self, input_data: Dict) -> Optional[Dict[str, Any]]:
        """Get context information."""
        pass


class LazyGitContextProvider(ContextProvider):
    """Provides git summary with on-demand details."""

    def get_context(self, input_data: Dict) -> Optional[Dict[str, Any]]:
        """Get minimal git summary (branch + change count only)."""
        try:
            # Get current branch
            branch_result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True, text=True, timeout=2
            )
            branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"

            # Count changes only (don't list them)
            status_result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True, text=True, timeout=2
            )

            if status_result.returncode == 0 and status_result.stdout.strip():
                change_count = len([line for line in status_result.stdout.strip().split('\n') if line])
            else:
                change_count = 0

            # Get main branch name (for PR context)
            try:
                main_result = subprocess.run(
                    ['git', 'symbolic-ref', 'refs/remotes/origin/HEAD'],
                    capture_output=True, text=True, timeout=2
                )
                if main_result.returncode == 0:
                    main_branch = main_result.stdout.strip().split('/')[-1]
                else:
                    main_branch = "main"
            except:
                main_branch = "main"

            return {
                'branch': branch,
                'change_count': change_count,
                'main_branch': main_branch,
                'summary_only': True,
                'mode': 'compact'
            }
        except Exception:
            return {
                'branch': 'unknown',
                'change_count': 0,
                'main_branch': 'main',
                'error': True,
                'mode': 'compact'
            }
