#!/usr/bin/env python3
"""
Documentation indexer for ai_docs.
Generates and maintains index.json with all documentation files.
"""

import json
import os
from pathlib import Path
from datetime import datetime
import hashlib

def get_file_hash(file_path):
    """Calculate MD5 hash of a file for change detection."""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def scan_ai_docs(ai_docs_path):
    """Scan ai_docs directory and build documentation index."""
    index = {
        "generated_at": datetime.now().isoformat(),
        "total_files": 0,
        "total_directories": 0,
        "categories": {},
        "absolute_docs": {
            "tracked_files": {},
            "obsolete_docs": []
        },
        "structure": {}
    }
    
    # Track directories and files
    for root, dirs, files in os.walk(ai_docs_path):
        rel_path = Path(root).relative_to(ai_docs_path)
        
        # Skip index.json itself
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        if str(rel_path) == '.':
            rel_path = ''
        else:
            rel_path = str(rel_path)
            index["total_directories"] += 1
        
        # Process files in this directory
        md_files = [f for f in files if f.endswith('.md')]
        
        if md_files:
            category_name = rel_path if rel_path else "root"
            index["categories"][category_name] = {
                "path": rel_path,
                "files": [],
                "count": len(md_files)
            }
            
            for file in md_files:
                file_path = Path(root) / file
                rel_file_path = file_path.relative_to(ai_docs_path)
                
                file_info = {
                    "name": file,
                    "path": str(rel_file_path),
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    "hash": get_file_hash(file_path)
                }
                
                index["categories"][category_name]["files"].append(file_info)
                index["total_files"] += 1
                
                # Check if this is an absolute doc
                if str(rel_path).startswith('_absolute_docs'):
                    # Extract the original file path this doc is for
                    doc_path = str(rel_file_path).replace('_absolute_docs/', '').replace('.md', '')
                    index["absolute_docs"]["tracked_files"][doc_path] = {
                        "doc_path": str(rel_file_path),
                        "last_updated": file_info["modified"],
                        "hash": file_info["hash"]
                    }
                elif str(rel_path).startswith('_obsolete_docs'):
                    index["absolute_docs"]["obsolete_docs"].append({
                        "path": str(rel_file_path),
                        "moved_date": file_info["modified"]
                    })
    
    # Build directory structure
    def build_tree(path, tree_dict):
        for item in sorted(path.iterdir()):
            if item.is_dir() and not item.name.startswith('.'):
                tree_dict[item.name] = {}
                build_tree(item, tree_dict[item.name])
            elif item.suffix == '.md':
                if 'files' not in tree_dict:
                    tree_dict['files'] = []
                tree_dict['files'].append(item.name)
    
    tree = {}
    build_tree(ai_docs_path, tree)
    index["structure"] = tree
    
    return index

def update_index(ai_docs_path):
    """Update the index.json file."""
    index = scan_ai_docs(ai_docs_path)
    index_path = ai_docs_path / 'index.json'
    
    with open(index_path, 'w') as f:
        json.dump(index, f, indent=2, sort_keys=True)
    
    return index

def check_documentation_requirement(file_path, ai_docs_path):
    """
    Check if a file has required documentation.
    Returns tuple (has_doc, doc_path, needs_update)
    """
    # Convert to Path object
    file_path = Path(file_path)
    
    # Skip if file is in ai_docs itself
    if 'ai_docs' in file_path.parts:
        return (True, None, False)
    
    # Import env_loader to get project root
    from env_loader import get_project_root
    project_root = get_project_root()
    
    # Build expected documentation path
    doc_name = f"{file_path.name}.md"
    
    # Make file path relative to project root
    try:
        relative_path = file_path.relative_to(project_root)
        doc_path = ai_docs_path / '_absolute_docs' / relative_path.parent / doc_name
    except ValueError:
        # If file is not under project root, try with cwd
        doc_path = ai_docs_path / '_absolute_docs' / file_path.parent.relative_to(Path.cwd()) / doc_name
    
    if doc_path.exists():
        # Check if source file is newer than doc
        if file_path.exists():
            source_mtime = file_path.stat().st_mtime
            doc_mtime = doc_path.stat().st_mtime
            needs_update = source_mtime > doc_mtime
            return (True, str(doc_path), needs_update)
        return (True, str(doc_path), False)
    
    return (False, str(doc_path), True)

def move_to_obsolete(doc_path, ai_docs_path):
    """Move a documentation file to _obsolete_docs when source is deleted."""
    doc_path = Path(doc_path)
    if not doc_path.exists():
        return
    
    # Build obsolete path
    rel_path = doc_path.relative_to(ai_docs_path / '_absolute_docs')
    obsolete_path = ai_docs_path / '_obsolete_docs' / rel_path
    
    # Create directory if needed
    obsolete_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Move the file
    doc_path.rename(obsolete_path)
    
    # Add timestamp marker
    timestamp_file = obsolete_path.with_suffix('.obsolete')
    timestamp_file.write_text(f"Moved to obsolete: {datetime.now().isoformat()}\n")

if __name__ == "__main__":
    # Import env_loader to get project root
    from env_loader import get_project_root
    
    # Get ai_docs path relative to project root
    ai_docs_path = get_project_root() / 'ai_docs'
    
    # Update index
    index = update_index(ai_docs_path)
    
    print(f"Index updated: {index['total_files']} files in {index['total_directories']} directories")
    print(f"Tracked absolute docs: {len(index['absolute_docs']['tracked_files'])}")
    print(f"Obsolete docs: {len(index['absolute_docs']['obsolete_docs'])}")