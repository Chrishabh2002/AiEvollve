import enum
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from kernel.planner import Planner, StepStatus

@dataclass
class ExecutionResult:
    step_id: str
    status: str # "DONE" | "FAILED"
    output: Optional[str] = None
    error: Optional[str] = None

class Executor:
    def __init__(self, planner: Planner):
        self._planner = planner
        self._handlers: Dict[str, Callable[[str], str]] = {}

    def register_handler(self, keyword: str, handler_fn: Callable[[str], str]) -> None:
        """
        Registers a function to handle steps containing the keyword.
        Last match wins if multiple keywords match (simple priority).
        """
        self._handlers[keyword.lower()] = handler_fn

    def execute_next(self, plan_id: str) -> Optional[ExecutionResult]:
        """
        Fetches the next READY step, executes it synchronously, and updates the plan.
        """
        ready_steps = self._planner.get_ready_steps(plan_id)
        if not ready_steps:
            return None
        
        # Pick the first one (deterministic)
        step = ready_steps[0]
        
        # Mark running manually involves internal API access? 
        # The requirements say "Mark steps as RUNNING". 
        # Planner exposed mark_step_done/failed, but maybe not explicit RUNNING via public API.
        # But we can assume we transition directly in this sync execution model or update status if Planner allows.
        # Looking at Planner.StepStatus enum, RUNNING exists.
        # Planner API didn't strictly expose mark_running, but internal property access is possible in same package
        # OR we just treat it as instantaneous.
        # I'll update status directly since I am in the kernel package.
        step.status = StepStatus.RUNNING

        # Find handler
        handler = None
        desc_lower = step.description.lower()
        
        # Simple keyword matching
        for keyword, fn in self._handlers.items():
            if keyword in desc_lower:
                handler = fn
                break
        
        result: ExecutionResult
        
        if handler:
            try:
                # Execute
                output = handler(step.description)
                self._planner.mark_step_done(plan_id, step.id, output)
                
                result = ExecutionResult(
                    step_id=step.id,
                    status="DONE",
                    output=output
                )
            except Exception as e:
                error_msg = str(e)
                self._planner.mark_step_failed(plan_id, step.id, error_msg)
                
                result = ExecutionResult(
                    step_id=step.id,
                    status="FAILED",
                    error=error_msg
                )
        else:
            # No handler found
            fail_msg = f"No handler registered for step: {step.description}"
            self._planner.mark_step_failed(plan_id, step.id, fail_msg)
            
            result = ExecutionResult(
                step_id=step.id,
                status="FAILED",
                error=fail_msg
            )
            
        return result
