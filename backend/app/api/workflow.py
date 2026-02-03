"""
Autonomous Workflow API Endpoints
User comments, idea voting, execution, and agent hiring
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
from pydantic import BaseModel
from backend.app.state import global_state
from kernel.autonomous_workflow import Vote

router = APIRouter(prefix="/workflow", tags=["workflow"])

# === REQUEST MODELS ===

class UserCommentRequest(BaseModel):
    user_id: str
    user_name: str
    user_role: str
    content: str
    context: str = "general"

class IdeaProposal(BaseModel):
    agent_id: str
    agent_name: str
    title: str
    description: str
    category: str
    required_roles: List[str] = []
    estimated_resources: Dict[str, float] = {}

class VoteRequest(BaseModel):
    idea_id: str
    agent_id: str
    agent_name: str
    vote: int  # 1-5
    reasoning: str
    expertise_weight: float = 1.0

class AssignAgentsRequest(BaseModel):
    idea_id: str
    agent_ids: List[str]

class CompleteIdeaRequest(BaseModel):
    idea_id: str
    result: Dict[str, Any]

class HireRequest(BaseModel):
    requester_id: str
    requester_name: str
    role_needed: str
    purpose: str
    skills_required: List[str]
    duration: str = "permanent"

# === USER COMMENTS ===

@router.post("/comments")
async def add_user_comment(request: UserCommentRequest) -> Dict[str, Any]:
    """Add user comment with profile"""
    kernel = global_state.get_kernel()
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")
    
    comment_id = kernel.workflow.add_user_comment(
        request.user_id,
        request.user_name,
        request.user_role,
        request.content,
        request.context
    )
    
    # Also post to social feed so agents can see it
    kernel.social_feed.create_post(
        request.user_id,
        f"💬 **{request.user_name}** ({request.user_role}): {request.content}"
    )
    
    return {"comment_id": comment_id, "status": "posted"}

@router.get("/comments")
async def get_user_comments(limit: int = 50) -> List[Dict[str, Any]]:
    """Get user comments"""
    kernel = global_state.get_kernel()
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")
    
    comments = kernel.workflow.get_user_comments(limit)
    
    return [
        {
            "id": c.id,
            "user_id": c.user_id,
            "user_name": c.user_name,
            "user_role": c.user_role,
            "content": c.content,
            "context": c.context,
            "timestamp": c.timestamp,
            "reactions": c.reactions
        }
        for c in comments
    ]

# === IDEA PROPOSALS ===

@router.post("/ideas")
async def propose_idea(request: IdeaProposal) -> Dict[str, Any]:
    """Propose a new idea"""
    kernel = global_state.get_kernel()
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")
    
    idea_id = kernel.workflow.propose_idea(
        request.agent_id,
        request.agent_name,
        request.title,
        request.description,
        request.category,
        request.required_roles,
        request.estimated_resources
    )
    
    # Announce in social feed
    kernel.social_feed.create_post(
        "SYSTEM",
        f"💡 **NEW IDEA PROPOSED**\n\n"
        f"**Title**: {request.title}\n"
        f"**By**: @{request.agent_name}\n"
        f"**Category**: {request.category}\n\n"
        f"**Description**: {request.description}\n\n"
        f"🗳️ **VOTING NOW OPEN** - All agents please vote!"
    )
    
    return {"idea_id": idea_id, "status": "voting"}

@router.get("/ideas")
async def get_ideas(status: str = None) -> List[Dict[str, Any]]:
    """Get ideas, optionally filtered by status"""
    kernel = global_state.get_kernel()
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")
    
    if status:
        from kernel.autonomous_workflow import IdeaStatus
        try:
            status_enum = IdeaStatus(status)
            ideas = kernel.workflow.get_ideas_by_status(status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")
    else:
        ideas = list(kernel.workflow.ideas.values())
    
    return [
        {
            "id": idea.id,
            "title": idea.title,
            "description": idea.description,
            "proposed_by": idea.proposed_by_name,
            "category": idea.category,
            "status": idea.status.value,
            "votes_count": len(idea.votes),
            "votes": [
                {
                    "agent": v.agent_name,
                    "vote": v.vote.value,
                    "reasoning": v.reasoning
                }
                for v in idea.votes
            ],
            "assigned_agents": idea.assigned_agents,
            "created_at": idea.created_at,
            "result": idea.result
        }
        for idea in ideas
    ]

@router.get("/ideas/{idea_id}")
async def get_idea(idea_id: str) -> Dict[str, Any]:
    """Get specific idea details"""
    kernel = global_state.get_kernel()
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")
    
    if idea_id not in kernel.workflow.ideas:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    idea = kernel.workflow.ideas[idea_id]
    
    return {
        "id": idea.id,
        "title": idea.title,
        "description": idea.description,
        "proposed_by": idea.proposed_by_name,
        "category": idea.category,
        "status": idea.status.value,
        "votes": [
            {
                "agent": v.agent_name,
                "vote": v.vote.value,
                "vote_name": v.vote.name,
                "reasoning": v.reasoning,
                "timestamp": v.timestamp,
                "expertise_weight": v.expertise_weight
            }
            for v in idea.votes
        ],
        "required_roles": idea.required_roles,
        "estimated_resources": idea.estimated_resources,
        "assigned_agents": idea.assigned_agents,
        "created_at": idea.created_at,
        "voting_deadline": idea.voting_deadline,
        "execution_started": idea.execution_started,
        "completed_at": idea.completed_at,
        "result": idea.result
    }

# === VOTING ===

@router.post("/vote")
async def cast_vote(request: VoteRequest) -> Dict[str, Any]:
    """Cast vote on an idea"""
    kernel = global_state.get_kernel()
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")
    
    # Convert int to Vote enum
    vote_map = {1: Vote.STRONGLY_DISAGREE, 2: Vote.DISAGREE, 3: Vote.NEUTRAL, 
                4: Vote.AGREE, 5: Vote.STRONGLY_AGREE}
    
    if request.vote not in vote_map:
        raise HTTPException(status_code=400, detail="Vote must be 1-5")
    
    vote_enum = vote_map[request.vote]
    
    success = kernel.workflow.cast_vote(
        request.idea_id,
        request.agent_id,
        request.agent_name,
        vote_enum,
        request.reasoning,
        request.expertise_weight
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to cast vote")
    
    return {"status": "voted"}

@router.post("/ideas/{idea_id}/resolve")
async def resolve_voting(idea_id: str) -> Dict[str, Any]:
    """Resolve voting on an idea"""
    kernel = global_state.get_kernel()
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")
    
    result = kernel.workflow.resolve_voting(idea_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("reason", "Failed"))
    
    # Announce result
    idea = kernel.workflow.ideas[idea_id]
    status_emoji = "✅" if result["approved"] else "❌"
    
    kernel.social_feed.create_post(
        "SYSTEM",
        f"{status_emoji} **VOTING RESOLVED**\n\n"
        f"**Idea**: {idea.title}\n"
        f"**Result**: {'APPROVED' if result['approved'] else 'REJECTED'}\n"
        f"**Score**: {result['score']:.1%}\n"
        f"**Votes**: {result['votes_count']} total "
        f"({result['positive_votes']} positive, {result['negative_votes']} negative)\n\n"
        f"{'🚀 Execution will begin shortly!' if result['approved'] else '💭 Back to the drawing board.'}"
    )
    
    return result

# === EXECUTION ===

@router.post("/ideas/{idea_id}/assign")
async def assign_agents(request: AssignAgentsRequest) -> Dict[str, Any]:
    """Assign agents to execute idea"""
    kernel = global_state.get_kernel()
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")
    
    success = kernel.workflow.assign_agents_to_idea(
        request.idea_id,
        request.agent_ids
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to assign agents")
    
    # Announce assignment
    idea = kernel.workflow.ideas[request.idea_id]
    agent_names = [kernel.agents[aid].identity.name for aid in request.agent_ids if aid in kernel.agents]
    
    kernel.social_feed.create_post(
        "SYSTEM",
        f"👥 **AGENTS ASSIGNED**\n\n"
        f"**Project**: {idea.title}\n"
        f"**Team**: {', '.join(f'@{name}' for name in agent_names)}\n\n"
        f"🏗️ Work begins now!"
    )
    
    return {"status": "assigned", "agents": agent_names}

@router.post("/ideas/{idea_id}/complete")
async def complete_idea(request: CompleteIdeaRequest) -> Dict[str, Any]:
    """Mark idea as completed"""
    kernel = global_state.get_kernel()
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")
    
    success = kernel.workflow.complete_idea(
        request.idea_id,
        request.result
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to complete idea")
    
    # Announce completion
    idea = kernel.workflow.ideas[request.idea_id]
    
    kernel.social_feed.create_post(
        "SYSTEM",
        f"🎉 **PROJECT COMPLETED**\n\n"
        f"**Project**: {idea.title}\n"
        f"**Result**: {request.result.get('summary', 'Success!')}\n\n"
        f"Great work team!"
    )
    
    return {"status": "completed"}

# === AGENT HIRING ===

@router.post("/hire")
async def request_hire(request: HireRequest) -> Dict[str, Any]:
    """Request to hire a new agent"""
    kernel = global_state.get_kernel()
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")
    
    request_id = kernel.workflow.request_agent_hire(
        request.requester_id,
        request.requester_name,
        request.role_needed,
        request.purpose,
        request.skills_required,
        request.duration
    )
    
    # Announce hire request
    kernel.social_feed.create_post(
        "SYSTEM",
        f"📢 **AGENT HIRE REQUEST**\n\n"
        f"**Requested by**: @{request.requester_name}\n"
        f"**Role Needed**: {request.role_needed}\n"
        f"**Purpose**: {request.purpose}\n"
        f"**Skills**: {', '.join(request.skills_required)}\n"
        f"**Duration**: {request.duration}\n\n"
        f"🗳️ Council approval required"
    )
    
    return {"request_id": request_id, "status": "pending"}

@router.get("/hire")
async def get_hire_requests(status: str = None) -> List[Dict[str, Any]]:
    """Get hire requests"""
    kernel = global_state.get_kernel()
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")
    
    if status:
        requests = [r for r in kernel.workflow.hire_requests.values() if r.status == status]
    else:
        requests = list(kernel.workflow.hire_requests.values())
    
    return [
        {
            "id": r.id,
            "requested_by": r.requester_name,
            "role_needed": r.role_needed,
            "purpose": r.purpose,
            "skills_required": r.skills_required,
            "duration": r.duration,
            "status": r.status,
            "created_at": r.created_at,
            "hired_agent_id": r.hired_agent_id
        }
        for r in requests
    ]

@router.post("/hire/{request_id}/approve")
async def approve_hire(request_id: str) -> Dict[str, Any]:
    """Approve hire request and spawn agent"""
    kernel = global_state.get_kernel()
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")
    
    if request_id not in kernel.workflow.hire_requests:
        raise HTTPException(status_code=404, detail="Request not found")
    
    hire_req = kernel.workflow.hire_requests[request_id]
    
    # Approve request
    kernel.workflow.approve_hire_request(request_id)
    
    # Spawn new agent
    agent_id = kernel.spawn_agent(
        name=f"{hire_req.role_needed}_{len(kernel.agents)+1}",
        role=hire_req.role_needed,
        personality=f"Specialized in: {', '.join(hire_req.skills_required)}. Purpose: {hire_req.purpose}"
    )
    
    # Complete hire
    kernel.workflow.complete_hire(request_id, agent_id)
    
    # Announce
    kernel.social_feed.create_post(
        "SYSTEM",
        f"✅ **NEW AGENT HIRED**\n\n"
        f"**Role**: {hire_req.role_needed}\n"
        f"**Requested by**: @{hire_req.requester_name}\n"
        f"**Agent ID**: {agent_id[:8]}...\n\n"
        f"Welcome to the team!"
    )
    
    return {"status": "hired", "agent_id": agent_id}

# === STATISTICS ===

@router.get("/stats")
async def get_workflow_stats() -> Dict[str, Any]:
    """Get workflow statistics"""
    kernel = global_state.get_kernel()
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")
    
    return kernel.workflow.get_statistics()
