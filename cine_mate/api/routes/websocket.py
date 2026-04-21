"""
CineMate API — WebSocket Routes
Real-time progress push for pipeline execution.
"""

import asyncio
import json
from typing import Dict, Set
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from cine_mate.api.schemas import WsProgressMessage

router = APIRouter(tags=["websocket"])


class ConnectionManager:
    """
    Manages WebSocket connections for real-time updates.
    
    Supports:
    - Multiple clients per run_id
    - Broadcasting progress updates to all subscribers
    - Graceful disconnect handling
    """
    
    def __init__(self):
        # run_id -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Global broadcast connections (no run_id filter)
        self.global_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket, run_id: str):
        """Accept a WebSocket connection and subscribe to a run."""
        await websocket.accept()
        if run_id not in self.active_connections:
            self.active_connections[run_id] = set()
        self.active_connections[run_id].add(websocket)
    
    async def connect_global(self, websocket: WebSocket):
        """Accept a WebSocket connection for global broadcasts."""
        await websocket.accept()
        self.global_connections.add(websocket)
    
    def disconnect(self, websocket: WebSocket, run_id: str = None):
        """Remove a WebSocket connection."""
        if run_id and run_id in self.active_connections:
            self.active_connections[run_id].discard(websocket)
            if not self.active_connections[run_id]:
                del self.active_connections[run_id]
        self.global_connections.discard(websocket)
    
    async def broadcast(self, run_id: str, message: WsProgressMessage):
        """Send a progress update to all subscribers of a run + global."""
        msg_json = message.model_dump_json()
        
        # Send to run-specific subscribers
        if run_id in self.active_connections:
            dead_connections = set()
            for conn in self.active_connections[run_id]:
                try:
                    await conn.send_text(msg_json)
                except Exception:
                    dead_connections.add(conn)
            for conn in dead_connections:
                self.disconnect(conn, run_id)
        
        # Send to global subscribers
        dead_global = set()
        for conn in self.global_connections:
            try:
                await conn.send_text(msg_json)
            except Exception:
                dead_global.add(conn)
        for conn in dead_global:
            self.disconnect(conn)


# Singleton manager
manager = ConnectionManager()


@router.websocket("/ws/progress")
async def websocket_progress(websocket: WebSocket):
    """
    WebSocket endpoint for real-time progress updates.
    
    Connects to global broadcast — receives all run updates.
    Send a JSON message with {"run_id": "..."} to subscribe to a specific run.
    
    Usage (JavaScript):
        const ws = new WebSocket('ws://localhost:8000/ws/progress');
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log(data.run_id, data.type, data.status);
        };
        ws.send(JSON.stringify({run_id: 'run_001'}));
    """
    await manager.connect_global(websocket)
    
    try:
        while True:
            # Client can send {"run_id": "..."} to filter (future enhancement)
            data = await websocket.receive_text()
            # Echo back acknowledgment (future: use for subscription management)
            await websocket.send_text(json.dumps({
                "type": "ack",
                "message": "Connected to progress stream",
                "timestamp": datetime.now().isoformat(),
            }))
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.websocket("/ws/run/{run_id}")
async def websocket_run_progress(websocket: WebSocket, run_id: str):
    """
    WebSocket endpoint for a specific run's progress updates.
    
    Only receives updates for the specified run_id.
    
    Usage (JavaScript):
        const ws = new WebSocket('ws://localhost:8000/ws/run/run_001');
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log(data.node_id, data.status);
        };
    """
    await manager.connect(websocket, run_id)
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, run_id)


async def notify_progress(run_id: str, message: WsProgressMessage):
    """
    Helper to send a progress update to WebSocket subscribers.
    
    Call this from the Orchestrator or elsewhere during pipeline execution.
    """
    await manager.broadcast(run_id, message)
