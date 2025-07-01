"""
SSE (Server-Sent Events) Support for File Watcher

This module provides SSE capabilities for real-time file change notifications
through MCP's streaming capabilities.
"""
import asyncio
import json
import logging
from typing import Dict, Any, AsyncGenerator, Set
from datetime import datetime
from fastapi import Request
from fastapi.responses import StreamingResponse
from app.tools.file_watcher import file_watcher_manager, FileWatcherEvent

logger = logging.getLogger(__name__)

class SSEFileWatcherNotifier:
    """Manages SSE connections for file watcher notifications."""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[asyncio.Queue]] = {}
        self.client_watchers: Dict[str, Set[str]] = {}  # client_id -> watcher_ids
        self._lock = asyncio.Lock()
    
    async def add_client(self, client_id: str, watcher_ids: list = None) -> asyncio.Queue:
        """Add a new SSE client for file watcher notifications."""
        async with self._lock:
            if client_id not in self.active_connections:
                self.active_connections[client_id] = set()
                self.client_watchers[client_id] = set(watcher_ids or [])
            
            # Create message queue for this client
            queue = asyncio.Queue(maxsize=100)  # Limit queue size
            self.active_connections[client_id].add(queue)
            
            logger.info(f"Added SSE client '{client_id}' for watchers: {watcher_ids}")
            return queue
    
    async def remove_client(self, client_id: str, queue: asyncio.Queue):
        """Remove an SSE client."""
        async with self._lock:
            if client_id in self.active_connections:
                self.active_connections[client_id].discard(queue)
                if not self.active_connections[client_id]:
                    del self.active_connections[client_id]
                    if client_id in self.client_watchers:
                        del self.client_watchers[client_id]
            
            logger.info(f"Removed SSE client '{client_id}'")
    
    async def broadcast_event(self, watcher_id: str, event: FileWatcherEvent):
        """Broadcast file watcher event to subscribed SSE clients."""
        message = {
            "type": "file_change",
            "watcher_id": watcher_id,
            "event": event.to_dict(),
            "timestamp": datetime.now().isoformat()
        }
        
        dead_queues = []
        
        async with self._lock:
            for client_id, queues in self.active_connections.items():
                # Check if client is subscribed to this watcher
                if not self.client_watchers.get(client_id) or watcher_id in self.client_watchers[client_id]:
                    for queue in queues:
                        try:
                            queue.put_nowait(message)
                        except asyncio.QueueFull:
                            logger.warning(f"Queue full for client '{client_id}', dropping message")
                        except Exception as e:
                            logger.error(f"Error queuing message for client '{client_id}': {e}")
                            dead_queues.append((client_id, queue))
        
        # Clean up dead queues
        for client_id, queue in dead_queues:
            await self.remove_client(client_id, queue)
    
    async def send_status_update(self, watcher_id: str, status: str, details: Dict[str, Any] = None):
        """Send status update to SSE clients."""
        message = {
            "type": "watcher_status",
            "watcher_id": watcher_id,
            "status": status,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        
        async with self._lock:
            for client_id, queues in self.active_connections.items():
                if not self.client_watchers.get(client_id) or watcher_id in self.client_watchers[client_id]:
                    for queue in queues:
                        try:
                            queue.put_nowait(message)
                        except asyncio.QueueFull:
                            logger.warning(f"Queue full for client '{client_id}', dropping status message")
                        except Exception:
                            pass

# Global SSE notifier
sse_notifier = SSEFileWatcherNotifier()

async def setup_watcher_sse_callback(watcher_id: str):
    """Setup SSE callback for a file watcher."""
    async def sse_callback(event: FileWatcherEvent):
        await sse_notifier.broadcast_event(watcher_id, event)
    
    file_watcher_manager.add_event_callback(watcher_id, sse_callback)

async def file_watcher_sse_stream(client_id: str, watcher_ids: list = None) -> AsyncGenerator[str, None]:
    """Generate SSE stream for file watcher events."""
    queue = await sse_notifier.add_client(client_id, watcher_ids)
    
    try:
        # Send initial connection message
        yield f"data: {json.dumps({'type': 'connected', 'client_id': client_id, 'timestamp': datetime.now().isoformat()})}\n\n"
        
        while True:
            try:
                # Wait for message with timeout
                message = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield f"data: {json.dumps(message)}\n\n"
            except asyncio.TimeoutError:
                # Send heartbeat to keep connection alive
                yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.now().isoformat()})}\n\n"
            except Exception as e:
                logger.error(f"Error in SSE stream for client '{client_id}': {e}")
                break
    
    except Exception as e:
        logger.error(f"Error in file watcher SSE stream: {e}")
    
    finally:
        await sse_notifier.remove_client(client_id, queue)

def create_sse_response(client_id: str, watcher_ids: list = None) -> StreamingResponse:
    """Create an SSE streaming response for file watcher events."""
    return StreamingResponse(
        file_watcher_sse_stream(client_id, watcher_ids),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
        }
    )
