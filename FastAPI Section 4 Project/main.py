# main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.responses import FileResponse
import uvicorn
import os
import asyncio
import tempfile

app = FastAPI(title="Students Collaboration app")

# clients: username -> WebSocket
clients: dict[str, WebSocket] = {}

# Put uploads outside the project tree (system temp dir) to avoid triggering
# uvicorn's file-watcher auto-reload that watches your project directory.
UPLOAD_DIR = os.environ.get(
    "UPLOAD_DIR",
    os.path.join(tempfile.gettempdir(), "fastapi_uploads")
)
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await websocket.accept()
    clients[username] = websocket
    print(f"{username} connected. Current clients: {list(clients.keys())}")
    try:
        while True:
            data = await websocket.receive_text()
            print(f"{username} sent: {data}")

            disconnected = []
            for user, client_ws in list(clients.items()):
                if user == username:
                    continue
                try:
                    await client_ws.send_text(f"{username}: {data}")
                except Exception as e:
                    print(f"Failed to send to {user}: {e}")
                    disconnected.append(user)

            for user in disconnected:
                clients.pop(user, None)

    except WebSocketDisconnect:
        print(f"{username} disconnected")
        clients.pop(username, None)


@app.post("/upload_and_notify")
async def upload_and_notify(file: UploadFile = File(...)):
    # Save file to UPLOAD_DIR (outside project)
    filename = os.path.basename(file.filename)
    file_path = os.path.join(UPLOAD_DIR, filename)

    # read & write (non-blocking for the async route)
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)
    await file.close()  # ensure stream released

    # notify clients in background so the HTTP POST returns quickly
    async def notify():
        disconnected = []
        for user, ws in list(clients.items()):
            try:
                await ws.send_text(
                    f"📂 New file uploaded: {filename} (download at /files/{filename})"
                )
            except Exception as e:
                print(f"❌ Failed to notify {user}: {e}")
                disconnected.append(user)
        for user in disconnected:
            clients.pop(user, None)

    asyncio.create_task(notify())

    return {"msg": "File uploaded & notified", "filename": filename, "url": f"/files/{filename}"}


from fastapi.responses import FileResponse

@app.get("/files/{filename}")
def get_file(filename: str):
    file_path = os.path.join("uploads", filename)
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    return FileResponse(
        file_path,
        media_type="application/octet-stream",
        filename=filename
    )



@app.get("/get_connected_users")
def get_connected_users():
    return {"users": list(clients.keys())}


@app.get("/")
def home_page():
    return {"message": "You are at Home Page"}


if __name__ == "__main__":

    uvicorn.run("main:app", host="127.0.0.1", port=4000, reload=False)
