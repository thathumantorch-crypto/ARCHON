"""FastAPI server exposing ARCHON AI capabilities."""

import os
import sys
import asyncio
import logging
from typing import Optional, Dict, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import aiofiles

# Ensure src is on the path when this module is executed directly
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.archon_ai import ArchonAI  # noqa: E402

logger = logging.getLogger("ARCHON.API")
logger.setLevel(logging.INFO)


class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None


class KnowledgeRequest(BaseModel):
    content: str
    category: Optional[str] = "general"
    source: Optional[str] = "api"


class SelfHealRequest(BaseModel):
    description: Optional[str] = ""


app = FastAPI(
    title="ARCHON AI API",
    description="REST/WebSocket interface for the ARCHON autonomous assistant",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

archon_instance: Optional[ArchonAI] = None


def main(host: str = "0.0.0.0", port: int = 8000, reload: bool = False, log_level: str = "info") -> None:
    """Convenience runner so other modules can start uvicorn without redefining settings."""
    import uvicorn

    uvicorn.run(
        "src.ui.api_server:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
    )


@app.on_event("startup")
async def startup_event() -> None:
    global archon_instance
    if archon_instance is None:
        logger.info("Initializing ARCHON AI for API server…")
        archon_instance = ArchonAI()
        logger.info("ARCHON AI ready.")


@app.get("/health")
def health_check() -> Dict[str, Any]:
    if archon_instance is None:
        return {"status": "initializing"}
    status = archon_instance.archon_core.get_status()
    return {"status": "ok", "archon": status}


@app.post("/chat")
def chat_endpoint(request: ChatRequest) -> Dict[str, Any]:
    if archon_instance is None:
        raise RuntimeError("ARCHON AI not initialized yet")
    response = archon_instance.process_message(request.message, request.context or {})
    return {
        "response": response.get("archon_response"),
        "intent": response.get("intent"),
        "confidence": response.get("confidence"),
        "metadata": {
            "actions": response.get("actions_taken", []),
            "reflection": response.get("archon_reflection"),
            "knowledgebase_hits": response.get("knowledgebase_results", []),
        },
    }


@app.post("/self-heal")
def self_heal(request: SelfHealRequest) -> Dict[str, Any]:
    if archon_instance is None:
        raise RuntimeError("ARCHON AI not initialized yet")
    result = archon_instance.request_self_healing(issue_description=request.description or "API request")
    return result


@app.post("/knowledge/text")
def add_knowledge(item: KnowledgeRequest) -> Dict[str, Any]:
    if archon_instance is None or not archon_instance.knowledgebase:
        return {"success": False, "message": "Knowledgebase not available"}
    embedding = [0.0] * 768  # simple placeholder; real embeddings handled elsewhere
    success = archon_instance.knowledgebase.add_knowledge(
        content=item.content,
        embedding=embedding,
        source=item.source or "api",
        category=item.category or "general",
    )
    return {"success": success}


@app.post("/knowledge/file")
async def upload_knowledge_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)) -> Dict[str, Any]:
    if archon_instance is None:
        return {"success": False, "message": "ARCHON not ready"}
    save_path = os.path.join("temp", file.filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    async with aiofiles.open(save_path, "wb") as out_file:
        while content := await file.read(1024 * 1024):
            await out_file.write(content)

    background_tasks.add_task(os.remove, save_path)
    return {"success": True, "message": f"Uploaded {file.filename}"}


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket) -> None:
    await websocket.accept()
    if archon_instance is None:
        await websocket.close(code=1012)
        return

    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message")
            context = data.get("context") or {}
            if not message:
                await websocket.send_json({"error": "message is required"})
                continue
            response = archon_instance.process_message(message, context)
            await websocket.send_json({
                "response": response.get("archon_response"),
                "intent": response.get("intent"),
                "confidence": response.get("confidence"),
            })
            await asyncio.sleep(0)  # yield
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as exc:
        logger.error("WebSocket error: %s", exc)
        await websocket.close(code=1011)
