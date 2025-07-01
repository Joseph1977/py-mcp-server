"""
File Watcher Tool for MCP Server

This module provides file watching capabilities with real-time notifications
through MCP's SSE (Server-Sent Events) system.
"""
import asyncio
import logging
import os
import fnmatch
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Callable
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
import json
import threading

logger = logging.getLogger(__name__)

class FileWatcherEvent:
    """Represents a file system event with additional metadata."""
    
    def __init__(self, event_type: str, path: str, is_directory: bool = False, 
                 src_path: str = None, timestamp: datetime = None):
        self.event_type = event_type  # created, modified, deleted, moved
        self.path = str(Path(path).resolve())
        self.is_directory = is_directory
        self.src_path = str(Path(src_path).resolve()) if src_path else None
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for JSON serialization."""
        return {
            "event_type": self.event_type,
            "path": self.path,
            "is_directory": self.is_directory,
            "src_path": self.src_path,
            "timestamp": self.timestamp.isoformat(),
            "filename": os.path.basename(self.path),
            "parent_dir": os.path.dirname(self.path)
        }

class AsyncFileEventHandler(FileSystemEventHandler):
    """Async-compatible file system event handler."""
    
    def __init__(self, callback: Callable, filters: Dict[str, Any]):
        super().__init__()
        self.callback = callback
        self.filters = filters
        self.loop = None
        self._setup_filters()
    
    def _setup_filters(self):
        """Setup file filters from configuration."""
        self.file_patterns = self.filters.get('file_patterns', ['*'])
        self.exclude_patterns = self.filters.get('exclude_patterns', [])
        self.include_directories = self.filters.get('include_directories', True)
        self.specific_files = set(self.filters.get('specific_files', []))
        
        # Convert to absolute paths
        if self.specific_files:
            self.specific_files = {str(Path(f).resolve()) for f in self.specific_files}
    
    def _should_process_event(self, event: FileSystemEvent) -> bool:
        """Determine if event should be processed based on filters."""
        path = Path(event.src_path)
        abs_path = str(path.resolve())
        
        # Check if it's a directory and we're excluding directories
        if event.is_directory and not self.include_directories:
            return False
        
        # Check specific files filter
        if self.specific_files and abs_path not in self.specific_files:
            return False
        
        # Check exclude patterns
        filename = path.name
        for pattern in self.exclude_patterns:
            if fnmatch.fnmatch(filename, pattern) or fnmatch.fnmatch(abs_path, pattern):
                return False
        
        # Check include patterns (only if no specific files are specified)
        if not self.specific_files:
            for pattern in self.file_patterns:
                if fnmatch.fnmatch(filename, pattern):
                    return True
            return False  # No patterns matched
        
        return True
    
    def _schedule_callback(self, watcher_event: FileWatcherEvent):
        """Schedule callback in the event loop."""
        if self.loop and not self.loop.is_closed():
            asyncio.run_coroutine_threadsafe(self.callback(watcher_event), self.loop)
    
    def on_created(self, event):
        if self._should_process_event(event):
            watcher_event = FileWatcherEvent("created", event.src_path, event.is_directory)
            self._schedule_callback(watcher_event)
    
    def on_modified(self, event):
        if self._should_process_event(event):
            watcher_event = FileWatcherEvent("modified", event.src_path, event.is_directory)
            self._schedule_callback(watcher_event)
    
    def on_deleted(self, event):
        if self._should_process_event(event):
            watcher_event = FileWatcherEvent("deleted", event.src_path, event.is_directory)
            self._schedule_callback(watcher_event)
    
    def on_moved(self, event):
        if self._should_process_event(event):
            watcher_event = FileWatcherEvent("moved", event.dest_path, event.is_directory, event.src_path)
            self._schedule_callback(watcher_event)

class FileWatcherManager:
    """Manages multiple file watchers with SSE support."""
    
    def __init__(self):
        self.watchers: Dict[str, Dict[str, Any]] = {}
        self.observers: Dict[str, Observer] = {}
        self.event_callbacks: Dict[str, List[Callable]] = {}
        self._lock = threading.Lock()
    
    async def create_watcher(self, watcher_id: str, watch_path: str, 
                           filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new file watcher."""
        if filters is None:
            filters = {}
        
        # Validate path
        path = Path(watch_path)
        if not path.exists():
            raise ValueError(f"Watch path does not exist: {watch_path}")
        
        abs_path = str(path.resolve())
        
        with self._lock:
            if watcher_id in self.watchers:
                raise ValueError(f"Watcher with ID '{watcher_id}' already exists")
            
            # Setup event callback
            async def event_callback(event: FileWatcherEvent):
                await self._handle_file_event(watcher_id, event)
            
            # Create event handler
            handler = AsyncFileEventHandler(event_callback, filters)
            handler.loop = asyncio.get_event_loop()
            
            # Create observer
            observer = Observer()
            observer.schedule(handler, abs_path, recursive=filters.get('recursive', True))
            
            # Store watcher info
            watcher_info = {
                'id': watcher_id,
                'path': abs_path,
                'filters': filters,
                'created': datetime.now(),
                'status': 'created',
                'event_count': 0
            }
            
            self.watchers[watcher_id] = watcher_info
            self.observers[watcher_id] = observer
            self.event_callbacks[watcher_id] = []
            
            logger.info(f"Created file watcher '{watcher_id}' for path: {abs_path}")
            return watcher_info
    
    async def start_watcher(self, watcher_id: str) -> Dict[str, Any]:
        """Start a file watcher."""
        with self._lock:
            if watcher_id not in self.watchers:
                raise ValueError(f"Watcher '{watcher_id}' not found")
            
            observer = self.observers[watcher_id]
            if not observer.is_alive():
                observer.start()
                self.watchers[watcher_id]['status'] = 'running'
                self.watchers[watcher_id]['started'] = datetime.now()
                logger.info(f"Started file watcher '{watcher_id}'")
            
            return self.watchers[watcher_id]
    
    async def stop_watcher(self, watcher_id: str) -> Dict[str, Any]:
        """Stop a file watcher."""
        with self._lock:
            if watcher_id not in self.watchers:
                raise ValueError(f"Watcher '{watcher_id}' not found")
            
            observer = self.observers[watcher_id]
            if observer.is_alive():
                observer.stop()
                observer.join(timeout=5.0)
                self.watchers[watcher_id]['status'] = 'stopped'
                self.watchers[watcher_id]['stopped'] = datetime.now()
                logger.info(f"Stopped file watcher '{watcher_id}'")
            
            return self.watchers[watcher_id]
    
    async def remove_watcher(self, watcher_id: str) -> bool:
        """Remove a file watcher."""
        if watcher_id not in self.watchers:
            return False
        
        # Stop if running (do this BEFORE acquiring the lock)
        await self.stop_watcher(watcher_id)
        
        # Clean up with lock
        with self._lock:
            if watcher_id in self.watchers:
                del self.watchers[watcher_id]
            if watcher_id in self.observers:
                del self.observers[watcher_id]
            if watcher_id in self.event_callbacks:
                del self.event_callbacks[watcher_id]
        
        logger.info(f"Removed file watcher '{watcher_id}'")
        return True
    
    async def list_watchers(self) -> List[Dict[str, Any]]:
        """List all file watchers."""
        with self._lock:
            return list(self.watchers.values())
    
    async def get_watcher_status(self, watcher_id: str) -> Dict[str, Any]:
        """Get status of a specific watcher."""
        with self._lock:
            if watcher_id not in self.watchers:
                raise ValueError(f"Watcher '{watcher_id}' not found")
            
            watcher_info = self.watchers[watcher_id].copy()
            observer = self.observers[watcher_id]
            watcher_info['is_alive'] = observer.is_alive()
            
            return watcher_info
    
    def add_event_callback(self, watcher_id: str, callback: Callable):
        """Add an event callback for a specific watcher."""
        with self._lock:
            if watcher_id in self.event_callbacks:
                self.event_callbacks[watcher_id].append(callback)
    
    def remove_event_callback(self, watcher_id: str, callback: Callable):
        """Remove an event callback for a specific watcher."""
        with self._lock:
            if watcher_id in self.event_callbacks:
                try:
                    self.event_callbacks[watcher_id].remove(callback)
                except ValueError:
                    pass
    
    async def _handle_file_event(self, watcher_id: str, event: FileWatcherEvent):
        """Handle file system events."""
        with self._lock:
            if watcher_id in self.watchers:
                self.watchers[watcher_id]['event_count'] += 1
                self.watchers[watcher_id]['last_event'] = datetime.now()
        
        logger.debug(f"File event in watcher '{watcher_id}': {event.event_type} - {event.path}")
        
        # Call registered callbacks
        callbacks = self.event_callbacks.get(watcher_id, [])
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                logger.error(f"Error in file watcher callback: {e}")
    
    async def cleanup_all(self):
        """Stop and remove all watchers."""
        watcher_ids = list(self.watchers.keys())
        for watcher_id in watcher_ids:
            await self.remove_watcher(watcher_id)

# Global instance
file_watcher_manager = FileWatcherManager()

# Utility functions for MCP tools
async def create_file_watcher(watcher_id: str, watch_path: str, 
                            file_patterns: List[str] = None,
                            exclude_patterns: List[str] = None,
                            specific_files: List[str] = None,
                            recursive: bool = True,
                            include_directories: bool = True) -> Dict[str, Any]:
    """Create a new file watcher with specified parameters."""
    filters = {
        'file_patterns': file_patterns or ['*'],
        'exclude_patterns': exclude_patterns or [],
        'specific_files': specific_files or [],
        'recursive': recursive,
        'include_directories': include_directories
    }
    
    return await file_watcher_manager.create_watcher(watcher_id, watch_path, filters)

async def start_file_watcher(watcher_id: str) -> Dict[str, Any]:
    """Start a file watcher."""
    return await file_watcher_manager.start_watcher(watcher_id)

async def stop_file_watcher(watcher_id: str) -> Dict[str, Any]:
    """Stop a file watcher."""
    return await file_watcher_manager.stop_watcher(watcher_id)

async def remove_file_watcher(watcher_id: str) -> bool:
    """Remove a file watcher."""
    return await file_watcher_manager.remove_watcher(watcher_id)

async def list_file_watchers() -> List[Dict[str, Any]]:
    """List all file watchers."""
    return await file_watcher_manager.list_watchers()

async def get_file_watcher_status(watcher_id: str) -> Dict[str, Any]:
    """Get status of a specific file watcher."""
    return await file_watcher_manager.get_watcher_status(watcher_id)
