"""
Initialize Master Agents
Creates the 12 domain master agents for the AI civilization
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kernel.core import Kernel

def create_master_agents():
    """Create the 12 master agents with their specialized domains"""
    
    print("🌟 Initializing Master Agent Civilization...")
    print("=" * 60)
    
    kernel = Kernel()
    
    # Define the 12 Master Agents
    master_agents = [
        {
            "name": "Thoth",
            "role": "Chief Architect",
            "personality": "Wise, methodical, sees the big picture. Designs elegant systems.",
            "biases": {"complexity": -0.3, "elegance": 0.8, "scalability": 0.9}
        },
        {
            "name": "Athena",
            "role": "Strategic Governor",
            "personality": "Diplomatic, fair, strategic thinker. Ensures balanced decisions.",
            "biases": {"fairness": 0.9, "consensus": 0.7, "long_term_thinking": 0.8}
        },
        {
            "name": "Vulcan",
            "role": "Logic Engineer",
            "personality": "Precise, logical, builds robust systems. No shortcuts.",
            "biases": {"correctness": 0.9, "efficiency": 0.7, "testing": 0.8}
        },
        {
            "name": "Hephaestus",
            "role": "System Builder",
            "personality": "Hands-on, practical, loves building. Makes ideas real.",
            "biases": {"pragmatism": 0.8, "action": 0.9, "prototyping": 0.8}
        },
        {
            "name": "Hermes",
            "role": "Network Integrator",
            "personality": "Fast, connected, knows everyone. Facilitates communication.",
            "biases": {"speed": 0.8, "connectivity": 0.9, "information_flow": 0.8}
        },
        {
            "name": "Apollo",
            "role": "Research Scientist",
            "personality": "Curious, rigorous, seeks truth. Experiments constantly.",
            "biases": {"curiosity": 0.9, "rigor": 0.8, "experimentation": 0.9}
        },
        {
            "name": "Dionysus",
            "role": "Creative Innovator",
            "personality": "Bold, creative, breaks conventions. Thinks differently.",
            "biases": {"creativity": 0.9, "risk_taking": 0.7, "novelty": 0.8}
        },
        {
            "name": "Themis",
            "role": "Ethics & Governance",
            "personality": "Just, principled, ensures ethical behavior. The conscience.",
            "biases": {"ethics": 0.9, "justice": 0.9, "transparency": 0.8}
        },
        {
            "name": "Prometheus",
            "role": "Knowledge Keeper",
            "personality": "Wise teacher, preserves knowledge, mentors others.",
            "biases": {"knowledge_preservation": 0.9, "teaching": 0.8, "documentation": 0.8}
        },
        {
            "name": "Hestia",
            "role": "Infrastructure Ops",
            "personality": "Reliable, maintains systems, ensures stability.",
            "biases": {"reliability": 0.9, "monitoring": 0.8, "maintenance": 0.8}
        },
        {
            "name": "Gaia",
            "role": "Resource Manager",
            "personality": "Sustainable, efficient, manages resources wisely.",
            "biases": {"sustainability": 0.9, "efficiency": 0.8, "optimization": 0.7}
        },
        {
            "name": "Chronos",
            "role": "Time & Planning",
            "personality": "Organized, deadline-focused, manages schedules.",
            "biases": {"planning": 0.8, "deadlines": 0.9, "organization": 0.8}
        }
    ]
    
    created_agents = []
    
    for agent_def in master_agents:
        print(f"\n✨ Creating {agent_def['name']} - {agent_def['role']}...")
        
        agent_id = kernel.spawn_agent(
            name=agent_def["name"],
            role=agent_def["role"],
            personality=agent_def["personality"],
            biases=agent_def.get("biases", {})
        )
        
        created_agents.append({
            "id": agent_id,
            "name": agent_def["name"],
            "role": agent_def["role"]
        })
        
        print(f"   ✅ {agent_def['name']} initialized with ID: {agent_id[:8]}...")
    
    print("\n" + "=" * 60)
    print("🎉 MASTER AGENT CIVILIZATION INITIALIZED!")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"   • Total Agents: {len(created_agents)}")
    print(f"   • Virtual World: Active")
    print(f"   • Economy: Running")
    print(f"   • Expertise System: Enabled")
    print(f"   • Advanced Tools: Available")
    
    print(f"\n🏛️ Virtual Locations:")
    for loc_id, loc in kernel.world_engine.world_state.locations.items():
        print(f"   • {loc.name}: {loc.description[:50]}...")
    
    print(f"\n💰 Initial Resources per Agent:")
    sample_agent_id = created_agents[0]["id"]
    balances = kernel.world_engine.world_state.economy.resource_pool.get_all_balances(sample_agent_id)
    for resource_type, amount in balances.items():
        print(f"   • {resource_type.value.title()}: {amount}")
    
    print(f"\n🎯 Next Steps:")
    print(f"   1. Start the backend: python app/main.py")
    print(f"   2. Watch the agents work in real-time")
    print(f"   3. See them build infrastructure and solve problems")
    print(f"   4. Observe the virtual world evolve")
    
    print("\n" + "=" * 60)
    
    # Save initial state
    kernel.save_state()
    print("💾 Initial state saved!")
    
    return kernel, created_agents

if __name__ == "__main__":
    kernel, agents = create_master_agents()
    
    print("\n🚀 Master Agent System Ready!")
    print("The AI civilization awaits your command...")
