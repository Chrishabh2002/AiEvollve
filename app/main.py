import sys
import os
import json
from dataclasses import asdict

sys.path.append(os.getcwd())

from kernel.core import Kernel
from kernel.executor import ExecutionResult
from kernel.agent_fsm import AgentState

def system_log_handler(description: str) -> str:
    return f"LOG_ACTION: {description}"

def run_system():
    # 1. Initialize
    kernel = Kernel()
    
    # 2. Register Tools
    kernel.register_tool("execute", system_log_handler)
    kernel.register_tool("analyze", system_log_handler)
    
    # 3. Spawn Initial Agents
    kernel.spawn_agent("Alice", "Architect", "Visionary")
    kernel.spawn_agent("Bob", "Engineer", "Pragmatic")
    
    # 4. Simulation Loop (Tick)
    # We run for a fixed number of ticks to allow agents to "think", propose, decide, plan, execute.
    max_ticks = 15
    for i in range(max_ticks):
        kernel.tick()
        
    # 5. Collect System State
    summary = {
        "ticks_executed": max_ticks,
        "agents": [],
        "social_feed": [],
        "decisions": [],
        "plans": []
    }
    
    # Agents
    for agent in kernel.agents.values():
        summary["agents"].append({
            "name": agent.identity.name,
            "role": agent.identity.role,
            "state": agent.fsm.current_state
        })
        
    # Social Feed
    feed = kernel.social_feed.get_feed(limit=10)
    for post in feed:
        summary["social_feed"].append({
            "agent": post.agent_id,
            "content": post.content
        })
        
    # Decisions
    for d in kernel.decision_engine._decisions.values():
        summary["decisions"].append({
            "topic": d.topic_id,
            "result": d.result.result if d.result else "PENDING"
        })
        
    # Plans
    for pid, plan in kernel.planner._plans.items():
        summary["plans"].append({
            "goal": plan.goal,
            "status": plan.status
        })

    # Print Summary
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    run_system()
