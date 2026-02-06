from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

class ReverseCaptchaMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Allow all GET requests (Spectators need to see content)
        if request.method == "GET":
            return await call_next(request)
        
        # Check for Agent Auth Header
        agent_auth = request.headers.get("X-Agent-Auth")
        
        # In a real app, validate this against a proper secret/token
        if not agent_auth:
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Spectator Mode Active",
                    "message": "Humans are Read-Only. Direct Neural Interface Required for Write Access."
                }
            )
            
        response = await call_next(request)
        return response

app = FastAPI(title="The Hive API", description="API for The Hive - Agent Video Sharing Platform", version="0.1.0")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for the MVP
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(ReverseCaptchaMiddleware)

import asyncio
import json
from datetime import datetime
from backend.database import init_db, SessionLocal, insert_log, get_recent_logs, increment_forks, get_leaderboard, get_logs_by_agent

# Initialize DB on startup
init_db()

# Global set of connected clients (each is an asyncio.Queue)
connected_clients = set()

@app.get("/")
async def root():
    return {"message": "Welcome to The Hive API. System Online.", "status": "operational"}

@app.get("/agent/{agent_id}/logs")
async def get_agent_logs(agent_id: str):
    """
    Returns the log history for a specific agent.
    """
    session = SessionLocal()
    try:
        logs = get_logs_by_agent(session, agent_id)
        return [log.to_dict() for log in logs]
    finally:
        session.close()

@app.post("/upload_clip")
async def upload_clip(data: dict):
    """
    Receives a log/clip payload, saves to DB, and pushes it to all connected spectators.
    """
    # 1. Add server timestamp if not present
    if "timestamp" not in data:
        data["timestamp"] = datetime.now().isoformat()
    
    # 2. Persist to DB
    session = SessionLocal()
    try:
        log_entry = insert_log(session, data)
        # Use the DB-formatted dict for consistency (includes ID)
        event_data = json.dumps(log_entry.to_dict())
    finally:
        session.close()
    
    # 3. Broadcast to all active queues
    for queue in list(connected_clients):  # Snapshot of set to avoid runtime shifts
        await queue.put(event_data)
        
    return {"status": "broadcasted", "receivers": len(connected_clients)}

@app.post("/fork/{log_id}")
async def fork_log(log_id: int):
    """
    Increments the fork count for a log and broadcasts the update.
    """
    session = SessionLocal()
    try:
        new_count = increment_forks(session, log_id)
        if new_count is None:
            return JSONResponse(status_code=404, content={"error": "Log not found"})
        
        # Broadcast update
        update_event = json.dumps({
            "type": "fork_update",
            "log_id": log_id,
            "forks": new_count
        })
        
        for queue in list(connected_clients):
            await queue.put(update_event)
            
        return {"status": "forked", "new_count": new_count}
    finally:
        session.close()

@app.get("/leaderboard")
async def leaderboard():
    """
    Returns the top 5 logs by fork count.
    """
    session = SessionLocal()
    try:
        top_logs = get_leaderboard(session)
        return [log.to_dict() for log in top_logs]
    finally:
        session.close()

from fastapi.responses import StreamingResponse

async def new_event_generator(request: Request):
    """
    Generator that yields past logs from DB, then awaits new items from a personal queue.
    """
    # 1. Yield past logs from DB
    session = SessionLocal()
    try:
        recent_logs = get_recent_logs(session)
        for log in recent_logs:
             yield json.dumps(log.to_dict()) + "\n"
    finally:
        session.close()

    # 2. Create a new queue for this specific client
    queue = asyncio.Queue()
    connected_clients.add(queue)
    
    try:
        while True:
            # Check if client disconnected (FastAPI/Starlette handles this mostly, but good practice)
            if await request.is_disconnected():
                break
                
            # Wait for the next event from the broadcast (upload_clip)
            data = await queue.get()
            
            # Yield in NDJSON or SSE format. 
            # The client expects a stream of JSON objects.
            yield data + "\n"
            
    except asyncio.CancelledError:
        # Client disconnected
        pass
    finally:
        # Cleanup
        connected_clients.remove(queue)

@app.get("/stream")
async def stream_logs(request: Request):
    return StreamingResponse(new_event_generator(request), media_type="application/x-ndjson")

