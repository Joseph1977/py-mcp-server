# File Watcher Implementation Documentation

## Overview

The File Watcher tool integration adds real-time file system monitoring capabilities to the MCP server, leveraging both MCP's tool system and SSE (Server-Sent Events) for live notifications.

## Architecture

### Components

1. **File Watcher Core** (`app/tools/file_watcher.py`)
   - `FileWatcherManager`: Central manager for all watchers
   - `AsyncFileEventHandler`: Async-compatible event handler
   - `FileWatcherEvent`: Event data structure

2. **SSE Integration** (`app/tools/file_watcher_sse.py`)
   - `SSEFileWatcherNotifier`: Manages SSE connections
   - Real-time event broadcasting
   - Client connection management

3. **MCP Tools Integration** (`app/main.py`)
   - MCP tool decorators for file watcher operations
   - Integration with FastMCP server

### Key Features

- ✅ **Real-time monitoring**: Uses `watchdog` library for efficient file system events
- ✅ **Pattern filtering**: Support for file patterns, exclusions, and specific files
- ✅ **SSE notifications**: Real-time push notifications via Server-Sent Events
- ✅ **Async-first design**: All operations are async-compatible
- ✅ **Resource management**: Proper cleanup and lifecycle management
- ✅ **Multi-client support**: Multiple SSE clients can connect simultaneously

## MCP Tools

### `create_watcher`
Creates a new file watcher with filtering options.

**Parameters:**
- `watcher_id` (str): Unique identifier for the watcher
- `watch_path` (str): Path to watch (file or directory)
- `file_patterns` (List[str], optional): File patterns to match (e.g., ['*.txt', '*.py'])
- `exclude_patterns` (List[str], optional): Patterns to exclude (e.g., ['*.tmp'])
- `specific_files` (List[str], optional): Specific files to watch (overrides patterns)
- `recursive` (bool): Watch subdirectories recursively (default: True)
- `include_directories` (bool): Include directory events (default: True)
- `auto_start` (bool): Auto-start watching after creation (default: True)

**Example:**
```json
{
  "tool": "create_watcher",
  "arguments": {
    "watcher_id": "my_project_watcher",
    "watch_path": "/path/to/project",
    "file_patterns": ["*.py", "*.js", "*.ts"],
    "exclude_patterns": ["__pycache__", "node_modules", "*.pyc"],
    "recursive": true,
    "auto_start": true
  }
}
```

### `start_watcher_tool`
Starts a stopped file watcher.

### `stop_watcher_tool`
Stops a running file watcher without removing it.

### `remove_watcher_tool`
Completely removes a file watcher.

### `list_watchers_tool`
Lists all file watchers and their status.

### `get_watcher_status_tool`
Gets detailed status information for a specific watcher.

## SSE (Server-Sent Events)

### Endpoint
```
GET /file-watcher/sse?watchers=watcher1,watcher2
```

### Event Types

1. **Connection Events**
   ```json
   {
     "type": "connected",
     "client_id": "uuid-string",
     "timestamp": "2025-07-01T10:30:00Z"
   }
   ```

2. **File Change Events**
   ```json
   {
     "type": "file_change",
     "watcher_id": "my_watcher",
     "event": {
       "event_type": "modified",
       "path": "/full/path/to/file.txt",
       "filename": "file.txt",
       "parent_dir": "/full/path/to",
       "is_directory": false,
       "timestamp": "2025-07-01T10:30:00Z"
     }
   }
   ```

3. **Watcher Status Events**
   ```json
   {
     "type": "watcher_status",
     "watcher_id": "my_watcher",
     "status": "started",
     "details": {},
     "timestamp": "2025-07-01T10:30:00Z"
   }
   ```

4. **Heartbeat Events**
   ```json
   {
     "type": "heartbeat",
     "timestamp": "2025-07-01T10:30:00Z"
   }
   ```

## Integration with Current Implementation

### What's Added

1. **New Dependencies** (in `requirements.txt`):
   ```
   watchdog>=3.0.0
   asyncio-mqtt>=0.16.0
   ```

2. **New MCP Tools** (6 new tools added to the server):
   - `create_watcher`
   - `start_watcher_tool`
   - `stop_watcher_tool`
   - `remove_watcher_tool`
   - `list_watchers_tool`
   - `get_watcher_status_tool`

3. **New HTTP Endpoint**:
   - `/file-watcher/sse` - SSE endpoint for real-time notifications

4. **Updated Server Info**:
   - New endpoint listed in `/info` response
   - Tools list updated to include file watcher tools

### What's Not Broken

✅ **Existing functionality preserved**:
- Weather tool continues to work
- Search tools (Brave/Google) continue to work
- All existing endpoints (`/health`, `/info`, `/ping`) work
- MCP protocol compatibility maintained
- Both stdio and HTTP transport modes supported

✅ **Graceful degradation**:
- If watchdog fails to install, only file watcher tools are affected
- SSE endpoint returns appropriate errors if components fail
- Server continues to function without file watcher capabilities

✅ **Resource management**:
- File watchers are properly cleaned up on server shutdown
- SSE connections are managed and cleaned up
- No memory leaks or resource accumulation

## Potential Issues & Mitigations

### 1. Dependency Issues
**Issue**: `watchdog` library might not install on some systems
**Mitigation**: 
- Graceful error handling in tool calls
- Clear error messages to users
- Server continues without file watcher functionality

### 2. File System Permissions
**Issue**: Watching restricted directories
**Mitigation**:
- Proper error handling with descriptive messages
- Path validation before creating watchers
- Permission check warnings

### 3. Performance Impact
**Issue**: Watching large directories with many files
**Mitigation**:
- Smart filtering with exclude patterns
- Resource usage monitoring
- Configurable limits on number of watchers

### 4. SSE Connection Management
**Issue**: Too many SSE connections or connection leaks
**Mitigation**:
- Connection limits and cleanup
- Dead connection detection
- Heartbeat mechanism for connection health

## Testing

### 1. MCP Tools Testing
Run the test client:
```bash
python test_file_watcher.py
```

### 2. SSE Testing
1. Start server in HTTP mode:
   ```bash
   python run.py
   ```

2. Open `file_watcher_test.html` in a browser

3. Connect to `http://localhost:8001`

### 3. Manual Testing
```bash
# Create watcher for current directory
create_watcher("test", ".", ["*.py"], ["__pycache__"])

# Create some files and watch SSE stream
echo "test" > test_file.py

# Check watcher status
get_watcher_status_tool("test")
```

## Future Enhancements

1. **Batch Events**: Group multiple file changes into batches
2. **Event Filtering**: Server-side filtering of events before SSE
3. **Persistence**: Save watcher configurations to restart after server reboot
4. **Metrics**: Detailed metrics on file system activity
5. **Integration**: Integration with git hooks, CI/CD systems
6. **Security**: Authentication and authorization for SSE endpoints

## Summary

The file watcher implementation adds powerful real-time file monitoring to the MCP server while:
- ✅ Maintaining full backward compatibility
- ✅ Using async/await throughout for performance
- ✅ Providing both MCP tools and SSE for different use cases
- ✅ Including comprehensive error handling and cleanup
- ✅ Supporting flexible filtering and configuration options

The implementation is production-ready and can be safely deployed alongside existing functionality.
