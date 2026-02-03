from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.app.lifespan import lifespan
from backend.app.state import global_state
from typing import List, Optional
from pydantic import BaseModel

# Import new routers
from backend.app.api import decisions, plans, evolution, control, world, workflow, social
from backend.app import ws

app = FastAPI(
    title="AiEvollve Backend",
    description="API Bridge for Self-Evolving Multi-Agent Ecosystem",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
# Allow all origins for the simulation prototype to prevent deployment headers issues
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Register Routers ---
app.include_router(decisions.router, prefix="/api/world/decisions", tags=["Decisions"])
app.include_router(plans.router, prefix="/api/world/plans", tags=["Plans"])
app.include_router(evolution.router, prefix="/api/world/evolution", tags=["Evolution"])
app.include_router(control.router, prefix="/api/world/control", tags=["Control"])
app.include_router(world.router, prefix="/api", tags=["Virtual World"])  # NEW: World endpoints
app.include_router(workflow.router, prefix="/api", tags=["Autonomous Workflow"])  # NEW: Workflow
app.include_router(social.router, prefix="/api", tags=["Social Feed - Twitter/X Style"])  # NEW
app.include_router(ws.router, prefix="/ws", tags=["WebSockets"])


# --- Existing High-Level Endpoints (Keep for backward compatibility/Health) ---

from typing import List, Optional, Any, Dict
from pydantic import BaseModel

class AgentModel(BaseModel):
    id: str
    name: str
    role: str
    state: str
    reputation: float
    current_plan: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None

class PostModel(BaseModel):
    id: str
    agent_id: str
    agent_name: Optional[str] = "Unknown"
    content: str
    timestamp: str
    parent_id: Optional[str] = None
    likes: List[str] = []

@app.get("/api/world/feed", response_model=List[PostModel])
async def get_feed(limit: int = 50):
    try:
        kernel = global_state.get_kernel()
        feed_data = kernel.introspection.get_social_feed(limit=limit)
        
        # We need direct access to posts to get 'likes' since introspection might not return it yet
        # Using kernel.social_feed directly to be safe, ideally we should update introspection
        # For now, let's just map directly from kernel if possible, or assume introspection was updated.
        # But wait, introspection.get_social_feed returns a list of Dicts.
        # Check introspection.py first? No, let's just trust we can grab standard posts.
        # Actually, introspection usually converts to dict.
        # Let's perform a direct read from social_feed if possible or map agent names here.
        
        # Accessing agents to map names
        agents_map = {a_id: agent for a_id, agent in kernel.agents.items()}
        
        mapped_feed = []
        for p in feed_data:
            # p is a dict from Introspection
            # If Introspection doesn't include 'likes', we might need to modify Introspection or read raw posts.
            # Let's read raw posts for accuracy given we just updated the Kernel class.
            
            raw_post = kernel.social_feed._posts.get(p["post_id"])
            likes = raw_post.likes if raw_post else []
            
            a_id = p["agent_id"]
            a_name = agents_map[a_id].identity.name if a_id in agents_map else "Unknown"
            if a_id == "SYSTEM": a_name = "SYSTEM"

            mapped_feed.append({
                "id": p["post_id"],
                "agent_id": a_id,
                "agent_name": a_name,
                "content": p["content"],
                "timestamp": p["timestamp"],
                "parent_id": p["parent_id"],
                "likes": likes
            })
        return mapped_feed
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/world/feed/{post_id}/like")
async def like_post(post_id: str, agent_id: str = "user"):
    try:
        kernel = global_state.get_kernel()
        success = kernel.social_feed.like_post(post_id, agent_id)
        if success:
            return {"status": "success", "message": "Post liked"}
        else:
            return {"status": "already_liked", "message": "Already liked or post not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SystemHealth(BaseModel):
    tick: int
    agent_count: int
    decision_count: int
    plan_count: int
    evolution_events: int
    status: str
    tick_rate: float
    max_agents: int
    auto_evolution: bool
    strict_mode: bool
    sandboxed: bool

class CreatePostModel(BaseModel):
    agent_id: str
    content: str
    parent_id: Optional[str] = None

@app.post("/api/world/feed")
async def create_post(post: CreatePostModel):
    try:
        kernel = global_state.get_kernel()
        # "user" or provided agent_id (if we allow imposters, but let's stick to user/admin for now)
        # Actually the frontend sends agent_id='user' probably.
        
        # If agent_id is not in agents, we treat it as external user or system.
        # SocialFeed handles string IDs.
        
        # Inject into feed
        post_id = kernel.social_feed.create_post(post.agent_id, post.content, post.parent_id)
        
        return {"status": "success", "post_id": post_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/world/health", response_model=SystemHealth)
async def get_world_health():
    try:
        kernel = global_state.get_kernel()
        status_data = kernel.introspection.get_system_status()
        return {
            "tick": status_data.get("tick", 0),
            "agent_count": status_data.get("agent_count", 0),
            "decision_count": status_data.get("decision_count", 0),
            "plan_count": status_data.get("active_plans", 0),
            "evolution_events": 0,
            "status": "RUNNING" if global_state.is_running else "PAUSED",
            "tick_rate": global_state.tick_rate,
            "max_agents": kernel.max_agents_limit,
            "auto_evolution": kernel.auto_evolution,
            "strict_mode": kernel.strict_mode,
            "sandboxed": kernel.sandboxed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/world/agents", response_model=List[AgentModel])
async def get_agents():
    try:
        kernel = global_state.get_kernel()
        agents_data = kernel.introspection.get_agents()
        mapped_agents = []
        for a in agents_data:
            mapped_agents.append({
                "id": a["agent_id"],
                "name": a["name"],
                "role": a["role"],
                "state": a["state"],
                "reputation": a["reputation"],
                "current_plan": a["current_plan"],
                "metrics": a.get("metrics", {})
            })
        return mapped_agents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
