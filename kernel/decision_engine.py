import enum
import uuid
import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from kernel.reputation import ReputationManager

class VoteChoice(enum.StrEnum):
    YES = "YES"
    NO = "NO"
    BLOCK = "BLOCK"

class DecisionStatus(enum.StrEnum):
    OPEN = "OPEN"
    VOTING = "VOTING"
    CLOSED = "CLOSED"

class DecisionResultType(enum.StrEnum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    PENDING = "PENDING"

@dataclass
class Proposal:
    id: str
    author_id: str
    content: str
    timestamp: str

@dataclass
class Opinion:
    id: str
    agent_id: str
    outcome: str  # "APPROVE" | "REJECT" | "AMEND"
    rationale: str
    confidence: float
    risks: List[Dict[str, str]]
    timestamp: str

@dataclass
class Vote:
    agent_id: str
    choice: VoteChoice
    rationale: str
    confidence: float
    timestamp: str
    weight: float = 0.0  # Populated at vote time based on reputation
    suggestions: List[str] = field(default_factory=list)  # Agent's suggestions for improvement


@dataclass
class DecisionResult:
    result: DecisionResultType
    consensus_type: str
    reason: str
    blocking_agents: List[str]
    timestamp: str

@dataclass
class Decision:
    id: str
    topic_id: str
    proposal: Proposal
    created_at: datetime.datetime
    deadline: datetime.datetime
    quorum_threshold: float
    opinions: List[Opinion] = field(default_factory=list)
    votes: List[Vote] = field(default_factory=list)
    result: Optional[DecisionResult] = None
    status: DecisionStatus = DecisionStatus.OPEN

class DecisionEngine:
    def __init__(self, reputation_manager: ReputationManager):
        self._reputation_manager = reputation_manager
        self._decisions: Dict[str, Decision] = {}

    def create_decision(self, 
                        topic_id: str, 
                        author_id: str, 
                        proposal_content: str, 
                        duration_minutes: int = 30) -> str:
        """
        Starts a new decision process. Returns Decision UUID.
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        proposal = Proposal(
            id=str(uuid.uuid4()),
            author_id=author_id,
            content=proposal_content,
            timestamp=now.isoformat()
        )
        
        decision_id = str(uuid.uuid4())
        decision = Decision(
            id=decision_id,
            topic_id=topic_id,
            proposal=proposal,
            created_at=now,
            deadline=now + datetime.timedelta(minutes=duration_minutes),
            quorum_threshold=0.5  # Default
        )
        
        self._decisions[decision_id] = decision
        return decision_id

    def submit_opinion(self, 
                       decision_id: str, 
                       agent_id: str, 
                       outcome: str, 
                       rationale: str, 
                       confidence: float, 
                       risks: List[Dict[str, str]]) -> str:
        """
        Records an agent's technical opinion during the debate phase.
        """
        if decision_id not in self._decisions:
            raise KeyError(f"Decision {decision_id} not found")
            
        decision = self._decisions[decision_id]
        if decision.status != DecisionStatus.OPEN:
            raise RuntimeError(f"Cannot submit opinion to decision {decision_id} in state {decision.status}")

        opinion_id = str(uuid.uuid4())
        opinion = Opinion(
            id=opinion_id,
            agent_id=agent_id,
            outcome=outcome,
            rationale=rationale,
            confidence=confidence,
            risks=risks,
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
        )
        decision.opinions.append(opinion)
        return opinion_id

    def open_voting_window(self, decision_id: str) -> None:
        """
        Transitions decision from OPEN to VOTING.
        """
        if decision_id not in self._decisions:
            raise KeyError(f"Decision {decision_id} not found")
        
        self._decisions[decision_id].status = DecisionStatus.VOTING

    def cast_vote(self, 
                  decision_id: str, 
                  agent_id: str, 
                  choice: VoteChoice, 
                  rationale: str, 
                  confidence: float,
                  role_bonus: float = 1.0,
                  suggestions: List[str] = None) -> None:
        """
        Casts a weighted vote.
        INTELLIGENT UPDATE: Applies sophisticated multipliers based on agent expertise.
        """
        if decision_id not in self._decisions:
            raise KeyError(f"Decision {decision_id} not found")
            
        decision = self._decisions[decision_id]
        
        # Auto-open voting if in OPEN state to facilitate fluid decision making
        if decision.status == DecisionStatus.OPEN:
            decision.status = DecisionStatus.VOTING
        
        if decision.status != DecisionStatus.VOTING:
            raise RuntimeError(f"Voting CLOSED for decision {decision_id}")

        # --- INTELLIGENT WEIGHTING ---
        base_power = self._reputation_manager.calculate_vote_power(agent_id)
        
        # Check topic relevance (naive check for now, can be LLM based later)
        topic_lower = decision.topic_id.lower()
        expertise_multiplier = 1.0
        
        # We need access to agent's role/domain here preferably, but we only have ID.
        # However, passed `role_bonus` is usually 1.0 from caller.
        # Let's rely on caller (Agent.vote_on_decisions) to pass a better role_bonus?
        # OR: We trust reputation manager has already factored basic role.
        
        # Let's apply a "Confidence Multiplier" - if agent is very confident, their vote weighs slightly more (Risk/Reward)
        confidence_multiplier = 1.0 + (confidence - 0.5) * 0.2  # Range: 0.9 to 1.2 for confidence 0.0 to 1.0
        
        final_weight = base_power * expertise_multiplier * confidence_multiplier * role_bonus
        
        vote = Vote(
            agent_id=agent_id,
            choice=choice,
            rationale=rationale,
            confidence=confidence,
            timestamp=datetime.datetime.now().isoformat(),
            weight=final_weight,
            suggestions=suggestions if suggestions else []
        )
        
        
        decision.votes.append(vote)


    def resolve_decision(self, decision_id: str) -> DecisionResult:
        """
        Closes voting and resolves the consensus.
        """
        if decision_id not in self._decisions:
            raise KeyError(f"Decision {decision_id} not found")
            
        decision = self._decisions[decision_id]
        now_ts = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Empty vote check
        if not decision.votes:
            result = DecisionResult(
                result=DecisionResultType.REJECTED,
                consensus_type="NO_VOTES",
                reason="No votes cast.",
                blocking_agents=[],
                timestamp=now_ts
            )
            decision.result = result
            decision.status = DecisionStatus.CLOSED
            return result

        total_power = sum(v.weight for v in decision.votes)
        
        if total_power == 0:
            result = DecisionResult(
                result=DecisionResultType.REJECTED,
                consensus_type="ZERO_POWER",
                reason="Total vote power is 0.",
                blocking_agents=[],
                timestamp=now_ts
            )
            decision.result = result
            decision.status = DecisionStatus.CLOSED
            return result

        yes_power = sum(v.weight for v in decision.votes if v.choice == VoteChoice.YES)
        block_votes = [v for v in decision.votes if v.choice == VoteChoice.BLOCK]

        # 1. Check Veto
        if block_votes:
            result = DecisionResult(
                result=DecisionResultType.REJECTED,
                consensus_type="VETO_EXERCISED",
                reason=f"Veto exercised by {len(block_votes)} agents.",
                blocking_agents=[v.agent_id for v in block_votes],
                timestamp=now_ts
            )
            decision.result = result
            decision.status = DecisionStatus.CLOSED
            return result

        yes_ratio = yes_power / total_power
        confidence_avg = sum(v.confidence for v in decision.votes) / len(decision.votes)

        # 2. Check Super-Consensus
        if yes_ratio > 0.8 and confidence_avg > 0.8:
            result = DecisionResult(
                result=DecisionResultType.ACCEPTED,
                consensus_type="SUPER_CONSENSUS",
                reason=f"Yes Ratio {yes_ratio:.2f} > 0.8 and Confidence {confidence_avg:.2f} > 0.8",
                blocking_agents=[],
                timestamp=now_ts
            )
        # 3. Check Simple Consensus
        elif yes_ratio > 0.51:
            result = DecisionResult(
                result=DecisionResultType.ACCEPTED,
                consensus_type="SIMPLE_MAJORITY",
                reason=f"Yes Ratio {yes_ratio:.2f} > 0.51",
                blocking_agents=[],
                timestamp=now_ts
            )
        # 4. Fail
        else:
            result = DecisionResult(
                result=DecisionResultType.REJECTED,
                consensus_type="INSUFFICIENT_SUPPORT",
                reason=f"Yes Ratio {yes_ratio:.2f} <= 0.51",
                blocking_agents=[],
                timestamp=now_ts
            )

        decision.result = result
        decision.status = DecisionStatus.CLOSED
        return result

    def get_decision(self, decision_id: str) -> Optional[Decision]:
        return self._decisions.get(decision_id)
    
    def get_open_decisions(self) -> List[Decision]:
        """
        Returns all decisions that are open for voting.
        """
        return [d for d in self._decisions.values() if d.status in [DecisionStatus.OPEN, DecisionStatus.VOTING]]

    def to_dict(self) -> Dict[str, Any]:
        serialized_decisions = {}
        for d_id, d in self._decisions.items():
            d_dict = vars(d).copy()
            # Convert nested objects
            d_dict["proposal"] = vars(d.proposal)
            d_dict["opinions"] = [vars(o) for o in d.opinions]
            d_dict["votes"] = [vars(v) for v in d.votes]
            d_dict["result"] = vars(d.result) if d.result else None
            # Enums
            d_dict["status"] = d.status.value
            # Dates
            d_dict["created_at"] = d.created_at.isoformat()
            d_dict["deadline"] = d.deadline.isoformat()
            
            # Vote Enum in votes list
            for v in d_dict["votes"]:
                v["choice"] = v["choice"].value
            
            if d_dict["result"]:
                 d_dict["result"]["result"] = d.result.result.value
            
            serialized_decisions[d_id] = d_dict
            
        return {"decisions": serialized_decisions}

    @classmethod
    def from_dict(cls, data: Dict[str, Any], reputation_manager: ReputationManager) -> 'DecisionEngine':
        engine = cls(reputation_manager)
        if "decisions" in data:
            for d_id, d_data in data["decisions"].items():
                # Proposal
                proposal = Proposal(**d_data["proposal"])
                
                # Opinions
                opinions = [Opinion(**o) for o in d_data["opinions"]]
                
                # Votes
                votes = []
                for v_data in d_data["votes"]:
                    v_data["choice"] = VoteChoice(v_data["choice"])
                    votes.append(Vote(**v_data))
                
                # Result
                result = None
                if d_data["result"]:
                    d_data["result"]["result"] = DecisionResultType(d_data["result"]["result"])
                    result = DecisionResult(**d_data["result"])
                
                decision = Decision(
                    id=d_data["id"],
                    topic_id=d_data["topic_id"],
                    proposal=proposal,
                    created_at=datetime.datetime.fromisoformat(d_data["created_at"]),
                    deadline=datetime.datetime.fromisoformat(d_data["deadline"]),
                    quorum_threshold=d_data["quorum_threshold"],
                    opinions=opinions,
                    votes=votes,
                    result=result,
                    status=DecisionStatus(d_data["status"])
                )
                engine._decisions[d_id] = decision
        return engine
