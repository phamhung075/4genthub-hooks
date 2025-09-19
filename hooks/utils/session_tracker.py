#!/usr/bin/env python3
"""
Session tracker for documentation enforcement.
Tracks modified files during a session to avoid blocking ongoing work.
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta

def get_session_file():
    """Get the session tracking file path."""
    # Store in AI_DATA directory
    from env_loader import get_ai_data_path
    session_file = get_ai_data_path() / 'documentation_session.json'
    return session_file

def get_current_session():
    """Get or create current session data."""
    session_file = get_session_file()
    
    # Default session data
    default_session = {
        "session_id": datetime.now().isoformat(),
        "started_at": datetime.now().isoformat(),
        "modified_files": [],
        "modified_folders": []
    }
    
    if session_file.exists():
        try:
            with open(session_file, 'r') as f:
                session = json.load(f)
                
            # Check if session is still valid (within 2 hours)
            started = datetime.fromisoformat(session['started_at'])
            if datetime.now() - started > timedelta(hours=2):
                # Session expired, create new one
                session = default_session
                save_session(session)
            
            return session
        except:
            pass
    
    # Create new session
    save_session(default_session)
    return default_session

def save_session(session_data):
    """Save session data to file."""
    session_file = get_session_file()
    with open(session_file, 'w') as f:
        json.dump(session_data, f, indent=2)

def add_modified_file(file_path):
    """Add a file to the current session's modified files."""
    session = get_current_session()
    
    file_str = str(file_path)
    if file_str not in session['modified_files']:
        session['modified_files'].append(file_str)
        save_session(session)

def add_modified_folder(folder_path):
    """Add a folder to the current session's modified folders."""
    session = get_current_session()
    
    folder_str = str(folder_path)
    if folder_str not in session['modified_folders']:
        session['modified_folders'].append(folder_str)
        save_session(session)

def is_file_in_session(file_path):
    """Check if a file was already modified in this session."""
    session = get_current_session()
    return str(file_path) in session['modified_files']

def is_folder_in_session(folder_path):
    """Check if a folder was already modified in this session."""
    session = get_current_session()
    return str(folder_path) in session['modified_folders']

def clear_expired_sessions():
    """Clear sessions older than 2 hours."""
    session_file = get_session_file()
    if session_file.exists():
        try:
            with open(session_file, 'r') as f:
                session = json.load(f)
            
            started = datetime.fromisoformat(session['started_at'])
            if datetime.now() - started > timedelta(hours=2):
                session_file.unlink()
        except:
            pass