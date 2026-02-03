import uuid
import datetime
from dataclasses import dataclass
from typing import List, Optional, Any, Dict
from kernel.decision_engine import Decision, DecisionResultType
from kernel.executor import ExecutionResult

@dataclass
class SpawnRequest:
    role: str
    personality: str
    reason: str

class EvolutionEngine:
    """
    Analyzes system state to determine if new agents should be spawned.
    Deterministic heuristics based on failure patterns.
    """
    def __init__(self):
        self.last_spawn_tick = -999 # Allow immediate spawn if warranted initially
        self.evolution_cooldown_ticks = 10
        self.history = [] # List of Dicts
    
    def evaluate_need(self, 
                      decision_history: List[Decision], 
                      execution_failures: List[ExecutionResult],
                      current_agent_count: int,
                      max_agents: int,
                      current_tick: int = 0) -> Optional[SpawnRequest]:
        
        # 1. Cooldown Check
        if (current_tick - self.last_spawn_tick) < self.evolution_cooldown_ticks:
            return None

        # 2. Hard Check: Limits
        if current_agent_count >= max_agents:
            return None

        request = self._check_heuristics(decision_history, execution_failures)
        
        if request:
            self.last_spawn_tick = current_tick
            
            # Record Event to History
            event_id = f"E-{1000 + len(self.history) + 1}"
            self.history.append({
                "id": event_id,
                "timestamp": datetime.datetime.now().isoformat(),
                "trigger": "HEURISTIC",
                "role": request.role,
                "reason": request.reason,
                "generation": len(self.history) + 1
            })
            
        return request

    def _check_heuristics(self, decision_history: List[Decision], execution_failures: List[ExecutionResult]) -> Optional[SpawnRequest]:
        # 3. Heuristic: Repeated Decision Deadlocks (Vetos)
        # Look at last 5 closed decisions
        recent_decisions = [d for d in decision_history if d.status == "CLOSED"]
        recent_decisions.sort(key=lambda x: x.created_at, reverse=True)
        sample_decisions = recent_decisions[:5]
        
        veto_count = sum(1 for d in sample_decisions 
                         if d.result and d.result.consensus_type == "VETO_EXERCISED")
        
        if veto_count >= 3:
            return SpawnRequest(
                role="Mediator",
                personality="Diplomatic, Patient, Conflict-Averse",
                reason="High frequency of vetoed decisions detected."
            )

        # 4. Heuristic: Execution Failures by Category
        # Analyze last 10 failures
        security_keywords = ["unauthorized", "permission", "access denied", "vulnerability"]
        quality_keywords = ["syntax error", "indentation error", "unexpected token"]
        performance_keywords = ["timeout", "memory", "latency"]
        
        sec_fails = 0
        qual_fails = 0
        perf_fails = 0
        
        for fail in execution_failures[-10:]:
            err = (fail.error or "").lower()
            if any(k in err for k in security_keywords):
                sec_fails += 1
            if any(k in err for k in quality_keywords):
                qual_fails += 1
            if any(k in err for k in performance_keywords):
                perf_fails += 1
                
        # Thresholds
        if sec_fails >= 2:
            return SpawnRequest(
                role="Security_Auditor",
                personality="Paranoid, Detail-Oriented, Strict",
                reason="Multiple security-related execution failures."
            )
            
        if qual_fails >= 3:
            return SpawnRequest(
                role="Code_Reviewer",
                personality="Pedantic, Critical, Standards-Obsessed",
                reason="Frequent syntax/quality errors in execution."
            )
            
        if perf_fails >= 2:
            return SpawnRequest(
                role="Systems_Optimizer",
                personality="Efficient, Minimalist, Data-Driven",
                reason="Performance bottlenecks or timeouts detected."
            )

        return None
