import enum
import datetime
import uuid
from typing import Dict, Set, Optional, Any
from dataclasses import dataclass

class AgentState(enum.StrEnum):
    CREATED = "CREATED"
    IDLE = "IDLE"
    DELIBERATING = "DELIBERATING"
    EXECUTING = "EXECUTING"
    AWAITING_REVIEW = "AWAITING_REVIEW"
    FAILED = "FAILED"
    QUARANTINED = "QUARANTINED"
    RETIRED = "RETIRED"

class FSMError(Exception):
    """Base class for FSM errors."""
    pass

class InvalidTransitionError(FSMError):
    """Raised when an invalid state transition is attempted."""
    pass

@dataclass(frozen=True)
class TransitionEvent:
    agent_id: str
    from_state: AgentState
    to_state: AgentState
    trigger: str
    timestamp: str

class AgentFSM:
    def __init__(self, agent_id: str, initial_state: AgentState = AgentState.CREATED):
        self.agent_id = agent_id
        self._current_state = initial_state
        
        # Define allowed transitions: {CurrentState: {Trigger: NextState}}
        self._transitions: Dict[AgentState, Dict[str, AgentState]] = {
            AgentState.CREATED: {
                "initialization_complete": AgentState.IDLE
            },
            AgentState.IDLE: {
                "join_thread": AgentState.DELIBERATING,
                "task_assigned": AgentState.EXECUTING,
            },
            AgentState.DELIBERATING: {
                "consensus_reached": AgentState.EXECUTING,
                "task_assigned_to_other": AgentState.IDLE,
            },
            AgentState.EXECUTING: {
                "task_submitted": AgentState.AWAITING_REVIEW,
                "execution_failed": AgentState.FAILED,
            },
            AgentState.AWAITING_REVIEW: {
                "task_accepted": AgentState.IDLE,
                "task_rejected": AgentState.FAILED,
            },
            AgentState.FAILED: {
                "retry_authorized": AgentState.IDLE,
                "max_failures_exceeded": AgentState.QUARANTINED,
            },
            AgentState.QUARANTINED: {
                "probation_passed": AgentState.IDLE,
                "max_recovery_exceeded": AgentState.RETIRED,
            },
            # RETIRED has no outgoing transitions
            AgentState.RETIRED: {}
        }

    @property
    def current_state(self) -> AgentState:
        return self._current_state

    @current_state.setter
    def current_state(self, new_state: Any):
        if isinstance(new_state, str):
            try:
                new_state = AgentState(new_state)
            except ValueError:
                pass 
        self._current_state = new_state

    def transition(self, trigger: str) -> Dict[str, Any]:
        """
        Executes a state transition based on the trigger.
        
        Args:
            trigger: The event name triggering the transition.
            
        Returns:
            A dictionary containing the structured event data.
            
        Raises:
            InvalidTransitionError: If the transition is not allowed from the current state.
        """
        
        # Handle global "force retire" or "deprecate" trigger which allows transition to RETIRED from any state
        # provided the agent is not already retired.
        if trigger in ["deprecate", "forced_retirement"]:
            if self._current_state == AgentState.RETIRED:
                raise InvalidTransitionError(f"Agent {self.agent_id} is already RETIRED.")
            target_state = AgentState.RETIRED
        else:
            # Standard lookup
            allowed_transitions = self._transitions.get(self._current_state, {})
            if trigger not in allowed_transitions:
                raise InvalidTransitionError(
                    f"Transition trigger '{trigger}' is invalid for state '{self._current_state}' "
                    f"in agent {self.agent_id}."
                )
            target_state = allowed_transitions[trigger]

        # Execute transition
        previous_state = self._current_state
        self._current_state = target_state
        
        # Create event payload
        event = TransitionEvent(
            agent_id=self.agent_id,
            from_state=previous_state,
            to_state=target_state,
            trigger=trigger,
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
        )
        
        return {
            "agent_id": event.agent_id,
            "from": event.from_state.value,
            "to": event.to_state.value,
            "trigger": event.trigger,
            "timestamp": event.timestamp
        }
