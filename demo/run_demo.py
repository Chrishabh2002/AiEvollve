import sys
import os
import traceback
from typing import List

# Ensure we can import kernel modules
sys.path.append(os.getcwd())

from kernel.core import Kernel
from kernel.social import SocialFeed
from kernel.evolution import EvolutionEngine
from kernel.decision_engine import VoteChoice, DecisionResultType
from kernel.executor import ExecutionResult

def echo_handler(description: str) -> str:
    return f"EXECUTED_ACTION: {description}"

def run():
    try:
        # 1. Initialize System
        print("Initializing Kernel...")
        kernel = Kernel()
        social = SocialFeed()
        evolution = EvolutionEngine()

        # 2. Register Tools
        kernel.register_tool("execute", echo_handler)

        # 3. Spawn Agents
        print("Spawning Agents...")
        alice_id = kernel.spawn_agent("Alice", "Architect", "Visionary")
        bob_id = kernel.spawn_agent("Bob", "Engineer", "Pragmatic")
        
        alice = kernel.get_agent(alice_id)
        bob = kernel.get_agent(bob_id)

        # 4. Social Interactions
        print("Simulating Social Feed...")
        post1 = social.create_post(alice_id, "We need to optimize the database.")
        social.reply_to(post1, bob_id, "Agreed. Let's run a migration.")

        # 5. Propose Decision
        print("Proposing Decision...")
        topic = "DB_Optimization"
        proposal_content = "Run database migration script to add indices."
        decision_id = alice.propose_decision(kernel.decision_engine, topic, proposal_content)

        # 6. Resolve Decision
        print("Resolving Decision...")
        engine = kernel.decision_engine
        
        # Open Voting
        engine.open_voting_window(decision_id)
        
        # Cast Votes
        engine.cast_vote(decision_id, alice_id, VoteChoice.YES, "Essential for perf", 0.9)
        engine.cast_vote(decision_id, bob_id, VoteChoice.YES, "Looks safe", 0.8)
        
        # Resolve
        decision_result = engine.resolve_decision(decision_id)
        print(f"Decision Result: {decision_result.result}")
        
        plan_id = None
        if decision_result.result == DecisionResultType.ACCEPTED:
            # Create Plan
            print("Creating Plan...")
            plan_id = kernel.planner.create_plan(decision_id, proposal_content)
            # Add a specific step that matches our handler
            kernel.planner.add_step(plan_id, "Execute migration script", [])
            
            # Assign to Bob
            bob.receive_plan(plan_id)
            
            # Execute
            # Check plan status
            print("Executing Plan...")
            plan = kernel.planner.get_plan(plan_id)
            
            # Tick until completion
            ticks = 0
            while plan.status == "ACTIVE" and ticks < 10:
                kernel.tick()
                ticks += 1
                
        # 7. Evolution Logic
        print("Evaluating Evolution...")
        # Inject fake failures to verify evolution trigger
        fake_failures = [
            ExecutionResult("s1", "FAILED", output=None, error="Security permission denied"),
            ExecutionResult("s2", "FAILED", output=None, error="Unauthorized access attempted")
        ]
        
        all_decisions = list(kernel.decision_engine._decisions.values())
        
        spawn_req = evolution.evaluate_need(
            decision_history=all_decisions,
            execution_failures=fake_failures,
            current_agent_count=len(kernel.agents),
            max_agents=5
        )
        
        new_agent_id = None
        if spawn_req:
            print(f"Evolution triggered: {spawn_req.reason}")
            new_agent_id = kernel.spawn_agent(
                name="System_Evolution", 
                role=spawn_req.role, 
                personality=spawn_req.personality
            )

        # 8. Final Report
        print("\n=== DEMO EXECUTION SUMMARY ===")
        print(f"Agents Active: {[a.identity.name for a in kernel.agents.values()]}")
        print(f"Social Posts: {len(social.get_feed())}")
        print(f"Decision '{topic}': {decision_result.result} ({decision_result.consensus_type})")
        
        if plan_id:
            plan = kernel.planner.get_plan(plan_id)
            print(f"Plan Status: {plan.status}")
            for step in plan.steps.values():
                print(f"  - Step '{step.description}': {step.status} (Output: {step.output})")
                
        print(f"Evolution Recommendation: {spawn_req.role if spawn_req else 'None'}")
        if new_agent_id:
            print(f"  -> Spawned Agent: {kernel.get_agent(new_agent_id).identity.name} ({kernel.get_agent(new_agent_id).identity.role})")
        print("==============================")
        
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    run()
