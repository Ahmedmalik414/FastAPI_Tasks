from fastapi import WebSocket
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        # Accept the connection (handshake)
        await websocket.accept()
        self.active_connections.append(websocket)
        print("New user connected, total:", len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print("User disconnected, total:", len(self.active_connections))

    async def broadcast(self, message: str):
        # Send message to all connected users
        for connection in self.active_connections:
            await connection.send_text(message)



