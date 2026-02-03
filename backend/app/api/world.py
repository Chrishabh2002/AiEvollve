"""
Virtual World API Endpoints
Provides access to world state, locations, infrastructure, and economy
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
from backend.app.state import global_state

router = APIRouter(prefix="/world", tags=["world"])

@router.get("/state")
async def get_world_state() -> Dict[str, Any]:
    """Get complete world state"""
    kernel = global_state.get_kernel()
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")
    
    return kernel.world_engine.to_dict()

@router.get("/stats")
async def get_world_stats() -> Dict[str, Any]:
    """Get world statistics"""
    kernel = global_state.get_kernel()
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")
    
    return kernel.world_engine.world_state.get_world_stats()

@router.get("/locations")
async def get_locations() -> List[Dict[str, Any]]:
    """Get all locations in the world"""
    kernel = global_state.get_kernel()
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")
    
    locations = []
    for loc_id, loc in kernel.world_engine.world_state.locations.items():
        locations.append({
            "id": loc.id,
            "name": loc.name,
            "type": loc.type.value,
            "description": loc.description,
            "capacity": loc.capacity,
            "occupants": len(loc.current_occupants),
            "occupant_names": [
                kernel.agents[aid].identity.name 
                for aid in loc.current_occupants 
                if aid in kernel.agents
            ],
            "infrastructure_count": len(loc.infrastructure)
        })
    
    return locations

@router.get("/locations/{location_id}")
async def get_location(location_id: str) -> Dict[str, Any]:
    """Get detailed info about a specific location"""
    kernel = global_state.get_kernel()
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")
    
    info = kernel.world_engine.world_state.get_location_info(location_id)
    if not info:
        raise HTTPException(status_code=404, detail="Location not found")
    
    return info

@router.get("/infrastructure")
async def get_infrastructure() -> List[Dict[str, Any]]:
    """Get all infrastructure in the world"""
    kernel = global_state.get_kernel()
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")
    
    infrastructure = []
    for infra_id, infra in kernel.world_engine.world_state.infrastructure.items():
        creator_name = "Unknown"
        if infra.creator_id in kernel.agents:
            creator_name = kernel.agents[infra.creator_id].identity.name
        
        infrastructure.append({
            "id": infra.id,
            "name": infra.name,
            "type": infra.type,
            "description": infra.description,
            "creator": creator_name,
            "location_id": infra.location_id,
            "status": infra.status,
            "usage_count": infra.usage_count,
            "created_at": infra.created_at
        })
    
    return infrastructure

@router.get("/achievements")
async def get_achievements() -> List[Dict[str, Any]]:
    """Get all civilization achievements"""
    kernel = global_state.get_kernel()
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")
    
    achievements = []
    for achievement in kernel.world_engine.world_state.achievements:
        achiever_names = [
            kernel.agents[aid].identity.name 
            for aid in achievement.achieved_by 
            if aid in kernel.agents
        ]
        
        achievements.append({
            "id": achievement.id,
            "name": achievement.name,
            "description": achievement.description,
            "category": achievement.category,
            "impact": achievement.impact,
            "achieved_by": achiever_names,
            "achieved_at": achievement.achieved_at
        })
    
    return achievements

@router.get("/economy")
async def get_economy_state() -> Dict[str, Any]:
    """Get economy state"""
    kernel = global_state.get_kernel()
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")
    
    return kernel.world_engine.world_state.economy.to_dict()

@router.get("/resources/{agent_id}")
async def get_agent_resources(agent_id: str) -> Dict[str, Any]:
    """Get resource balances for an agent"""
    kernel = global_state.get_kernel()
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")
    
    if agent_id not in kernel.agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    balances = kernel.world_engine.world_state.economy.resource_pool.get_all_balances(agent_id)
    
    return {
        "agent_id": agent_id,
        "agent_name": kernel.agents[agent_id].identity.name,
        "resources": {rt.value: amount for rt, amount in balances.items()}
    }

@router.get("/expertise/{agent_id}")
async def get_agent_expertise(agent_id: str) -> Dict[str, Any]:
    """Get expertise profile for an agent"""
    kernel = global_state.get_kernel()
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")
    
    if agent_id not in kernel.agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    expertise = kernel.expertise_manager.get_expertise(agent_id)
    if not expertise:
        return {"error": "Expertise not initialized"}
    
    return {
        "agent_id": agent_id,
        "agent_name": kernel.agents[agent_id].identity.name,
        "domain": expertise.domain,
        "level": expertise.level,
        "skills": {
            name: {"level": skill.level, "experience": skill.experience}
            for name, skill in expertise.skills.items()
        },
        "proven_successes": expertise.proven_successes,
        "teaching_ability": expertise.teaching_ability
    }

@router.get("/artifacts")
async def get_artifacts() -> Dict[str, Any]:
    """Get all created artifacts"""
    kernel = global_state.get_kernel()
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")
    
    stats = kernel.advanced_tools.get_stats()
    
    return {
        "statistics": stats,
        "recent_artifacts": list(kernel.advanced_tools.created_artifacts.values())[-10:],
        "recent_experiments": kernel.advanced_tools.experiments_run[-10:],
        "active_systems": [
            s for s in kernel.advanced_tools.systems_built.values()
            if s.get("status") == "active"
        ]
    }

@router.post("/build_infrastructure")
async def build_infrastructure(
    name: str,
    infra_type: str,
    description: str,
    creator_id: str,
    location_id: str
) -> Dict[str, Any]:
    """Build new infrastructure"""
    kernel = global_state.get_kernel()
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")
    
    infra_id = kernel.world_engine.world_state.build_infrastructure(
        name, infra_type, description, creator_id, location_id
    )
    
    if not infra_id:
        raise HTTPException(status_code=400, detail="Failed to build infrastructure")
    
    return {"infrastructure_id": infra_id, "status": "created"}

@router.post("/record_achievement")
async def record_achievement(
    name: str,
    description: str,
    achieved_by: List[str],
    category: str,
    impact: str
) -> Dict[str, Any]:
    """Record a civilization achievement"""
    kernel = global_state.get_kernel()
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")
    
    achievement_id = kernel.world_engine.world_state.record_achievement(
        name, description, achieved_by, category, impact
    )
    
    return {"achievement_id": achievement_id, "status": "recorded"}
