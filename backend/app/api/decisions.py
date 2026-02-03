from fastapi import APIRouter, HTTPException
from backend.app.state import global_state
from typing import List, Optional, Any
from pydantic import BaseModel

router = APIRouter()

class VoteSummary(BaseModel):
    yes: int
    no: int
    veto: int

class VoteDetail(BaseModel):
    agent: str
    decision: str
    weight: float

class DecisionModel(BaseModel):
    id: str
    topic: str
    proposal_content: Optional[str] = None
    status: str
    result: Optional[str] = None
    confidence: Optional[float] = 0.0
    author_id: str
    created_at: str
    votes_summary: VoteSummary
    votes: Optional[List[VoteDetail]] = []

@router.get("", response_model=List[DecisionModel])
async def get_decisions():
    try:
        kernel = global_state.get_kernel()
        decisions_data = kernel.introspection.get_decisions()
        
        mapped = []
        for d in decisions_data:
            # Need to re-fetch full object to get votes if introspection is light
            # For now, introspection returns basic dict. We might need to expand introspection.py 
            # Or access kernel directly since we are on the same process in this monorepo architecture.
            # Introspection.get_decisions returns basic info.
            
            # Re-accessing raw object for details (safe read)
            raw_decision = kernel.decision_engine.get_decision(d["decision_id"])
            if not raw_decision:
                continue
                
            yes = sum(1 for v in raw_decision.votes if v.choice.name == "YES")
            no = sum(1 for v in raw_decision.votes if v.choice.name == "NO")
            veto = sum(1 for v in raw_decision.votes if v.choice.name == "VETO")
            
            mapped.append({
                "id": raw_decision.id,
                "topic": raw_decision.topic_id,
                "proposal_content": raw_decision.proposal.content,
                "status": raw_decision.status.name,
                "result": raw_decision.result.result.name if raw_decision.result else None,
                "confidence": 0.8, # Placeholder logic
                "author_id": raw_decision.proposal.author_id,
                "created_at": raw_decision.created_at.isoformat() if hasattr(raw_decision.created_at, 'isoformat') else str(raw_decision.created_at),
                "votes_summary": {"yes": yes, "no": no, "veto": veto},
                "votes": [] # List for summary view is optional, keeping it light
            })
            
        return mapped
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id}", response_model=DecisionModel)
async def get_decision_detail(id: str):
    try:
        kernel = global_state.get_kernel()
        raw_decision = kernel.decision_engine.get_decision(id)
        if not raw_decision:
            raise HTTPException(status_code=404, detail="Decision not found")
            
        yes = sum(1 for v in raw_decision.votes if v.choice.name == "YES")
        no = sum(1 for v in raw_decision.votes if v.choice.name == "NO")
        veto = sum(1 for v in raw_decision.votes if v.choice.name == "VETO")
        
        # EXTRACT VOTES WITH DETAILED REASONING
        votes_list = []
        for v in raw_decision.votes:
             agent_name = v.agent_id
             if v.agent_id in kernel.agents:
                 agent_name = kernel.agents[v.agent_id].identity.name
             
             votes_list.append({
                 "agent": agent_name,
                 "decision": v.choice.name,
                 "weight": v.weight,
                 "reasoning": v.rationale if hasattr(v, 'rationale') else None,
                 "suggestions": v.suggestions if hasattr(v, 'suggestions') else []
             })

        
        return {
            "id": raw_decision.id,
            "topic": raw_decision.topic_id,
            "proposal_content": raw_decision.proposal.content,
            "status": raw_decision.status.name,
            "result": raw_decision.result.result.name if raw_decision.result else None,
            "confidence": 0.8,
            "author_id": raw_decision.proposal.author_id,
            "created_at": raw_decision.created_at.isoformat() if hasattr(raw_decision.created_at, 'isoformat') else str(raw_decision.created_at),
            "votes_summary": {"yes": yes, "no": no, "veto": veto},
            "votes": votes_list
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
