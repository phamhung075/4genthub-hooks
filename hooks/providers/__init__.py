"""
Optimized context providers for token-efficient session startup.

This module provides compact alternatives to the verbose context providers,
reducing token consumption by ~60% while maintaining information accessibility
through on-demand slash commands.
"""

__all__ = [
    'LazyGitContextProvider',
    'ConditionalMCPProvider',
    'CompactEnvironmentProvider',
    'SimpleFormatter',
]
