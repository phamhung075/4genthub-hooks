#!/usr/bin/env python3
"""
Task Tracker for Status Line
Tracks active tasks per session and provides status line integration
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
import hashlib


class TaskTracker:
    """Manages task tracking for status line display."""

    def __init__(self, session_id: str = None):
        """Initialize task tracker with session ID."""
        self.session_id = session_id or self._generate_session_id()
        # Use correct path: .claude/data/task_tracking
        self.data_dir = Path(__file__).parent.parent.parent / "data" / "task_tracking"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.tasks_file = self.data_dir / "active_tasks.json"
        self.session_file = self.data_dir / f"session_{self.session_id[:8]}.json"

    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()

    def _load_tasks(self) -> Dict[str, Any]:
        """Load all active tasks."""
        if self.tasks_file.exists():
            try:
                with open(self.tasks_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_tasks(self, tasks: Dict[str, Any]):
        """Save tasks to file."""
        with open(self.tasks_file, 'w') as f:
            json.dump(tasks, f, indent=2, default=str)

    def _load_session_tasks(self) -> List[Dict[str, Any]]:
        """Load tasks for current session."""
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r') as f:
                    data = json.load(f)
                    return data.get('tasks', [])
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def _save_session_tasks(self, tasks: List[Dict[str, Any]]):
        """Save session-specific tasks."""
        session_data = {
            'session_id': self.session_id,
            'created_at': datetime.now().isoformat(),
            'tasks': tasks
        }
        with open(self.session_file, 'w') as f:
            json.dump(session_data, f, indent=2, default=str)

    def add_task(self, task_id: str, title: str, status: str = "pending",
                 assignee: str = None, priority: int = 0, details: str = None):
        """Add a new task to tracking."""
        tasks = self._load_tasks()

        task_data = {
            'id': task_id,
            'title': title,
            'status': status,
            'assignee': assignee,
            'priority': priority,
            'details': details,
            'created_at': datetime.now().isoformat(),
            'session_id': self.session_id,
            'last_updated': datetime.now().isoformat()
        }

        tasks[task_id] = task_data
        self._save_tasks(tasks)

        # Also track in session
        session_tasks = self._load_session_tasks()
        session_tasks.append({
            'task_id': task_id,
            'title': title,
            'status': status,
            'added_at': datetime.now().isoformat()
        })
        self._save_session_tasks(session_tasks)

        return task_data

    def update_task(self, task_id: str, **kwargs):
        """Update an existing task."""
        tasks = self._load_tasks()

        if task_id in tasks:
            tasks[task_id].update(kwargs)
            tasks[task_id]['last_updated'] = datetime.now().isoformat()
            self._save_tasks(tasks)

            # Update session tasks
            session_tasks = self._load_session_tasks()
            for task in session_tasks:
                if task['task_id'] == task_id:
                    if 'status' in kwargs:
                        task['status'] = kwargs['status']
                    if 'title' in kwargs:
                        task['title'] = kwargs['title']
                    break
            self._save_session_tasks(session_tasks)

            return tasks[task_id]
        return None

    def complete_task(self, task_id: str):
        """Mark a task as completed and remove from active tracking."""
        tasks = self._load_tasks()

        if task_id in tasks:
            # Archive the task before removal
            task = tasks[task_id]
            task['completed_at'] = datetime.now().isoformat()
            task['status'] = 'completed'

            # Archive to completed tasks file
            self._archive_task(task)

            # Remove from active tasks
            del tasks[task_id]
            self._save_tasks(tasks)

            # Remove from session tasks
            session_tasks = self._load_session_tasks()
            session_tasks = [t for t in session_tasks if t['task_id'] != task_id]
            self._save_session_tasks(session_tasks)

            return True
        return False

    def _archive_task(self, task: Dict[str, Any]):
        """Archive completed task."""
        archive_file = self.data_dir / "completed_tasks.json"

        if archive_file.exists():
            try:
                with open(archive_file, 'r') as f:
                    archive = json.load(f)
            except (json.JSONDecodeError, IOError):
                archive = []
        else:
            archive = []

        archive.append(task)

        # Keep only last 100 completed tasks
        if len(archive) > 100:
            archive = archive[-100:]

        with open(archive_file, 'w') as f:
            json.dump(archive, f, indent=2, default=str)

    def get_active_tasks(self, session_only: bool = False) -> List[Dict[str, Any]]:
        """Get list of active tasks."""
        if session_only:
            session_tasks = self._load_session_tasks()
            # Get full task data for session tasks
            all_tasks = self._load_tasks()
            active = []
            for st in session_tasks:
                if st['task_id'] in all_tasks:
                    active.append(all_tasks[st['task_id']])
            return active
        else:
            tasks = self._load_tasks()
            return list(tasks.values())

    def get_task_summary(self) -> Dict[str, Any]:
        """Get summary of tasks for status line display."""
        tasks = self.get_active_tasks()
        session_tasks = self.get_active_tasks(session_only=True)

        # Count by status
        status_counts = {
            'pending': 0,
            'in_progress': 0,
            'blocked': 0,
            'review': 0
        }

        for task in tasks:
            status = task.get('status', 'pending')
            if status in status_counts:
                status_counts[status] += 1

        # Get most recent in-progress task
        in_progress = [t for t in tasks if t.get('status') == 'in_progress']
        current_task = None
        if in_progress:
            # Sort by last_updated to get most recent
            in_progress.sort(key=lambda x: x.get('last_updated', ''), reverse=True)
            current_task = in_progress[0]

        return {
            'total': len(tasks),
            'session_count': len(session_tasks),
            'status_counts': status_counts,
            'current_task': current_task,
            'has_blocked': status_counts['blocked'] > 0
        }

    def cleanup_old_sessions(self, hours: int = 24):
        """Clean up old session files."""
        cutoff = datetime.now() - timedelta(hours=hours)

        for file in self.data_dir.glob("session_*.json"):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                created = datetime.fromisoformat(data.get('created_at', ''))
                if created < cutoff:
                    file.unlink()
            except (json.JSONDecodeError, IOError, ValueError):
                # If we can't read it, it's probably corrupted
                file.unlink()

    def format_task_summary(self) -> str:
        """Format task summary for display in hints."""
        summary = self.get_task_summary()

        if summary['total'] == 0:
            return "No active tasks"

        lines = []
        lines.append(f"Total Active Tasks: {summary['total']}")

        # Show current task if exists
        if summary['current_task']:
            lines.append(f"Current: {summary['current_task']['title']}")

        # Show status counts
        status_parts = []
        if summary['status_counts']['in_progress'] > 0:
            status_parts.append(f"In Progress: {summary['status_counts']['in_progress']}")
        if summary['status_counts']['pending'] > 0:
            status_parts.append(f"Pending: {summary['status_counts']['pending']}")
        if summary['status_counts']['blocked'] > 0:
            status_parts.append(f"BLOCKED: {summary['status_counts']['blocked']}")

        if status_parts:
            lines.append(" | ".join(status_parts))

        return "\n".join(lines)


# Singleton instance management
_tracker_instance = None

def get_task_tracker(session_id: str = None) -> TaskTracker:
    """Get or create the task tracker instance."""
    global _tracker_instance
    if _tracker_instance is None or (session_id and _tracker_instance.session_id != session_id):
        _tracker_instance = TaskTracker(session_id)
    return _tracker_instance


def track_task_from_mcp(action: str, task_data: Dict[str, Any], session_id: str = None):
    """Track task operations from MCP calls."""
    tracker = get_task_tracker(session_id)

    if action == "create":
        tracker.add_task(
            task_id=task_data.get('id', ''),
            title=task_data.get('title', 'Untitled Task'),
            status=task_data.get('status', 'pending'),
            assignee=task_data.get('assignees', [None])[0] if task_data.get('assignees') else None,
            details=task_data.get('details', '')
        )
    elif action == "update":
        tracker.update_task(
            task_id=task_data.get('id', ''),
            status=task_data.get('status'),
            title=task_data.get('title')
        )
    elif action == "complete":
        tracker.complete_task(task_data.get('id', ''))


if __name__ == "__main__":
    # Test the tracker
    tracker = TaskTracker()

    # Add test tasks
    task1 = tracker.add_task("test-1", "Implement authentication", "in_progress", "coding-agent")
    task2 = tracker.add_task("test-2", "Write tests", "pending", "test-agent")
    task3 = tracker.add_task("test-3", "Fix bug in login", "blocked")

    # Get summary
    summary = tracker.get_task_summary()
    print(f"Task Summary: {json.dumps(summary, indent=2)}")

    # Format task summary
    status = tracker.format_task_summary()
    print(f"Task Summary:\n{status}")

    # Complete a task
    tracker.complete_task("test-1")

    # Check again
    status = tracker.format_task_summary()
    print(f"\nAfter completion:\n{status}")