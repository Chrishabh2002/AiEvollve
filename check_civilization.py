"""
Quick Status Check
View the current state of the AI civilization
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kernel.core import Kernel
from kernel.world.resources import ResourceType

def check_status():
    """Check and display current civilization status"""
    
    print("\n🌍 AI CIVILIZATION STATUS")
    print("=" * 60)
    
    kernel = Kernel()
    
    # Try to load existing state
    loaded = kernel.load_state()
    
    if not loaded:
        print("⚠️  No saved state found. Run initialize_masters.py first!")
        return
    
    print(f"\n✅ State loaded successfully!")
    print(f"📊 Current Tick: {kernel.current_tick}")
    print(f"👥 Total Agents: {len(kernel.agents)}")
    
    print(f"\n🎭 MASTER AGENTS:")
    print("-" * 60)
    for agent in kernel.agents.values():
        expertise = kernel.expertise_manager.get_expertise(agent.id)
        resources = kernel.world_engine.world_state.economy.resource_pool.get_all_balances(agent.id)
        
        print(f"\n  {agent.identity.name} - {agent.identity.role}")
        print(f"    Domain: {expertise.domain if expertise else 'Unknown'}")
        print(f"    Level: {expertise.level if expertise else 0}/10")
        print(f"    Influence: {resources.get(ResourceType.INFLUENCE, 0)}")
        print(f"    State: {agent.fsm.current_state}")
    
    print(f"\n🏛️  VIRTUAL WORLD:")
    print("-" * 60)
    world_stats = kernel.world_engine.world_state.get_world_stats()
    print(f"  Locations: {world_stats['locations']}")
    print(f"  Infrastructure: {world_stats['infrastructure']}")
    print(f"  Achievements: {world_stats['achievements']}")
    print(f"  Active Infrastructure: {world_stats['active_infrastructure']}")
    
    print(f"\n💬 RECENT ACTIVITY:")
    print("-" * 60)
    feed = kernel.social_feed.get_feed(limit=5)
    for post in feed:
        agent_name = "SYSTEM"
        if post.agent_id in kernel.agents:
            agent_name = kernel.agents[post.agent_id].identity.name
        
        content_preview = post.content[:80] + "..." if len(post.content) > 80 else post.content
        print(f"  [{agent_name}]: {content_preview}")
    
    print(f"\n🎯 SYSTEM HEALTH:")
    print("-" * 60)
    print(f"  Auto Evolution: {'✅ Enabled' if kernel.auto_evolution else '❌ Disabled'}")
    print(f"  Max Agents: {kernel.max_agents_limit}")
    print(f"  Sandboxed: {'✅ Yes' if kernel.sandboxed else '❌ No'}")
    
    print("\n" + "=" * 60)
    print("🚀 System is ready! Start the backend to activate agents.")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    check_status()
