from routes import account, trades, signal
from agent_runner import run_agent_async
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()


connected_clients: list[WebSocket] = []


async def broadcast(data: dict):
    dead = []
    for client in connected_clients:
        try:
            await client.send_json(data)
        except Exception:
            dead.append(client)
    for d in dead:
        if d in connected_clients:
            connected_clients.remove(d)


async def agent_loop():
    while True:
        await run_agent_async(broadcast)
        await asyncio.sleep(900)  # 15 min


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(agent_loop())
    yield
    task.cancel()


app = FastAPI(title="AlgoSentinel API", version="1.0.0", lifespan=lifespan)

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(account.router)
app.include_router(trades.router)
app.include_router(signal.router)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in connected_clients:
            connected_clients.remove(websocket)


@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}
