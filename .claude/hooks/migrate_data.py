#!/usr/bin/env python3
"""
Migrate and consolidate data from multiple locations to the correct directories
based on .env.claude configuration.
"""
import os
import shutil
import json
from pathlib import Path
from datetime import datetime


def load_env_claude():
    """Load environment variables from .env.claude file."""
    env_file = Path.cwd() / '.env.claude'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    if key not in os.environ:
                        os.environ[key] = value.strip()


def migrate_data():
    """Migrate data from old locations to new consolidated locations."""
    load_env_claude()
    
    project_root = Path.cwd()
    
    # Define target directories from .env.claude
    target_data_dir = project_root / os.getenv('AI_DATA', '.claude/data')
    target_logs_dir = project_root / os.getenv('LOG_PATH', 'logs/claude')
    
    # Ensure target directories exist
    target_data_dir.mkdir(parents=True, exist_ok=True)
    target_logs_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Target data directory: {target_data_dir}")
    print(f"Target logs directory: {target_logs_dir}")
    
    # Old data locations to migrate from
    old_locations = {
        'data': [
            project_root / '.claude' / 'hooks' / 'data',  # Old hook data
            project_root / 'logs',  # Old logs location (if used for data)
        ],
        'logs': [
            project_root / 'logs',  # Old logs location
        ]
    }
    
    # Migrate data files
    print("\n=== Migrating Data Files ===")
    for old_dir in old_locations['data']:
        if old_dir.exists() and old_dir != target_data_dir:
            print(f"\nMigrating from: {old_dir}")
            
            # Migrate pending_hints.json
            old_hints = old_dir / 'pending_hints.json'
            if old_hints.exists():
                target_hints = target_data_dir / 'pending_hints.json'
                if target_hints.exists():
                    # Merge hints
                    print(f"  Merging pending_hints.json")
                    merge_json_files(old_hints, target_hints)
                else:
                    print(f"  Moving pending_hints.json")
                    shutil.move(str(old_hints), str(target_hints))
            
            # Migrate session files
            for session_file in old_dir.glob('*.json'):
                if session_file.name != 'pending_hints.json':
                    target_file = target_data_dir / session_file.name
                    if not target_file.exists():
                        print(f"  Moving {session_file.name}")
                        shutil.move(str(session_file), str(target_file))
    
    # Migrate log files
    print("\n=== Migrating Log Files ===")
    for old_dir in old_locations['logs']:
        if old_dir.exists() and old_dir != target_logs_dir:
            print(f"\nMigrating from: {old_dir}")
            
            # Move MCP hint logs
            for log_file in ['mcp_post_hints.log', 'mcp_post_hints_detailed.json']:
                old_log = old_dir / log_file
                if old_log.exists():
                    target_log = target_logs_dir / log_file
                    if target_log.exists():
                        print(f"  Merging {log_file}")
                        if log_file.endswith('.json'):
                            merge_json_files(old_log, target_log)
                        else:
                            merge_log_files(old_log, target_log)
                    else:
                        print(f"  Moving {log_file}")
                        shutil.move(str(old_log), str(target_log))
    
    # Clean up old empty directories
    print("\n=== Cleaning Up ===")
    for old_dir in set(old_locations['data'] + old_locations['logs']):
        if old_dir.exists() and old_dir not in [target_data_dir, target_logs_dir]:
            try:
                if not any(old_dir.iterdir()):
                    print(f"Removing empty directory: {old_dir}")
                    old_dir.rmdir()
            except Exception as e:
                print(f"Could not remove {old_dir}: {e}")
    
    print("\n✅ Migration complete!")


def merge_json_files(source: Path, target: Path):
    """Merge JSON files, keeping unique entries."""
    try:
        with open(source, 'r') as f:
            source_data = json.load(f)
        with open(target, 'r') as f:
            target_data = json.load(f)
        
        if isinstance(source_data, list) and isinstance(target_data, list):
            # Merge lists, keeping unique entries
            merged = target_data + source_data
            # Remove duplicates based on content
            seen = set()
            unique = []
            for item in merged:
                item_str = json.dumps(item, sort_keys=True)
                if item_str not in seen:
                    seen.add(item_str)
                    unique.append(item)
            
            # Keep only last 100 entries if it's a log
            if len(unique) > 100:
                unique = unique[-100:]
            
            with open(target, 'w') as f:
                json.dump(unique, f, indent=2)
            
            # Remove source file after successful merge
            source.unlink()
    except Exception as e:
        print(f"    Error merging {source.name}: {e}")


def merge_log_files(source: Path, target: Path):
    """Merge text log files."""
    try:
        with open(source, 'r') as f:
            source_lines = f.readlines()
        
        with open(target, 'a') as f:
            f.writelines(source_lines)
        
        # Remove source file after successful merge
        source.unlink()
    except Exception as e:
        print(f"    Error merging {source.name}: {e}")


if __name__ == '__main__':
    migrate_data()