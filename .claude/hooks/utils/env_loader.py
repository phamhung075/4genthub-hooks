#!/usr/bin/env python3
"""Utility to load environment paths from .env.claude file."""

import os
from pathlib import Path
from dotenv import load_dotenv

def find_project_root():
    """Find the project root by looking for .env.claude or .git directory."""
    current = Path.cwd()
    
    # Walk up the directory tree looking for .env.claude or .git
    for parent in [current] + list(current.parents):
        if (parent / '.env.claude').exists() or (parent / '.git').exists():
            return parent
    
    # Fallback to current directory if no markers found
    return current

# Find project root and load .env.claude file once at module level
PROJECT_ROOT = find_project_root()
ENV_CLAUDE_PATH = PROJECT_ROOT / '.env.claude'

if ENV_CLAUDE_PATH.exists():
    load_dotenv(ENV_CLAUDE_PATH)
else:
    # Fallback to .env if .env.claude doesn't exist
    env_path = PROJECT_ROOT / '.env'
    if env_path.exists():
        load_dotenv(env_path)

def get_ai_data_path():
    """
    Get the AI_DATA path from .env.claude file.
    Falls back to 'logs' if not set.
    Always relative to project root, not current working directory.
    """
    
    # Get AI_DATA from environment, default to 'logs'
    ai_data_path = os.getenv('AI_DATA', 'logs')
    
    # Convert to Path object and ensure it's absolute
    if not os.path.isabs(ai_data_path):
        ai_data_path = PROJECT_ROOT / ai_data_path
    else:
        ai_data_path = Path(ai_data_path)
    
    # Ensure the directory exists
    ai_data_path.mkdir(parents=True, exist_ok=True)
    
    return ai_data_path

def get_ai_docs_path():
    """
    Get the AI_DOCS path from .env.claude file.
    Falls back to 'ai_docs' if not set.
    Always relative to project root, not current working directory.
    """
    # Get AI_DOCS from environment, default to 'ai_docs'
    ai_docs_path = os.getenv('AI_DOCS', 'ai_docs')
    
    # Convert to Path object and ensure it's absolute
    if not os.path.isabs(ai_docs_path):
        ai_docs_path = PROJECT_ROOT / ai_docs_path
    else:
        ai_docs_path = Path(ai_docs_path)
    
    # Ensure the directory exists
    ai_docs_path.mkdir(parents=True, exist_ok=True)
    
    return ai_docs_path

def get_log_path():
    """
    Get the LOG_PATH from .env.claude file.
    Falls back to 'logs' if not set.
    Always relative to project root, not current working directory.
    """
    # Get LOG_PATH from environment, default to 'logs'
    log_path = os.getenv('LOG_PATH', 'logs')
    
    # Convert to Path object and ensure it's absolute
    if not os.path.isabs(log_path):
        log_path = PROJECT_ROOT / log_path
    else:
        log_path = Path(log_path)
    
    # Ensure the directory exists
    log_path.mkdir(parents=True, exist_ok=True)
    
    return log_path

def get_all_paths():
    """
    Get all configured paths as a dictionary.
    Returns dict with 'ai_data', 'ai_docs', and 'log_path' keys.
    """
    return {
        'ai_data': get_ai_data_path(),
        'ai_docs': get_ai_docs_path(),
        'log_path': get_log_path()
    }

def is_claude_edit_enabled():
    """
    Check if editing .claude files is enabled.
    Returns True if ENABLE_CLAUDE_EDIT is 'true', '1', 'yes', or 'on'.
    """
    enable_edit = os.getenv('ENABLE_CLAUDE_EDIT', 'false').lower()
    return enable_edit in ['true', '1', 'yes', 'on']

def get_project_root():
    """
    Get the project root directory.
    Returns the cached PROJECT_ROOT that was found at module load time.
    """
    return PROJECT_ROOT