import asyncio
from backend.app.state import global_state
from backend.app.events import event_bus
import logging

logger = logging.getLogger("uvicorn")

async def run_simulation_loop():
    """
    Background task to tick the kernel and emit events.
    """
    logger.info("Simulation loop started.")
    
    while True:
        if global_state.is_running:
            try:
                kernel = global_state.get_kernel()
                
                # Snapshot counts before tick
                prev_decision_count = len(kernel.decision_engine._decisions)
                prev_plan_count = len(kernel.planner._plans)
                # social feed check moved to ID tracking

                # EXECUTE TICK (Offload sync work to thread)
                await asyncio.to_thread(kernel.tick)
                
                # 1. Emit Agent Thoughts (Check for new posts via Enhanced Feed)
                # We use get_feed (which calls get_timeline) to see recent activity
                recent_posts = kernel.social_feed.get_feed(limit=10)
                
                # We need a way to track what we've already emitted. 
                # Since this function is async and persistent, we can use a local 'seen' set.
                # However, Python's loop scope... we should init 'seen_ids' outside loop.
                # But we can't edit outside loop easily with chunk replacer.
                # Let's use a static-like variable attached to the function or global state?
                # Simplest: use global_state._seen_posts if meaningful, or just use a time-based filter?
                # Time-based is safer.
                # Let's use the timestamp of the last processed post.
                
                if not hasattr(run_simulation_loop, "last_post_time"):
                     run_simulation_loop.last_post_time = 0
                
                new_max_time = run_simulation_loop.last_post_time
                
                for post in reversed(recent_posts): # Oldest first to preserve order
                    if post.timestamp > run_simulation_loop.last_post_time:
                       await event_bus.publish("AGENT_MESSAGE", {
                           "agent": post.agent_id,
                           "content": post.content,
                           "id": post.id
                       })
                       if post.timestamp > new_max_time:
                           new_max_time = post.timestamp
                           
                run_simulation_loop.last_post_time = new_max_time


                # 2. Emit New Decisions
                # _decisions is a dict, so we convert to list and sort by creation time to find new ones
                all_decisions = sorted(kernel.decision_engine._decisions.values(), key=lambda d: d.created_at)
                curr_decision_count = len(all_decisions)
                
                if curr_decision_count > prev_decision_count:
                    new_decisions = all_decisions[prev_decision_count:]
                    for d in new_decisions:
                        await event_bus.publish("DECISION_CREATED", {
                            "id": d.id,
                            "topic": d.topic_id,
                            "author": d.author_id
                        })
                
                # 3. Emit New Plans
                # _plans is likely a dict too.
                curr_plan_count = len(kernel.planner._plans)
                if curr_plan_count > prev_plan_count:
                     await event_bus.publish("PLAN_UPDATE", {"count": curr_plan_count})

                # 4. Emit Tick Pulse
                await event_bus.publish("TICK", {"tick": kernel.current_tick})

                # 5. Periodic Save (every 10 ticks)
                if kernel.current_tick % 10 == 0:
                     await asyncio.to_thread(kernel.save_state)

            except Exception as e:
                logger.error(f"Error in simulation loop: {e}")
        
        # Wait for next tick (dynamic tick rate support)
        sleep_time = 1.0 / max(0.1, global_state.tick_rate)
        await asyncio.sleep(sleep_time)
