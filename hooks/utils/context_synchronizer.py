#!/usr/bin/env python3
"""
Context Synchronization Module for Real-Time Hook Enhancement

This module implements real-time context synchronization between hooks,
providing shared cache management, conflict resolution, and performance optimization.

Task ID: de7621a4-df75-4d03-a967-8fb743b455f1 (Phase 2)
Architecture Reference: Real-Time Context Injection System
"""

import os
import json
import time
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List, Set
from dataclasses import dataclass, asdict
from threading import Lock
from enum import Enum

# Import cache manager
from .cache_manager import SessionContextCache
from .mcp_client import OptimizedMCPClient

# Configure logging
logger = logging.getLogger(__name__)

class ConflictResolutionStrategy(Enum):
    """Strategies for resolving context conflicts."""
    LATEST_WINS = "latest_wins"
    MERGE_COMPATIBLE = "merge_compatible"
    MANUAL_REVIEW = "manual_review"
    PRIORITY_BASED = "priority_based"

@dataclass
class ContextChange:
    """Represents a context change event."""
    change_id: str
    timestamp: float
    source: str  # pre_tool_hook, post_tool_hook, mcp_direct
    operation: str  # create, update, delete, sync
    context_type: str  # task, branch, project, global
    context_id: str
    changes: Dict[str, Any]
    priority: int = 1  # 1-5, higher = more important
    requires_sync: bool = True

@dataclass
class SynchronizationConfig:
    """Configuration for context synchronization."""
    enable_real_time_sync: bool = True
    conflict_resolution: ConflictResolutionStrategy = ConflictResolutionStrategy.LATEST_WINS
    sync_timeout_ms: int = 2000
    max_pending_changes: int = 100
    batch_sync_interval_ms: int = 500
    enable_change_broadcast: bool = True


class ConflictResolver:
    """Handles context synchronization conflicts."""
    
    def __init__(self, strategy: ConflictResolutionStrategy):
        self.strategy = strategy
        self.resolution_history = []
    
    async def resolve_conflicts(self, conflicts: List[Dict]) -> List[ContextChange]:
        """
        Resolve context conflicts using the configured strategy.
        
        Args:
            conflicts: List of conflicting changes
            
        Returns:
            List of resolved changes to apply
        """
        if not conflicts:
            return []
        
        logger.info(f"Resolving {len(conflicts)} conflicts using strategy: {self.strategy.value}")
        
        if self.strategy == ConflictResolutionStrategy.LATEST_WINS:
            return await self._resolve_latest_wins(conflicts)
        elif self.strategy == ConflictResolutionStrategy.MERGE_COMPATIBLE:
            return await self._resolve_merge_compatible(conflicts)
        elif self.strategy == ConflictResolutionStrategy.PRIORITY_BASED:
            return await self._resolve_priority_based(conflicts)
        else:  # MANUAL_REVIEW
            return await self._resolve_manual_review(conflicts)
    
    async def _resolve_latest_wins(self, conflicts: List[Dict]) -> List[ContextChange]:
        """Resolve conflicts by taking the latest change."""
        # Group conflicts by context_id
        conflict_groups = {}
        for conflict in conflicts:
            context_key = f"{conflict['context_type']}:{conflict['context_id']}"
            if context_key not in conflict_groups:
                conflict_groups[context_key] = []
            conflict_groups[context_key].append(conflict)
        
        resolved_changes = []
        for context_key, group in conflict_groups.items():
            # Sort by timestamp and take the latest
            latest_conflict = sorted(group, key=lambda x: x['timestamp'], reverse=True)[0]
            resolved_changes.append(ContextChange(**latest_conflict))
            
            # Log resolution
            self._log_resolution(context_key, "latest_wins", len(group), latest_conflict['change_id'])
        
        return resolved_changes
    
    async def _resolve_merge_compatible(self, conflicts: List[Dict]) -> List[ContextChange]:
        """Resolve conflicts by merging compatible changes."""
        # Group conflicts by context_id
        conflict_groups = {}
        for conflict in conflicts:
            context_key = f"{conflict['context_type']}:{conflict['context_id']}"
            if context_key not in conflict_groups:
                conflict_groups[context_key] = []
            conflict_groups[context_key].append(conflict)
        
        resolved_changes = []
        for context_key, group in conflict_groups.items():
            if len(group) == 1:
                # No conflict, just apply the change
                resolved_changes.append(ContextChange(**group[0]))
            else:
                # Try to merge changes
                merged_change = await self._merge_changes(group)
                if merged_change:
                    resolved_changes.append(merged_change)
                    self._log_resolution(context_key, "merge_compatible", len(group), merged_change.change_id)
                else:
                    # Fall back to latest wins
                    latest = sorted(group, key=lambda x: x['timestamp'], reverse=True)[0]
                    resolved_changes.append(ContextChange(**latest))
                    self._log_resolution(context_key, "merge_fallback", len(group), latest['change_id'])
        
        return resolved_changes
    
    async def _resolve_priority_based(self, conflicts: List[Dict]) -> List[ContextChange]:
        """Resolve conflicts based on priority levels."""
        # Group conflicts by context_id
        conflict_groups = {}
        for conflict in conflicts:
            context_key = f"{conflict['context_type']}:{conflict['context_id']}"
            if context_key not in conflict_groups:
                conflict_groups[context_key] = []
            conflict_groups[context_key].append(conflict)
        
        resolved_changes = []
        for context_key, group in conflict_groups.items():
            # Sort by priority (highest first), then by timestamp (latest first)
            highest_priority = sorted(
                group, 
                key=lambda x: (x.get('priority', 1), x['timestamp']), 
                reverse=True
            )[0]
            
            resolved_changes.append(ContextChange(**highest_priority))
            self._log_resolution(context_key, "priority_based", len(group), highest_priority['change_id'])
        
        return resolved_changes
    
    async def _resolve_manual_review(self, conflicts: List[Dict]) -> List[ContextChange]:
        """Mark conflicts for manual review (placeholder)."""
        # In a real implementation, this would queue conflicts for manual review
        # For now, we'll fall back to latest wins with logging
        logger.warning(f"Manual review required for {len(conflicts)} conflicts - falling back to latest wins")
        return await self._resolve_latest_wins(conflicts)
    
    async def _merge_changes(self, changes: List[Dict]) -> Optional[ContextChange]:
        """
        Attempt to merge compatible changes.
        
        This is a simplified merge that combines non-overlapping field updates.
        """
        if not changes:
            return None
        
        # Start with the earliest change as base
        base_change = min(changes, key=lambda x: x['timestamp'])
        merged_changes = base_change['changes'].copy()
        
        # Try to merge subsequent changes
        for change in changes:
            if change == base_change:
                continue
            
            change_data = change['changes']
            
            # Check for field conflicts
            conflicting_fields = set(merged_changes.keys()) & set(change_data.keys())
            
            if conflicting_fields:
                # Can't safely merge if there are field conflicts
                logger.debug(f"Cannot merge changes due to conflicting fields: {conflicting_fields}")
                return None
            
            # Merge non-conflicting fields
            merged_changes.update(change_data)
        
        # Create merged change
        return ContextChange(
            change_id=f"merged_{int(time.time())}_{base_change['change_id'][:8]}",
            timestamp=time.time(),
            source="conflict_resolver",
            operation="update",
            context_type=base_change['context_type'],
            context_id=base_change['context_id'],
            changes=merged_changes,
            priority=max(c.get('priority', 1) for c in changes)
        )
    
    def _log_resolution(self, context_key: str, strategy: str, conflict_count: int, winning_change_id: str):
        """Log conflict resolution for audit purposes."""
        resolution_entry = {
            'timestamp': datetime.now().isoformat(),
            'context_key': context_key,
            'strategy': strategy,
            'conflict_count': conflict_count,
            'winning_change_id': winning_change_id
        }
        
        self.resolution_history.append(resolution_entry)
        
        # Keep only last 100 resolutions
        if len(self.resolution_history) > 100:
            self.resolution_history = self.resolution_history[-100:]
        
        logger.info(f"Resolved conflict for {context_key} using {strategy}")


class ContextSynchronizer:
    """Main context synchronization manager."""
    
    def __init__(self, config: Optional[SynchronizationConfig] = None):
        self.config = config or SynchronizationConfig()
        self.cache = SessionContextCache()
        self.mcp_client = OptimizedMCPClient()
        self.conflict_resolver = ConflictResolver(self.config.conflict_resolution)
        
        # Synchronization state
        self.sync_lock = Lock()
        self.pending_changes: List[ContextChange] = []
        self.change_subscribers: Set[str] = set()
        self.last_sync_time = time.time()
        
        # Performance tracking
        self.sync_stats = {
            'total_syncs': 0,
            'successful_syncs': 0,
            'conflicts_resolved': 0,
            'average_sync_time_ms': 0
        }
    
    async def sync_context_changes(self, changes: List[ContextChange]) -> bool:
        """
        Synchronize context changes across the system.
        
        This is the main entry point for context synchronization.
        """
        if not changes or not self.config.enable_real_time_sync:
            return True
        
        start_time = time.time()
        
        try:
            async with asyncio.timeout(self.config.sync_timeout_ms / 1000):
                # Step 1: Add to pending changes
                with self.sync_lock:
                    self.pending_changes.extend(changes)
                    
                    # Limit pending changes to prevent memory issues
                    if len(self.pending_changes) > self.config.max_pending_changes:
                        self.pending_changes = self.pending_changes[-self.config.max_pending_changes:]
                
                # Step 2: Detect and resolve conflicts
                conflicts = self._detect_conflicts(changes)
                if conflicts:
                    logger.info(f"Detected {len(conflicts)} conflicts in context changes")
                    resolved_changes = await self.conflict_resolver.resolve_conflicts(conflicts)
                    self.sync_stats['conflicts_resolved'] += len(conflicts)
                else:
                    resolved_changes = changes
                
                # Step 3: Apply changes to shared cache
                await self._apply_changes_to_cache(resolved_changes)
                
                # Step 4: Broadcast changes if enabled
                if self.config.enable_change_broadcast:
                    await self._broadcast_context_updates(resolved_changes)
                
                # Step 5: Update statistics
                sync_time_ms = (time.time() - start_time) * 1000
                self._update_sync_stats(sync_time_ms, True)
                
                logger.info(f"Context synchronization completed in {sync_time_ms:.2f}ms")
                return True
                
        except asyncio.TimeoutError:
            logger.error(f"Context synchronization timed out after {self.config.sync_timeout_ms}ms")
            self._update_sync_stats((time.time() - start_time) * 1000, False)
            return False
        except Exception as e:
            logger.error(f"Context synchronization failed: {e}")
            self._update_sync_stats((time.time() - start_time) * 1000, False)
            return False
    
    def add_context_change(self, 
                          source: str,
                          operation: str,
                          context_type: str,
                          context_id: str,
                          changes: Dict[str, Any],
                          priority: int = 1) -> ContextChange:
        """
        Add a new context change to the synchronization queue.
        
        This is a convenience method for creating and queuing context changes.
        """
        change = ContextChange(
            change_id=f"{source}_{int(time.time())}_{hash(str(changes)) % 10000:04d}",
            timestamp=time.time(),
            source=source,
            operation=operation,
            context_type=context_type,
            context_id=context_id,
            changes=changes,
            priority=priority
        )
        
        with self.sync_lock:
            self.pending_changes.append(change)
        
        logger.debug(f"Added context change: {change.change_id}")
        return change
    
    async def sync_pending_changes(self) -> bool:
        """
        Synchronize all pending context changes.
        
        This method processes the queue of pending changes.
        """
        if not self.pending_changes:
            return True
        
        with self.sync_lock:
            changes_to_sync = self.pending_changes.copy()
            self.pending_changes.clear()
        
        return await self.sync_context_changes(changes_to_sync)
    
    def _detect_conflicts(self, changes: List[ContextChange]) -> List[Dict]:
        """
        Detect conflicts in context changes.
        
        Conflicts occur when multiple changes target the same context within
        a short time window.
        """
        conflicts = []
        change_groups = {}
        
        # Group changes by context
        for change in changes:
            context_key = f"{change.context_type}:{change.context_id}"
            if context_key not in change_groups:
                change_groups[context_key] = []
            change_groups[context_key].append(asdict(change))
        
        # Identify conflicts (multiple changes to same context)
        for context_key, group in change_groups.items():
            if len(group) > 1:
                # Check if changes are close in time (within 5 seconds)
                timestamps = [c['timestamp'] for c in group]
                time_span = max(timestamps) - min(timestamps)
                
                if time_span <= 5.0:  # 5 seconds window
                    conflicts.extend(group)
                    logger.debug(f"Conflict detected for {context_key}: {len(group)} changes in {time_span:.2f}s")
        
        return conflicts
    
    async def _apply_changes_to_cache(self, changes: List[ContextChange]) -> None:
        """Apply resolved changes to the shared cache."""
        for change in changes:
            try:
                cache_key = f"{change.context_type}_{change.context_id}"
                
                if change.operation == 'delete':
                    self.cache.delete(cache_key)
                    logger.debug(f"Deleted cache entry: {cache_key}")
                else:
                    # Get existing cached data
                    existing_data = self.cache.get(cache_key) or {}
                    
                    # Apply changes
                    if isinstance(existing_data, dict):
                        existing_data.update(change.changes)
                    else:
                        existing_data = change.changes
                    
                    # Update timestamp
                    if isinstance(existing_data, dict):
                        existing_data['last_sync'] = datetime.now().isoformat()
                    
                    # Cache with appropriate TTL based on context type
                    ttl = self._get_cache_ttl(change.context_type)
                    self.cache.set(cache_key, existing_data, ttl)
                    
                    logger.debug(f"Updated cache entry: {cache_key}")
                    
            except Exception as e:
                logger.warning(f"Failed to apply change {change.change_id} to cache: {e}")
    
    async def _broadcast_context_updates(self, changes: List[ContextChange]) -> None:
        """
        Broadcast context updates to interested parties.
        
        This is a placeholder for future real-time notification system.
        """
        if not self.config.enable_change_broadcast or not changes:
            return
        
        # Create broadcast message
        broadcast_message = {
            'timestamp': datetime.now().isoformat(),
            'change_count': len(changes),
            'changes': [
                {
                    'change_id': c.change_id,
                    'context_type': c.context_type,
                    'context_id': c.context_id,
                    'operation': c.operation,
                    'source': c.source
                }
                for c in changes
            ]
        }
        
        # Log broadcast (in a real system, this would send to subscribers)
        logger.info(f"Broadcasting {len(changes)} context updates")
        
        # Store broadcast log for debugging
        try:
            from .env_loader import get_ai_data_path
            
            broadcast_log_path = get_ai_data_path() / 'context_broadcasts.json'
            
            if broadcast_log_path.exists():
                with open(broadcast_log_path, 'r') as f:
                    try:
                        broadcast_data = json.load(f)
                    except (json.JSONDecodeError, ValueError):
                        broadcast_data = []
            else:
                broadcast_data = []
            
            broadcast_data.append(broadcast_message)
            
            # Keep only last 50 broadcasts
            if len(broadcast_data) > 50:
                broadcast_data = broadcast_data[-50:]
            
            with open(broadcast_log_path, 'w') as f:
                json.dump(broadcast_data, f, indent=2)
                
        except Exception as e:
            logger.warning(f"Failed to log context broadcast: {e}")
    
    def _get_cache_ttl(self, context_type: str) -> int:
        """Get appropriate TTL for context type."""
        ttl_map = {
            'task': 900,      # 15 minutes
            'subtask': 600,   # 10 minutes
            'branch': 1800,   # 30 minutes
            'project': 3600,  # 1 hour
            'global': 7200    # 2 hours
        }
        return ttl_map.get(context_type, 900)  # Default 15 minutes
    
    def _update_sync_stats(self, sync_time_ms: float, success: bool) -> None:
        """Update synchronization statistics."""
        self.sync_stats['total_syncs'] += 1
        
        if success:
            self.sync_stats['successful_syncs'] += 1
        
        # Update average sync time (exponential moving average)
        current_avg = self.sync_stats['average_sync_time_ms']
        self.sync_stats['average_sync_time_ms'] = (current_avg * 0.9) + (sync_time_ms * 0.1)
        
        self.last_sync_time = time.time()
    
    def get_sync_statistics(self) -> Dict[str, Any]:
        """Get synchronization performance statistics."""
        total = self.sync_stats['total_syncs']
        successful = self.sync_stats['successful_syncs']
        
        return {
            **self.sync_stats,
            'success_rate': successful / total if total > 0 else 0,
            'last_sync_time': datetime.fromtimestamp(self.last_sync_time).isoformat(),
            'pending_changes_count': len(self.pending_changes),
            'config': asdict(self.config)
        }


# Factory function and convenience wrappers
def create_context_synchronizer(config: Optional[SynchronizationConfig] = None) -> ContextSynchronizer:
    """Create a context synchronizer instance."""
    return ContextSynchronizer(config)


# Global synchronizer instance for hook usage
_global_synchronizer: Optional[ContextSynchronizer] = None

def get_global_synchronizer() -> ContextSynchronizer:
    """Get the global context synchronizer instance."""
    global _global_synchronizer
    if _global_synchronizer is None:
        _global_synchronizer = create_context_synchronizer()
    return _global_synchronizer


def sync_context_change(source: str,
                       operation: str,
                       context_type: str,
                       context_id: str,
                       changes: Dict[str, Any],
                       priority: int = 1) -> bool:
    """
    Synchronous wrapper for adding and syncing a single context change.
    
    This provides a simple interface for hooks to sync context changes.
    """
    synchronizer = get_global_synchronizer()
    
    try:
        # Add the change
        change = synchronizer.add_context_change(
            source=source,
            operation=operation,
            context_type=context_type,
            context_id=context_id,
            changes=changes,
            priority=priority
        )
        
        # Sync immediately if real-time sync is enabled
        if synchronizer.config.enable_real_time_sync:
            try:
                loop = asyncio.get_running_loop()
                # If already in an event loop, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, synchronizer.sync_context_changes([change]))
                    return future.result(timeout=2.0)
            except RuntimeError:
                # No event loop is running, create a new one
                return asyncio.run(synchronizer.sync_context_changes([change]))
        else:
            return True  # Change queued for later sync
            
    except Exception as e:
        logger.error(f"Failed to sync context change: {e}")
        return False


if __name__ == "__main__":
    # Test the context synchronizer
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Context Synchronizer")
    parser.add_argument('--stats', action='store_true', help='Show synchronization statistics')
    parser.add_argument('--test', action='store_true', help='Run synchronization test')
    
    args = parser.parse_args()
    
    if args.stats:
        synchronizer = get_global_synchronizer()
        stats = synchronizer.get_sync_statistics()
        print(json.dumps(stats, indent=2))
    
    if args.test:
        # Test synchronization
        print("Testing context synchronization...")
        
        success = sync_context_change(
            source="test",
            operation="update",
            context_type="task",
            context_id="test-task-123",
            changes={"status": "in_progress", "test": True},
            priority=3
        )
        
        if success:
            print("✅ Context synchronization test passed")
        else:
            print("❌ Context synchronization test failed")
            exit(1)