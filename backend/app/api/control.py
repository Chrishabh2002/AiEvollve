from fastapi import APIRouter, HTTPException
from backend.app.state import global_state
from pydantic import BaseModel
import asyncio
from backend.app.tick import run_simulation_loop

router = APIRouter()

class TickRateRequest(BaseModel):
    tick_rate: float

class MaxAgentsRequest(BaseModel):
    max_agents: int
    
class SystemEventRequest(BaseModel):
    message: str

class BooleanRequest(BaseModel):
    value: bool

@router.post("/pause")
async def pause_world():
    if not global_state.is_running:
        return {"status": "Already paused"}
    
    global_state.is_running = False
    
    # Save state on pause
    try:
        kernel = global_state.get_kernel()
        kernel.save_state()
    except Exception:
        pass
        
    return {"status": "Paused", "server_status": "PAUSED"}

@router.post("/resume")
async def resume_world():
    if global_state.is_running:
        return {"status": "Already running"}
    
    global_state.is_running = True
    
    # Triggering backgorund loop if not exists
    if not global_state.simulation_task:
        loop = asyncio.get_event_loop()
        global_state.simulation_task = loop.create_task(run_simulation_loop())

    return {"status": "Resumed", "server_status": "RUNNING"}

@router.post("/event")
async def inject_event(req: SystemEventRequest):
    """
    Injects a 'SYSTEM' event into the social feed to trigger agent reaction.
    """
    try:
        kernel = global_state.get_kernel()
        # Create a post from 'SYSTEM'
        kernel.social_feed.create_post("SYSTEM", req.message)
        return {"status": "Event Injected", "message": req.message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/set-tick")
async def set_tick_rate(req: TickRateRequest):
    global_state.tick_rate = req.tick_rate
    return {"status": "Updated", "tick_rate": global_state.tick_rate}

@router.post("/set-max-agents")
async def set_max_agents(req: MaxAgentsRequest):
    if req.max_agents < 2 or req.max_agents > 100:
         raise HTTPException(status_code=400, detail="Invalid max agents limit")
    
    try:
        kernel = global_state.get_kernel()
        kernel.max_agents_limit = req.max_agents
        return {"status": "Updated", "max_agents": kernel.max_agents_limit}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/set-auto-evolution")
async def set_auto_evolution(req: BooleanRequest):
    try:
        kernel = global_state.get_kernel()
        kernel.auto_evolution = req.value
        return {"status": "Updated", "auto_evolution": kernel.auto_evolution}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/set-strict-mode")
async def set_strict_mode(req: BooleanRequest):
    try:
        kernel = global_state.get_kernel()
        kernel.strict_mode = req.value
        return {"status": "Updated", "strict_mode": kernel.strict_mode}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/set-sandboxed")
async def set_sandboxed(req: BooleanRequest):
    try:
        kernel = global_state.get_kernel()
        kernel.sandboxed = req.value
        return {"status": "Updated", "sandboxed": kernel.sandboxed}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/settings")
async def get_settings():
    try:
        kernel = global_state.get_kernel()
        return {
            "tick_rate": global_state.tick_rate,
            "max_agents": kernel.max_agents_limit,
            "auto_evolution": kernel.auto_evolution,
            "strict_mode": kernel.strict_mode,
            "sandboxed": kernel.sandboxed,
            "is_running": global_state.is_running
        }
    except Exception as e:
        # Fallback if kernel not ready (though unlikely given middleware)
        return {
             "tick_rate": global_state.tick_rate,
             "is_running": global_state.is_running,
             "error": str(e)
        }
