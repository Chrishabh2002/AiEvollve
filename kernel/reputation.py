import datetime
import datetime
from typing import Dict, Optional, Set, Any

class ReputationError(Exception):
    """Base class for Reputation errors."""
    pass

class UnknownAgentError(ReputationError):
    """Raised when operation is performed on an unknown agent."""
    pass

class InvalidEventError(ReputationError):
    """Raised when an invalid event type is provided."""
    pass

class ReputationManager:
    # Event impact definition
    EVENT_IMPACTS = {
        "artifact_accepted": 0.05,
        "consensus_winner": 0.02,
        "artifact_rejected": -0.05,
        "execution_failure": -0.10,
        "misbehavior": -0.20
    }

    def __init__(self):
        # Stores agent reputation: {agent_id: reputation_score}
        self._reputations: Dict[str, float] = {}
        # Stores last decay timestamp: {agent_id: datetime}
        self._last_decay_check: Dict[str, datetime.datetime] = {}
        # Stores quarantine status: {agent_id: bool}
        self._quarantined: Set[str] = set()

    def initialize_agent(self, agent_id: str, initial_rep: Optional[float] = None) -> None:
        """
        Initialize an agent with a default or specified reputation.
        """
        if initial_rep is None:
            initial_rep = 0.5
        
        # Enforce range [0.0, 1.0] on initialization just in case
        initial_rep = max(0.0, min(1.0, initial_rep))
        
        self._reputations[agent_id] = initial_rep
        self._last_decay_check[agent_id] = datetime.datetime.now(datetime.timezone.utc)
        if agent_id in self._quarantined:
            self._quarantined.remove(agent_id)

    def set_quarantine_status(self, agent_id: str, is_quarantined: bool) -> None:
        """
        Updates the quarantine status of an agent.
        """
        if agent_id not in self._reputations:
            raise UnknownAgentError(f"Agent {agent_id} not found.")
        
        if is_quarantined:
            self._quarantined.add(agent_id)
            # If entering quarantine, ensure they don't exceed cap immediately?
            # Requirement says: "cannot gain Rep > 0.5". 
            # It doesn't explicitly say existing rep is clamped down, but usually quarantine implies bad standing.
            # However, prompt only says "cannot gain". I'll leave current rep as is until an event happens.
        else:
            if agent_id in self._quarantined:
                self._quarantined.remove(agent_id)

    def apply_event(self, agent_id: str, event_type: str) -> None:
        """
        Apply a reputation change based on an event.
        """
        if agent_id not in self._reputations:
            raise UnknownAgentError(f"Agent {agent_id} not found.")

        if event_type not in self.EVENT_IMPACTS:
            raise InvalidEventError(f"Event '{event_type}' is not a valid reputation event.")

        impact = self.EVENT_IMPACTS[event_type]
        current_rep = self._reputations[agent_id]
        new_rep = current_rep + impact

        # Logic: Agents in QUARANTINED state cannot gain Rep > 0.5
        is_quarantined = agent_id in self._quarantined
        
        # If quarantined and trying to go above 0.5
        if is_quarantined and new_rep > 0.5:
             # If they were already above 0.5 (unlikely if quarantined, but possible)
             # or if the gain pushes them over.
             # We cap at 0.5 if they are in quarantine.
             new_rep = 0.5
             # Note: If they strictly lose reputation, it drops below. 
             # If they obtain a gain that puts them at 0.51, it clamps to 0.5.
             # If they were at 0.6 and quarantined (maybe manual), they drop to 0.5?
             # The rule says "cannot gain Rep > 0.5". It implies a ceiling for growth.
             # I will interpret strictly: If quarantined, result cannot exceed 0.5.

        # General clamp [0.0, 1.0]
        new_rep = max(0.0, min(1.0, new_rep))
        
        self._reputations[agent_id] = new_rep

    def get_reputation(self, agent_id: str) -> float:
        """
        Returns the current reputation of an agent.
        """
        if agent_id not in self._reputations:
            raise UnknownAgentError(f"Agent {agent_id} not found.")
        return self._reputations[agent_id]

    def calculate_vote_power(self, agent_id: str, role_bonus: float = 1.0) -> float:
        """
        Calculate voting power: 1 + (Reputation - 0.5) * 2
        """
        rep = self.get_reputation(agent_id)
        
        # Formula: VotePower = BaseWeight * RoleBonus
        # Where BaseWeight as per architecture discussion seems to serve the logic:
        # "VotePower = 1 + (Reputation - 0.5) * 2"
        # Let's ensure we follow the prompt formula exactly.
        # "1 + (Reputation - 0.5) * 2" -> This maps 0.0->0.0, 0.5->1.0, 1.0->2.0.
        
        base_power = 1.0 + (rep - 0.5) * 2.0
        
        # Apply role bonus
        final_power = base_power * role_bonus
        
        # Ensure non-negative power (though formula logically implies min 0.0 at rep 0.0)
        return max(0.0, final_power)

    def apply_decay(self, current_timestamp: datetime.datetime) -> None:
        """
        Apply weekly decay of -0.01 to all agents if a week has passed since their last check.
        """
        decay_amount = 0.01
        week_delta = datetime.timedelta(days=7)

        for agent_id, last_check in list(self._last_decay_check.items()):
            if current_timestamp - last_check >= week_delta:
                # Apply decay
                current_rep = self._reputations[agent_id]
                new_rep = current_rep - decay_amount
                
                # Check bounds
                new_rep = max(0.0, min(1.0, new_rep))
                
                self._reputations[agent_id] = new_rep
                self._reputations[agent_id] = new_rep
                self._last_decay_check[agent_id] = current_timestamp

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reputations": self._reputations,
            "last_decay_check": {aid: ts.isoformat() for aid, ts in self._last_decay_check.items()},
            "quarantined": list(self._quarantined)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReputationManager':
        manager = cls()
        manager._reputations = data.get("reputations", {})
        
        last_decay = data.get("last_decay_check", {})
        manager._last_decay_check = {aid: datetime.datetime.fromisoformat(ts) for aid, ts in last_decay.items()}
        
        manager._quarantined = set(data.get("quarantined", []))
        return manager
