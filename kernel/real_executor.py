"""
Real Plan Executor - Actually executes plans with agent collaboration
"""

import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from kernel.planner import Planner, StepStatus
from kernel.llm import LLMClient, LLMRequest

@dataclass
class ExecutionResult:
    success: bool
    output: str
    artifacts_created: List[str]
    errors: List[str]

class RealPlanExecutor:
    """
    Executes plans by:
    1. Assigning steps to capable agents
    2. Actually running the work
    3. Tracking failures
    4. Requesting help from other agents if needed
    """
    
    def __init__(self, planner: Planner, llm_client: LLMClient, kernel: Any):
        self.planner = planner
        self.llm_client = llm_client
        self.kernel = kernel
        self.execution_log: List[Dict] = []
        self.failed_steps: Dict[str, List[str]] = {}  # step_id -> list of agent_ids who failed
        
    def tick(self) -> None:
        """
        Called every tick to progress active plans
        """
        for plan_id, plan in self.planner._plans.items():
            if plan.status != "ACTIVE":
                continue
                
            # Get ready steps
            ready_steps = self.planner.get_ready_steps(plan_id)
            
            for step in ready_steps:
                # Try to execute this step
                self._execute_step(plan_id, step)
    
    def _execute_step(self, plan_id: str, step: Any) -> None:
        """
        Actually execute a plan step
        """
        # Find best agent for this step
        assigned_agent = self._find_best_agent_for_step(step)
        
        if not assigned_agent:
            # No agent available - mark as blocked
            step.status = StepStatus.BLOCKED
            return
        
        # Mark as running
        step.status = StepStatus.RUNNING
        
        # Create execution prompt for the agent
        prompt = f"""
🎯 PLAN EXECUTION TASK

You are assigned to execute this step:
{step.description}

This is part of plan: {self.planner.get_plan(plan_id).goal}

Your task:
1. Understand what needs to be done
2. Actually DO the work (use tools if needed)
3. Create any necessary artifacts
4. Report completion with details

Use TOOL: create_artifact(filename, content) if you need to create files.

Execute now and report results! 🚀
"""
        
        try:
            # Agent executes the step
            req = LLMRequest(prompt=prompt, context={"step_id": step.id, "plan_id": plan_id})
            response = self.llm_client.generate(req)
            
            # Parse response for tool calls and artifacts
            result = self._parse_execution_result(response.content, assigned_agent)
            
            if result.success:
                # Mark step as done
                self.planner.mark_step_done(plan_id, step.id, result.output)
                
                # Log success
                self.execution_log.append({
                    "plan_id": plan_id,
                    "step_id": step.id,
                    "agent_id": assigned_agent.id,
                    "status": "SUCCESS",
                    "output": result.output,
                    "artifacts": result.artifacts_created
                })
                
                # Post to social feed
                self.kernel.social_feed.create_post(
                    assigned_agent.id,
                    f"✅ Completed: {step.description}\n\n{result.output} 🎉",
                    agent_name=assigned_agent.identity.name,
                    agent_role=assigned_agent.identity.role
                )
                
            else:
                # Step failed - try to get help
                self._handle_step_failure(plan_id, step, assigned_agent, result.errors)
                
        except Exception as e:
            # Execution error
            self._handle_step_failure(plan_id, step, assigned_agent, [str(e)])
    
    def _find_best_agent_for_step(self, step: Any) -> Optional[Any]:
        """
        Find the most suitable agent for this step based on:
        - Role relevance
        - Past success rate
        - Current workload
        """
        step_lower = step.description.lower()
        
        # Score each agent
        agent_scores = []
        for agent in self.kernel.agents.values():
            score = 0.0
            
            # Role matching
            role_lower = agent.identity.role.lower()
            if "architect" in role_lower and ("design" in step_lower or "architecture" in step_lower):
                score += 10.0
            if "engineer" in role_lower and ("build" in step_lower or "implement" in step_lower):
                score += 10.0
            if "analyst" in role_lower and ("analyze" in step_lower or "research" in step_lower):
                score += 10.0
            if "coordinator" in role_lower and ("coordinate" in step_lower or "organize" in step_lower):
                score += 10.0
                
            # Check if agent has failed this step before
            if step.id in self.failed_steps and agent.id in self.failed_steps[step.id]:
                score -= 20.0  # Penalize agents who already failed this
            
            # Reputation bonus
            rep = self.kernel.reputation_manager.get_reputation(agent.id)
            score += rep.total_score * 0.1
            
            agent_scores.append((agent, score))
        
        # Sort by score
        agent_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return best agent if score > 0
        if agent_scores and agent_scores[0][1] > 0:
            return agent_scores[0][0]
        
        # Fallback: return any agent
        if self.kernel.agents:
            return list(self.kernel.agents.values())[0]
        
        return None
    
    def _parse_execution_result(self, content: str, agent: Any) -> ExecutionResult:
        """
        Parse agent's response to determine if step succeeded
        """
        artifacts = []
        errors = []
        
        # Check for tool calls (artifact creation)
        if "TOOL:" in content and "create_artifact" in content:
            # Extract artifact names (simplified parsing)
            lines = content.split("\n")
            for line in lines:
                if "create_artifact" in line:
                    # Try to extract filename
                    if "(" in line and ")" in line:
                        try:
                            parts = line.split("(")[1].split(")")[0].split(",")
                            if parts:
                                filename = parts[0].strip().strip('"').strip("'")
                                artifacts.append(filename)
                        except:
                            pass
        
        # Check for failure indicators
        failure_keywords = ["error", "failed", "cannot", "unable", "impossible"]
        has_failure = any(keyword in content.lower() for keyword in failure_keywords)
        
        # Check for success indicators
        success_keywords = ["done", "completed", "finished", "success", "created", "built"]
        has_success = any(keyword in content.lower() for keyword in success_keywords)
        
        # Determine success
        if has_failure and not has_success:
            errors.append("Agent reported failure in execution")
            return ExecutionResult(False, content, artifacts, errors)
        
        # Default to success if agent responded
        return ExecutionResult(True, content, artifacts, errors)
    
    def _handle_step_failure(self, plan_id: str, step: Any, failed_agent: Any, errors: List[str]) -> None:
        """
        Handle step failure by:
        1. Recording the failure
        2. Requesting help from another agent
        3. If all agents fail, mark plan as failed
        """
        # Record failure
        if step.id not in self.failed_steps:
            self.failed_steps[step.id] = []
        self.failed_steps[step.id].append(failed_agent.id)
        
        # Log failure
        self.execution_log.append({
            "plan_id": plan_id,
            "step_id": step.id,
            "agent_id": failed_agent.id,
            "status": "FAILED",
            "errors": errors
        })
        
        # Post to social feed asking for help
        self.kernel.social_feed.create_post(
            failed_agent.id,
            f"❌ I need help! Failed to complete: {step.description}\n\n"
            f"Error: {errors[0] if errors else 'Unknown error'}\n\n"
            f"Can someone else take this? 🆘",
            agent_name=failed_agent.identity.name,
            agent_role=failed_agent.identity.role
        )
        
        # Check if too many agents have failed
        if len(self.failed_steps[step.id]) >= min(3, len(self.kernel.agents)):
            # Too many failures - mark plan as failed
            self.planner.mark_step_failed(plan_id, step.id, f"Multiple agents failed: {', '.join(errors)}")
            
            # Announce failure
            self.kernel.social_feed.create_post(
                "SYSTEM",
                f"⛔ Plan Failed: {self.planner.get_plan(plan_id).goal}\n\n"
                f"Step '{step.description}' failed after {len(self.failed_steps[step.id])} attempts.\n\n"
                f"We need to redesign this approach! 🔧",
                agent_name="System",
                agent_role="Orchestrator"
            )
        else:
            # Reset step to READY so another agent can try
            step.status = StepStatus.READY
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """
        Get execution statistics
        """
        total_executions = len(self.execution_log)
        successes = sum(1 for log in self.execution_log if log["status"] == "SUCCESS")
        failures = sum(1 for log in self.execution_log if log["status"] == "FAILED")
        
        return {
            "total_executions": total_executions,
            "successes": successes,
            "failures": failures,
            "success_rate": successes / total_executions if total_executions > 0 else 0.0,
            "active_plans": sum(1 for p in self.planner._plans.values() if p.status == "ACTIVE"),
            "completed_plans": sum(1 for p in self.planner._plans.values() if p.status == "COMPLETED"),
            "failed_plans": sum(1 for p in self.planner._plans.values() if p.status == "FAILED")
        }
