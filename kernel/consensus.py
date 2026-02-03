import enum
from typing import List, Optional, Any
from dataclasses import dataclass
import datetime

class VoteChoice(enum.StrEnum):
    YES = "YES"
    NO = "NO"
    BLOCK = "BLOCK"

class ConsensusResultType(enum.StrEnum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

@dataclass
class Vote:
    agent_id: str
    choice: VoteChoice
    rationale: str
    confidence: float
    vote_power: float  # Pre-calculated by ReputationManager

@dataclass
class ConsensusResult:
    result: ConsensusResultType
    type: str  # "SUPER_CONSENSUS" | "SIMPLE_MAJORITY" | "INSUFFICIENT_SUPPORT" | "VETO_EXERCISED"
    reason: str
    blocking_agents: List[str]
    timestamp: str

class ConsensusEngine:
    """
    Deterministic Consensus Resolution Engine.
    Implements rules defined in DECISION_CONSENSUS_ENGINE.md.
    """

    def resolve_consensus(self, votes: List[Vote]) -> ConsensusResult:
        """
        Executes the resolution algorithm to determine the outcome of a vote.
        """
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        if not votes:
            return ConsensusResult(
                result=ConsensusResultType.REJECTED,
                type="NO_VOTES",
                reason="No votes cast.",
                blocking_agents=[],
                timestamp=timestamp
            )

        total_power = sum(v.vote_power for v in votes)
        if total_power == 0:
             # Avoid division by zero if all weights are 0 (unlikely but possible)
             return ConsensusResult(
                result=ConsensusResultType.REJECTED,
                type="ZERO_POWER",
                reason="Total vote power is zero.",
                blocking_agents=[],
                timestamp=timestamp
            )

        yes_power = sum(v.vote_power for v in votes if v.choice == VoteChoice.YES)
        block_votes = [v for v in votes if v.choice == VoteChoice.BLOCK]

        # 1. Check Veto
        if block_votes:
            return ConsensusResult(
                result=ConsensusResultType.REJECTED,
                type="VETO_EXERCISED",
                reason=f"Veto exercised by {len(block_votes)} agents.",
                blocking_agents=[v.agent_id for v in block_votes],
                timestamp=timestamp
            )

        # Calculate metrics
        # Avoid division by zero if yes_power is 0 or votes is empty (checked above)
        yes_ratio = yes_power / total_power
        confidence_avg = sum(v.confidence for v in votes) / len(votes)

        # 2. Check Super-Consensus
        # Criteria: > 80% Weighted YES AND Average Confidence > 0.8
        if yes_ratio > 0.8 and confidence_avg > 0.8:
            return ConsensusResult(
                result=ConsensusResultType.ACCEPTED,
                type="SUPER_CONSENSUS",
                reason=f"Yes Ratio {yes_ratio:.2f} > 0.8 and Confidence {confidence_avg:.2f} > 0.8",
                blocking_agents=[],
                timestamp=timestamp
            )

        # 3. Check Simple Consensus
        # Criteria: > 51% Weighted Votes are YES (and No BLOCK - checked above)
        if yes_ratio > 0.51:
            return ConsensusResult(
                result=ConsensusResultType.ACCEPTED,
                type="SIMPLE_MAJORITY",
                reason=f"Yes Ratio {yes_ratio:.2f} > 0.51",
                blocking_agents=[],
                timestamp=timestamp
            )

        # 4. Default Failure
        return ConsensusResult(
            result=ConsensusResultType.REJECTED,
            type="INSUFFICIENT_SUPPORT",
            reason=f"Yes Ratio {yes_ratio:.2f} is insufficient.",
            blocking_agents=[],
            timestamp=timestamp
        )
