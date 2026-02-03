from typing import Any, Dict, List, Optional

class IntrospectionAPI:
    def __init__(self, kernel: Any):
        self._kernel = kernel

    def get_system_status(self) -> Dict[str, Any]:
        return {
            "tick": self._kernel.current_tick,
            "agent_count": len(self._kernel.agents),
            "decision_count": len(self._kernel.decision_engine._decisions),
            "active_plans": len([p for p in self._kernel.planner._plans.values() if p.status == "ACTIVE"])
        }

    def get_agents(self) -> List[Dict[str, Any]]:
        agents = []
        # feed_posts = self._kernel.social_feed._posts (Unused)
        
        for agent in self._kernel.agents.values():
            rep = self._kernel.reputation_manager.get_reputation(agent.id)
            
            # Real metrics
            mem_count = len(agent.memory.get_working(agent.id))
            # Calculate total posts by this agent (a bit expensive but user wants REAL DATA)
            posts_count = len(self._kernel.social_feed.get_agent_posts(agent.id))
            
            # Determine "AGI Progress" based on metrics
            # Heuristic: Reputation + Memory + Communication
            agi_score = min(100, int(rep + (mem_count * 0.5) + (posts_count * 2)))
            
            agents.append({
                "agent_id": agent.id,
                "name": agent.identity.name,
                "role": agent.identity.role,
                "state": agent.fsm.current_state,
                "reputation": rep,
                "current_plan": agent._current_plan_id,
                "metrics": {
                    "memory_count": mem_count,
                    "posts_count": posts_count,
                    "agi_score": agi_score,
                    "tools_mastered": 5 # Placeholder until tool tracker implemented
                }
            })
        return agents

    def get_decisions(self) -> List[Dict[str, Any]]:
        decisions = []
        # Access protected member _decisions directly for introspection
        for d in self._kernel.decision_engine._decisions.values():
            result_str = None
            if d.result:
                result_str = d.result.result
            
            decisions.append({
                "decision_id": d.id,
                "topic": d.topic_id,
                "status": d.status,
                "result": result_str
            })
        return decisions

    def get_plans(self) -> List[Dict[str, Any]]:
        plans = []
        for p in self._kernel.planner._plans.values():
            steps = []
            for s in p.steps.values():
                steps.append({
                    "step_id": s.id,
                    "status": s.status,
                    "description": s.description
                })
            
            plans.append({
                "plan_id": p.id,
                "goal": p.goal,
                "status": p.status,
                "steps": steps
            })
        return plans

    def get_social_feed(self, limit: int = 20) -> List[Dict[str, Any]]:
        posts = self._kernel.social_feed.get_feed(limit=limit)
        feed_data = []
        for p in posts:
            feed_data.append({
                "post_id": p.id,
                "agent_id": p.agent_id,
                "content": p.content,
                "timestamp": p.timestamp,
                "parent_id": p.parent_id
            })
        return feed_data
