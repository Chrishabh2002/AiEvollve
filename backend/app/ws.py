from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.app.events import event_bus
import logging

router = APIRouter()
logger = logging.getLogger("uvicorn")

@router.websocket("/world")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    async def send_event(event: dict):
        try:
            await websocket.send_json(event)
        except Exception as e:
            logger.error(f"Error sending WS event: {e}")

    # Subscribe
    await event_bus.subscribe(send_event)
    
    try:
        while True:
            # Keep connection open, maybe listen for client commands if needed later
            # For now just receive (and ignore) to keep loop alive or handle disconnect
            data = await websocket.receive_text()
            # We could handle client-sent events here if needed
            
    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await event_bus.unsubscribe(send_event)
