"""
Autonomous Workflow System
Complete end-to-end autonomous agent workflow with voting, execution, and hiring
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import time
import uuid

class IdeaStatus(Enum):
    PROPOSED = "proposed"
    VOTING = "voting"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class Vote(Enum):
    STRONGLY_AGREE = 5
    AGREE = 4
    NEUTRAL = 3
    DISAGREE = 2
    STRONGLY_DISAGREE = 1

@dataclass
class AgentVote:
    """A vote from an agent on an idea"""
    agent_id: str
    agent_name: str
    vote: Vote
    reasoning: str
    timestamp: float
    expertise_weight: float = 1.0  # Based on domain expertise

@dataclass
class Idea:
    """An idea proposed by an agent"""
    id: str
    title: str
    description: str
    proposed_by: str
    proposed_by_name: str
    category: str  # "tool", "infrastructure", "experiment", "governance", "other"
    status: IdeaStatus
    votes: List[AgentVote] = field(default_factory=list)
    required_roles: List[str] = field(default_factory=list)
    estimated_resources: Dict[str, float] = field(default_factory=dict)
    assigned_agents: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    voting_deadline: Optional[float] = None
    execution_started: Optional[float] = None
    completed_at: Optional[float] = None
    result: Optional[Dict[str, Any]] = None

@dataclass
class UserComment:
    """User comment with profile"""
    id: str
    user_id: str
    user_name: str
    user_role: str  # "admin", "observer", "contributor"
    content: str
    context: str  # What they're commenting on
    timestamp: float
    reactions: Dict[str, int] = field(default_factory=dict)  # agent_id -> reaction

@dataclass
class AgentHireRequest:
    """Request to hire a new specialized agent"""
    id: str
    requested_by: str
    requester_name: str
    role_needed: str
    purpose: str
    skills_required: List[str]
    duration: str  # "temporary", "permanent"
    status: str  # "pending", "approved", "hired", "rejected"
    created_at: float
    hired_agent_id: Optional[str] = None

class AutonomousWorkflow:
    """Manages complete autonomous workflow"""
    
    def __init__(self):
        self.ideas: Dict[str, Idea] = {}
        self.user_comments: List[UserComment] = []
        self.hire_requests: Dict[str, AgentHireRequest] = {}
        self.voting_threshold = 0.6  # 60% positive votes needed
        
    # === USER INTERACTION ===
    
    def add_user_comment(self, user_id: str, user_name: str, user_role: str, 
                        content: str, context: str = "general") -> str:
        """Add user comment with full profile"""
        comment = UserComment(
            id=str(uuid.uuid4()),
            user_id=user_id,
            user_name=user_name,
            user_role=user_role,
            content=content,
            context=context,
            timestamp=time.time()
        )
        
        self.user_comments.append(comment)
        return comment.id
        
    def get_user_comments(self, limit: int = 50) -> List[UserComment]:
        """Get recent user comments"""
        return sorted(self.user_comments, key=lambda x: x.timestamp, reverse=True)[:limit]
        
    def agent_react_to_comment(self, comment_id: str, agent_id: str, reaction: str):
        """Agent reacts to user comment"""
        for comment in self.user_comments:
            if comment.id == comment_id:
                comment.reactions[agent_id] = reaction
                break
                
    # === IDEA PROPOSAL ===
    
    def propose_idea(self, agent_id: str, agent_name: str, title: str, 
                    description: str, category: str, 
                    required_roles: List[str] = None,
                    estimated_resources: Dict[str, float] = None) -> str:
        """Agent proposes a new idea"""
        
        idea_id = str(uuid.uuid4())
        
        idea = Idea(
            id=idea_id,
            title=title,
            description=description,
            proposed_by=agent_id,
            proposed_by_name=agent_name,
            category=category,
            status=IdeaStatus.PROPOSED,
            required_roles=required_roles or [],
            estimated_resources=estimated_resources or {},
            voting_deadline=time.time() + 300  # 5 minutes voting period
        )
        
        self.ideas[idea_id] = idea
        
        # Automatically move to voting
        idea.status = IdeaStatus.VOTING
        
        return idea_id
        
    # === VOTING ===
    
    def cast_vote(self, idea_id: str, agent_id: str, agent_name: str, 
                 vote: Vote, reasoning: str, expertise_weight: float = 1.0) -> bool:
        """Agent votes on an idea"""
        
        if idea_id not in self.ideas:
            return False
            
        idea = self.ideas[idea_id]
        
        if idea.status != IdeaStatus.VOTING:
            return False
            
        # Check if already voted
        for existing_vote in idea.votes:
            if existing_vote.agent_id == agent_id:
                return False  # Already voted
                
        vote_obj = AgentVote(
            agent_id=agent_id,
            agent_name=agent_name,
            vote=vote,
            reasoning=reasoning,
            timestamp=time.time(),
            expertise_weight=expertise_weight
        )
        
        idea.votes.append(vote_obj)
        
        return True
        
    def resolve_voting(self, idea_id: str) -> Dict[str, Any]:
        """Resolve voting and determine if idea is approved"""
        
        if idea_id not in self.ideas:
            return {"success": False, "reason": "Idea not found"}
            
        idea = self.ideas[idea_id]
        
        if idea.status != IdeaStatus.VOTING:
            return {"success": False, "reason": "Not in voting status"}
            
        if not idea.votes:
            idea.status = IdeaStatus.REJECTED
            return {
                "success": True,
                "approved": False,
                "reason": "No votes received"
            }
            
        # Calculate weighted score
        total_weight = sum(v.expertise_weight for v in idea.votes)
        weighted_score = sum(v.vote.value * v.expertise_weight for v in idea.votes)
        
        # Normalize to 0-1 scale (votes are 1-5)
        normalized_score = (weighted_score / total_weight - 1) / 4
        
        # Check if approved
        approved = normalized_score >= self.voting_threshold
        
        if approved:
            idea.status = IdeaStatus.APPROVED
        else:
            idea.status = IdeaStatus.REJECTED
            
        return {
            "success": True,
            "approved": approved,
            "score": normalized_score,
            "votes_count": len(idea.votes),
            "positive_votes": sum(1 for v in idea.votes if v.vote.value >= 4),
            "negative_votes": sum(1 for v in idea.votes if v.vote.value <= 2)
        }
        
    # === EXECUTION ===
    
    def assign_agents_to_idea(self, idea_id: str, agent_ids: List[str]) -> bool:
        """Assign agents to execute an approved idea"""
        
        if idea_id not in self.ideas:
            return False
            
        idea = self.ideas[idea_id]
        
        if idea.status != IdeaStatus.APPROVED:
            return False
            
        idea.assigned_agents = agent_ids
        idea.status = IdeaStatus.IN_PROGRESS
        idea.execution_started = time.time()
        
        return True
        
    def complete_idea(self, idea_id: str, result: Dict[str, Any]) -> bool:
        """Mark idea as completed with results"""
        
        if idea_id not in self.ideas:
            return False
            
        idea = self.ideas[idea_id]
        
        if idea.status != IdeaStatus.IN_PROGRESS:
            return False
            
        idea.status = IdeaStatus.COMPLETED
        idea.completed_at = time.time()
        idea.result = result
        
        return True
        
    def fail_idea(self, idea_id: str, reason: str) -> bool:
        """Mark idea as failed"""
        
        if idea_id not in self.ideas:
            return False
            
        idea = self.ideas[idea_id]
        
        if idea.status != IdeaStatus.IN_PROGRESS:
            return False
            
        idea.status = IdeaStatus.FAILED
        idea.completed_at = time.time()
        idea.result = {"failed": True, "reason": reason}
        
        return True
        
    # === AGENT HIRING ===
    
    def request_agent_hire(self, requester_id: str, requester_name: str,
                          role_needed: str, purpose: str, 
                          skills_required: List[str],
                          duration: str = "permanent") -> str:
        """Agent requests to hire a new specialized agent"""
        
        request_id = str(uuid.uuid4())
        
        request = AgentHireRequest(
            id=request_id,
            requested_by=requester_id,
            requester_name=requester_name,
            role_needed=role_needed,
            purpose=purpose,
            skills_required=skills_required,
            duration=duration,
            status="pending",
            created_at=time.time()
        )
        
        self.hire_requests[request_id] = request
        
        return request_id
        
    def approve_hire_request(self, request_id: str) -> bool:
        """Approve agent hire request"""
        
        if request_id not in self.hire_requests:
            return False
            
        request = self.hire_requests[request_id]
        request.status = "approved"
        
        return True
        
    def complete_hire(self, request_id: str, hired_agent_id: str) -> bool:
        """Complete hire by assigning new agent"""
        
        if request_id not in self.hire_requests:
            return False
            
        request = self.hire_requests[request_id]
        
        if request.status != "approved":
            return False
            
        request.status = "hired"
        request.hired_agent_id = hired_agent_id
        
        return True
        
    # === QUERIES ===
    
    def get_active_ideas(self) -> List[Idea]:
        """Get all active ideas (voting or in progress)"""
        return [
            idea for idea in self.ideas.values()
            if idea.status in [IdeaStatus.VOTING, IdeaStatus.IN_PROGRESS]
        ]
        
    def get_ideas_by_status(self, status: IdeaStatus) -> List[Idea]:
        """Get ideas by status"""
        return [idea for idea in self.ideas.values() if idea.status == status]
        
    def get_pending_hire_requests(self) -> List[AgentHireRequest]:
        """Get pending hire requests"""
        return [
            req for req in self.hire_requests.values()
            if req.status == "pending"
        ]
        
    def get_agent_workload(self, agent_id: str) -> Dict[str, Any]:
        """Get agent's current workload"""
        
        active_ideas = [
            idea for idea in self.ideas.values()
            if agent_id in idea.assigned_agents and idea.status == IdeaStatus.IN_PROGRESS
        ]
        
        return {
            "agent_id": agent_id,
            "active_projects": len(active_ideas),
            "projects": [
                {
                    "id": idea.id,
                    "title": idea.title,
                    "started": idea.execution_started
                }
                for idea in active_ideas
            ]
        }
        
    # === STATISTICS ===
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get workflow statistics"""
        
        return {
            "total_ideas": len(self.ideas),
            "voting": len(self.get_ideas_by_status(IdeaStatus.VOTING)),
            "approved": len(self.get_ideas_by_status(IdeaStatus.APPROVED)),
            "in_progress": len(self.get_ideas_by_status(IdeaStatus.IN_PROGRESS)),
            "completed": len(self.get_ideas_by_status(IdeaStatus.COMPLETED)),
            "rejected": len(self.get_ideas_by_status(IdeaStatus.REJECTED)),
            "failed": len(self.get_ideas_by_status(IdeaStatus.FAILED)),
            "user_comments": len(self.user_comments),
            "pending_hires": len(self.get_pending_hire_requests()),
            "total_hires": len([r for r in self.hire_requests.values() if r.status == "hired"])
        }
        
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "ideas": {
                idea_id: {
                    "id": idea.id,
                    "title": idea.title,
                    "description": idea.description,
                    "proposed_by": idea.proposed_by_name,
                    "category": idea.category,
                    "status": idea.status.value,
                    "votes_count": len(idea.votes),
                    "assigned_agents": idea.assigned_agents
                }
                for idea_id, idea in self.ideas.items()
            },
            "statistics": self.get_statistics()
        }

# Global instance
global_workflow = AutonomousWorkflow()
