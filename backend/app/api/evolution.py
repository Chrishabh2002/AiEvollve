from fastapi import APIRouter, HTTPException
from backend.app.state import global_state
from typing import List
from pydantic import BaseModel

router = APIRouter()

class EvolutionEventModel(BaseModel):
    id: str
    timestamp: str
    trigger: str
    spawned_agent_role: str
    reason: str
    generation: int

@router.get("", response_model=List[EvolutionEventModel])
async def get_evolution_events():
    try:
        kernel = global_state.get_kernel()
        # Ensure we access the history we added
        history = getattr(kernel.evolution_engine, "history", [])
        
        # Map to model
        events = []
        for h in history:
            events.append({
                "id": h.get("id", "unknown"),
                "timestamp": h.get("timestamp", ""),
                "trigger": h.get("trigger", "SYSTEM"),
                "spawned_agent_role": h.get("role", "Unknown"),
                "reason": h.get("reason", ""),
                "generation": h.get("generation", 0)
            })
        
        # Reverse to show newest first
        return events[::-1]
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e)) 
