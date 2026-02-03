from fastapi import APIRouter, HTTPException
from backend.app.state import global_state
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()

class PlanStepModel(BaseModel):
    id: str
    description: str
    status: str

class PlanModel(BaseModel):
    id: str
    goal: str
    status: str
    steps: List[PlanStepModel]

@router.get("", response_model=List[PlanModel])
async def get_plans():
    try:
        kernel = global_state.get_kernel()
        plans_data = kernel.introspection.get_plans()
        
        mapped = []
        for p in plans_data:
            steps = []
            for s in p["steps"]:
                steps.append({
                    "id": s["step_id"],
                    "description": s["description"],
                    "status": s["status"]
                })
            
            mapped.append({
                "id": p["plan_id"],
                "goal": p["goal"],
                "status": p["status"],
                "steps": steps
            })
        return mapped
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id}", response_model=PlanModel)
async def get_plan_detail(id: str):
    try:
        kernel = global_state.get_kernel()
        # Direct access to search for plan since introspection returns simplified list
        # Using introspection data for consistency
        plans_data = kernel.introspection.get_plans()
        target = next((p for p in plans_data if p["plan_id"] == id), None)
        
        if not target:
             raise HTTPException(status_code=404, detail="Plan not found")
             
        steps = []
        for s in target["steps"]:
            steps.append({
                "id": s["step_id"],
                "description": s["description"],
                "status": s["status"]
            })
        
        return {
            "id": target["plan_id"],
            "goal": target["goal"],
            "status": target["status"],
            "steps": steps
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/execution")
async def get_execution_stats():
    """
    Get real-time execution statistics
    """
    try:
        kernel = global_state.get_kernel()
        
        if not kernel.real_executor:
            return {
                "total_executions": 0,
                "successes": 0,
                "failures": 0,
                "success_rate": 0.0,
                "active_plans": 0,
                "completed_plans": 0,
                "failed_plans": 0,
                "recent_executions": []
            }
        
        stats = kernel.real_executor.get_execution_stats()
        
        # Add recent execution log (last 10)
        recent = kernel.real_executor.execution_log[-10:] if kernel.real_executor.execution_log else []
        stats["recent_executions"] = recent
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

