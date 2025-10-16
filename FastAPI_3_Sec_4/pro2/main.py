from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI()

# ----------------- Status -----------------
@app.get("/status")
async def status():
    return {"message": "Server is running ✅"}

# ----------------- Feedback -----------------
class Feedback(BaseModel):
    name: str
    feedback: str

@app.post("/feedback")
async def feedback(data: Feedback):
    print(f"Feedback from {data.name}: {data.feedback}")
    return {"message": "Thanks for your feedback!"}

# ----------------- WebSocket -----------------
class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for conn in self.active_connections:
            await conn.send_text(message)

manager = ConnectionManager()
# ----------------- WebSocket (continued) -----------------
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()  # wait for client message
            await manager.broadcast(f"User says: {data}")  # broadcast to all
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("A user left the chat")

# ----------------- Streaming Large File -----------------
def iterfile(file_path: str):
    # Read file in chunks to stream
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):  # 1 MB chunks
            yield chunk

@app.get("/download")
def download_file():
    file_path = "large_file.zip"  # make sure this file exists
    return StreamingResponse(iterfile(file_path), media_type="application/octet-stream")


@app.get("/hello_world")
def hello_world():
    return "hello world"