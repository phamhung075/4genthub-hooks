#!/usr/bin/env python3
"""
Unit tests for Documentation Indexer.

Tests the docs_indexer.py module which handles:
- Documentation scanning and indexing
- MD5 hash calculation for change detection
- Absolute docs tracking
- Obsolete docs management
- Index JSON generation
"""

import json
import pytest
import tempfile
import hashlib
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add the utils directory to the path for testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "utils"))

from docs_indexer import (
    get_file_hash,
    scan_ai_docs,
    update_index,
    check_documentation_requirement,
    move_to_obsolete
)


class TestFileHash:
    """Test file hash calculation functionality."""

    def test_get_file_hash_valid_file(self):
        """Test MD5 hash calculation for a valid file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            f.flush()

            result = get_file_hash(f.name)

            # Calculate expected hash
            expected = hashlib.md5(b"test content").hexdigest()
            assert result == expected

            # Cleanup
            Path(f.name).unlink()

    def test_get_file_hash_empty_file(self):
        """Test hash calculation for empty file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.flush()

            result = get_file_hash(f.name)
            expected = hashlib.md5(b"").hexdigest()
            assert result == expected

            Path(f.name).unlink()

    def test_get_file_hash_nonexistent_file(self):
        """Test hash calculation for non-existent file."""
        result = get_file_hash("/nonexistent/file.txt")
        assert result is None

    def test_get_file_hash_permission_error(self):
        """Test hash calculation when file cannot be read."""
        with patch('builtins.open', side_effect=PermissionError):
            result = get_file_hash("any_file.txt")
            assert result is None


class TestScanAiDocs:
    """Test documentation scanning functionality."""

    def test_scan_ai_docs_empty_directory(self):
        """Test scanning empty ai_docs directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            ai_docs_path = Path(temp_dir)

            result = scan_ai_docs(ai_docs_path)

            assert result["total_files"] == 0
            assert result["total_directories"] == 0
            assert result["categories"] == {}
            assert "generated_at" in result
            assert "absolute_docs" in result
            assert "structure" in result

    def test_scan_ai_docs_with_markdown_files(self):
        """Test scanning directory with markdown files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            ai_docs_path = Path(temp_dir)

            # Create some markdown files
            (ai_docs_path / "readme.md").write_text("# README")
            (ai_docs_path / "guide.md").write_text("# Guide")

            result = scan_ai_docs(ai_docs_path)

            assert result["total_files"] == 2
            assert result["total_directories"] == 0
            assert "root" in result["categories"]
            assert result["categories"]["root"]["count"] == 2
            assert len(result["categories"]["root"]["files"]) == 2

    def test_scan_ai_docs_with_subdirectories(self):
        """Test scanning with subdirectories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            ai_docs_path = Path(temp_dir)

            # Create subdirectory with files
            sub_dir = ai_docs_path / "api-docs"
            sub_dir.mkdir()
            (sub_dir / "endpoints.md").write_text("# Endpoints")

            result = scan_ai_docs(ai_docs_path)

            assert result["total_files"] == 1
            assert result["total_directories"] == 1
            assert "api-docs" in result["categories"]
            assert result["categories"]["api-docs"]["count"] == 1

    def test_scan_ai_docs_with_absolute_docs(self):
        """Test scanning with _absolute_docs structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            ai_docs_path = Path(temp_dir)

            # Create absolute docs structure
            abs_docs = ai_docs_path / "_absolute_docs" / "src"
            abs_docs.mkdir(parents=True)
            (abs_docs / "main.py.md").write_text("# Main module documentation")

            result = scan_ai_docs(ai_docs_path)

            assert "src/main.py" in result["absolute_docs"]["tracked_files"]
            tracked = result["absolute_docs"]["tracked_files"]["src/main.py"]
            assert tracked["doc_path"] == "_absolute_docs/src/main.py.md"
            assert "last_updated" in tracked
            assert "hash" in tracked

    def test_scan_ai_docs_with_obsolete_docs(self):
        """Test scanning with _obsolete_docs structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            ai_docs_path = Path(temp_dir)

            # Create obsolete docs
            obs_docs = ai_docs_path / "_obsolete_docs"
            obs_docs.mkdir()
            (obs_docs / "old_file.md").write_text("# Old documentation")

            result = scan_ai_docs(ai_docs_path)

            assert len(result["absolute_docs"]["obsolete_docs"]) == 1
            obsolete = result["absolute_docs"]["obsolete_docs"][0]
            assert obsolete["path"] == "_obsolete_docs/old_file.md"
            assert "moved_date" in obsolete

    def test_scan_ai_docs_ignores_hidden_directories(self):
        """Test that hidden directories are ignored."""
        with tempfile.TemporaryDirectory() as temp_dir:
            ai_docs_path = Path(temp_dir)

            # Create hidden directory
            hidden_dir = ai_docs_path / ".hidden"
            hidden_dir.mkdir()
            (hidden_dir / "secret.md").write_text("# Secret")

            # Create normal file
            (ai_docs_path / "normal.md").write_text("# Normal")

            result = scan_ai_docs(ai_docs_path)

            assert result["total_files"] == 1  # Only normal.md counted
            assert ".hidden" not in result["categories"]

    def test_scan_ai_docs_structure_generation(self):
        """Test directory structure generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            ai_docs_path = Path(temp_dir)

            # Create nested structure
            (ai_docs_path / "api" / "v1").mkdir(parents=True)
            (ai_docs_path / "api" / "v1" / "users.md").write_text("# Users API")
            (ai_docs_path / "guides").mkdir()
            (ai_docs_path / "guides" / "setup.md").write_text("# Setup Guide")

            result = scan_ai_docs(ai_docs_path)

            structure = result["structure"]
            assert "api" in structure
            assert "v1" in structure["api"]
            assert "files" in structure["api"]["v1"]
            assert "users.md" in structure["api"]["v1"]["files"]

            assert "guides" in structure
            assert "files" in structure["guides"]
            assert "setup.md" in structure["guides"]["files"]


class TestUpdateIndex:
    """Test index update functionality."""

    def test_update_index_creates_file(self):
        """Test that update_index creates index.json file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            ai_docs_path = Path(temp_dir)
            (ai_docs_path / "test.md").write_text("# Test")

            result = update_index(ai_docs_path)

            index_file = ai_docs_path / "index.json"
            assert index_file.exists()

            # Verify file content
            with open(index_file) as f:
                data = json.load(f)

            assert data["total_files"] == 1
            assert "generated_at" in data

    def test_update_index_overwrites_existing(self):
        """Test that update_index overwrites existing index.json."""
        with tempfile.TemporaryDirectory() as temp_dir:
            ai_docs_path = Path(temp_dir)
            index_file = ai_docs_path / "index.json"

            # Create initial index
            index_file.write_text('{"old": "data"}')

            # Add markdown file and update
            (ai_docs_path / "new.md").write_text("# New")
            result = update_index(ai_docs_path)

            # Verify old data is gone
            with open(index_file) as f:
                data = json.load(f)

            assert "old" not in data
            assert data["total_files"] == 1


class TestCheckDocumentationRequirement:
    """Test documentation requirement checking."""

    @patch('docs_indexer.get_project_root')
    def test_check_documentation_requirement_file_in_ai_docs(self, mock_get_root):
        """Test that files in ai_docs directory don't require documentation."""
        mock_get_root.return_value = Path("/project")

        with tempfile.TemporaryDirectory() as temp_dir:
            ai_docs_path = Path(temp_dir)
            file_path = Path("/project/ai_docs/test.md")

            has_doc, doc_path, needs_update = check_documentation_requirement(
                file_path, ai_docs_path
            )

            assert has_doc is True
            assert doc_path is None
            assert needs_update is False

    @patch('docs_indexer.get_project_root')
    def test_check_documentation_requirement_existing_doc(self, mock_get_root):
        """Test checking file with existing documentation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_get_root.return_value = Path(temp_dir)
            ai_docs_path = Path(temp_dir) / "ai_docs"
            ai_docs_path.mkdir()

            # Create source file
            source_file = Path(temp_dir) / "src" / "test.py"
            source_file.parent.mkdir()
            source_file.write_text("# Test code")

            # Create documentation
            doc_dir = ai_docs_path / "_absolute_docs" / "src"
            doc_dir.mkdir(parents=True)
            doc_file = doc_dir / "test.py.md"
            doc_file.write_text("# Test documentation")

            has_doc, doc_path, needs_update = check_documentation_requirement(
                source_file, ai_docs_path
            )

            assert has_doc is True
            assert doc_path == str(doc_file)
            assert needs_update is False

    @patch('docs_indexer.get_project_root')
    def test_check_documentation_requirement_no_doc(self, mock_get_root):
        """Test checking file without documentation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_get_root.return_value = Path(temp_dir)
            ai_docs_path = Path(temp_dir) / "ai_docs"
            ai_docs_path.mkdir()

            # Create source file only
            source_file = Path(temp_dir) / "src" / "test.py"
            source_file.parent.mkdir()
            source_file.write_text("# Test code")

            has_doc, doc_path, needs_update = check_documentation_requirement(
                source_file, ai_docs_path
            )

            assert has_doc is False
            assert doc_path.endswith("_absolute_docs/src/test.py.md")
            assert needs_update is True

    @patch('docs_indexer.get_project_root')
    def test_check_documentation_requirement_outdated_doc(self, mock_get_root):
        """Test checking file with outdated documentation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_get_root.return_value = Path(temp_dir)
            ai_docs_path = Path(temp_dir) / "ai_docs"
            ai_docs_path.mkdir()

            # Create documentation first
            doc_dir = ai_docs_path / "_absolute_docs" / "src"
            doc_dir.mkdir(parents=True)
            doc_file = doc_dir / "test.py.md"
            doc_file.write_text("# Test documentation")

            # Create source file after documentation (newer)
            import time
            time.sleep(0.1)  # Ensure different timestamps
            source_file = Path(temp_dir) / "src" / "test.py"
            source_file.parent.mkdir()
            source_file.write_text("# Test code")

            has_doc, doc_path, needs_update = check_documentation_requirement(
                source_file, ai_docs_path
            )

            assert has_doc is True
            assert doc_path == str(doc_file)
            assert needs_update is True


class TestMoveToObsolete:
    """Test moving documentation to obsolete."""

    def test_move_to_obsolete_existing_doc(self):
        """Test moving existing documentation to obsolete."""
        with tempfile.TemporaryDirectory() as temp_dir:
            ai_docs_path = Path(temp_dir)

            # Create absolute docs structure
            abs_docs = ai_docs_path / "_absolute_docs" / "src"
            abs_docs.mkdir(parents=True)
            doc_file = abs_docs / "test.py.md"
            doc_file.write_text("# Test documentation")

            # Move to obsolete
            move_to_obsolete(doc_file, ai_docs_path)

            # Check file was moved
            assert not doc_file.exists()

            obsolete_file = ai_docs_path / "_obsolete_docs" / "src" / "test.py.md"
            assert obsolete_file.exists()
            assert obsolete_file.read_text() == "# Test documentation"

            # Check timestamp file was created
            timestamp_file = obsolete_file.with_suffix('.obsolete')
            assert timestamp_file.exists()
            content = timestamp_file.read_text()
            assert "Moved to obsolete:" in content

    def test_move_to_obsolete_nonexistent_doc(self):
        """Test moving non-existent documentation (should not error)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            ai_docs_path = Path(temp_dir)
            nonexistent = ai_docs_path / "_absolute_docs" / "fake.md"

            # Should not raise error
            move_to_obsolete(nonexistent, ai_docs_path)

    def test_move_to_obsolete_creates_directories(self):
        """Test that move_to_obsolete creates necessary directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            ai_docs_path = Path(temp_dir)

            # Create deeply nested doc
            deep_path = ai_docs_path / "_absolute_docs" / "deep" / "nested" / "path"
            deep_path.mkdir(parents=True)
            doc_file = deep_path / "test.md"
            doc_file.write_text("# Deep documentation")

            # Move to obsolete
            move_to_obsolete(doc_file, ai_docs_path)

            # Check directory structure was created
            obsolete_file = ai_docs_path / "_obsolete_docs" / "deep" / "nested" / "path" / "test.md"
            assert obsolete_file.exists()
            assert obsolete_file.read_text() == "# Deep documentation"


class TestIntegration:
    """Integration tests for documentation indexer."""

    def test_full_documentation_workflow(self):
        """Test complete documentation indexing workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            ai_docs_path = Path(temp_dir)

            # Create complex documentation structure
            structure = {
                "api-docs/endpoints.md": "# API Endpoints",
                "guides/setup.md": "# Setup Guide",
                "guides/deployment.md": "# Deployment",
                "_absolute_docs/src/main.py.md": "# Main module",
                "_absolute_docs/src/utils.py.md": "# Utilities",
                "_obsolete_docs/old/legacy.md": "# Legacy docs"
            }

            for file_path, content in structure.items():
                full_path = ai_docs_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)

            # Run full index update
            result = update_index(ai_docs_path)

            # Verify comprehensive results
            assert result["total_files"] == 6
            assert result["total_directories"] == 6  # api-docs, guides, _absolute_docs, src (2x), _obsolete_docs, old

            # Check categories
            assert len(result["categories"]) == 6
            assert "api-docs" in result["categories"]
            assert "guides" in result["categories"]

            # Check absolute docs tracking
            tracked = result["absolute_docs"]["tracked_files"]
            assert "src/main.py" in tracked
            assert "src/utils.py" in tracked

            # Check obsolete docs
            obsolete = result["absolute_docs"]["obsolete_docs"]
            assert len(obsolete) == 1
            assert obsolete[0]["path"] == "_obsolete_docs/old/legacy.md"

            # Check structure
            structure = result["structure"]
            assert "api-docs" in structure
            assert "guides" in structure
            assert "_absolute_docs" in structure
            assert "_obsolete_docs" in structure

            # Verify index.json was created
            index_file = ai_docs_path / "index.json"
            assert index_file.exists()

            # Verify JSON is valid and matches result
            with open(index_file) as f:
                saved_data = json.load(f)

            assert saved_data["total_files"] == result["total_files"]
            assert saved_data["total_directories"] == result["total_directories"]

    @patch('docs_indexer.get_project_root')
    def test_documentation_requirement_workflow(self, mock_get_root):
        """Test complete documentation requirement checking workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_get_root.return_value = Path(temp_dir)
            ai_docs_path = Path(temp_dir) / "ai_docs"
            ai_docs_path.mkdir()

            # Create project structure
            src_dir = Path(temp_dir) / "src"
            src_dir.mkdir()

            # Test file without documentation
            test_file = src_dir / "new_module.py"
            test_file.write_text("# New module")

            has_doc, doc_path, needs_update = check_documentation_requirement(
                test_file, ai_docs_path
            )

            assert has_doc is False
            assert needs_update is True

            # Create documentation
            doc_file = Path(doc_path)
            doc_file.parent.mkdir(parents=True, exist_ok=True)
            doc_file.write_text("# Documentation for new module")

            # Check again
            has_doc, doc_path, needs_update = check_documentation_requirement(
                test_file, ai_docs_path
            )

            assert has_doc is True
            assert needs_update is False

            # Update source file to make doc outdated
            import time
            time.sleep(0.1)
            test_file.write_text("# Updated new module")

            has_doc, doc_path, needs_update = check_documentation_requirement(
                test_file, ai_docs_path
            )

            assert has_doc is True
            assert needs_update is True

            # Test moving to obsolete when source is deleted
            test_file.unlink()
            move_to_obsolete(doc_file, ai_docs_path)

            assert not doc_file.exists()
            obsolete_file = ai_docs_path / "_obsolete_docs" / "src" / "new_module.py.md"
            assert obsolete_file.exists()


if __name__ == "__main__":
    pytest.main([__file__])