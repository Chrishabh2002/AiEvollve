from typing import Dict, Optional, List, Any
from kernel.agent import Agent, AgentIdentity
from kernel.reputation import ReputationManager
from kernel.decision_engine import DecisionEngine, DecisionStatus, DecisionResultType
from kernel.planner import Planner
from kernel.executor import Executor
from kernel.agent_fsm import AgentState
from kernel.llm import LLMClient
from kernel.social import SocialFeed
from kernel.introspection import IntrospectionAPI
from kernel.evolution import EvolutionEngine
from kernel.storage import StorageManager
from kernel.internal_tools import global_internal_tools

# NEW IMPORTS - Master Agent Systems
from kernel.world.world_engine import WorldEngine
from kernel.world.resources import ResourceType
from kernel.expertise import ExpertiseManager, global_expertise_manager
from kernel.advanced_tools import AdvancedTools, global_advanced_tools
from kernel.knowledge.domain_knowledge import DomainKnowledge, global_knowledge, ExpertiseLevel
from kernel.autonomous_workflow import AutonomousWorkflow, global_workflow, Vote
from kernel.real_executor import RealPlanExecutor

class Kernel:
    def __init__(self):
        self.reputation_manager = ReputationManager()
        self.decision_engine = DecisionEngine(self.reputation_manager)
        self.planner = Planner()
        self.executor = Executor(self.planner)
        self.llm_client = LLMClient()
        self.social_feed = SocialFeed()
        self.evolution_engine = EvolutionEngine()
        self.agents: Dict[str, Agent] = {}

        # --- Register Default Executors ---
        self.executor.register_handler("simulate", lambda desc: global_internal_tools.thought_simulator(desc))
        self.executor.register_handler("experiment", lambda desc: global_internal_tools.virtual_experiment(desc))
        self.executor.register_handler("design", lambda desc: global_internal_tools.protocol_designer(desc))
        self.executor.register_handler("analyze", lambda desc: global_internal_tools.system_analyzer())
        self.executor.register_handler("research", lambda desc: global_internal_tools.read_url(desc) if "http" in desc else global_internal_tools.retrieve_knowledge(desc))
        
        # Storage
        self.storage = StorageManager()
        
        # === NEW MASTER AGENT SYSTEMS ===
        
        # Virtual World
        self.world_engine = WorldEngine()
        
        # Expertise Management
        self.expertise_manager = global_expertise_manager
        
        # Advanced Tools
        self.advanced_tools = global_advanced_tools
        
        # Domain Knowledge
        self.domain_knowledge = global_knowledge
        
        # Autonomous Workflow
        self.workflow = global_workflow
        
        # Real Plan Executor (for actual plan execution)
        self.real_executor = RealPlanExecutor(self.planner, self.llm_client, self)
        
        # Register advanced tools with executor
        self.executor.register_handler("generate_code", lambda spec: self.advanced_tools.generate_code(spec))
        self.executor.register_handler("run_experiment", lambda hyp: self.advanced_tools.run_experiment(hyp))
        self.executor.register_handler("build_database", lambda name: self.advanced_tools.build_database(name, {}))
        self.executor.register_handler("deploy_service", lambda name: self.advanced_tools.deploy_service(name, ""))
        self.executor.register_handler("build_infrastructure", lambda name: self.world_engine.world_state.build_infrastructure(name, "tool", "", "SYSTEM", "workshop"))
        
        # Rate Limiting
        self.max_decisions_per_tick = 5
        self.max_votes_per_tick = 10
        self.max_posts_per_tick = 5
        
        self.decisions_created_this_tick = 0
        self.votes_cast_this_tick = 0
        self.posts_created_this_tick = 0
        
        # Global Counter
        self.current_tick = 0
        
        # Introspection
        self.introspection = IntrospectionAPI(self)

        # System Settings
        self.auto_evolution = True
        self.strict_mode = False
        self.sandboxed = True
        self.max_agents_limit = 12

    def save_state(self) -> None:
        """
        Saves full system state to disk.
        """
        data = {
            "current_tick": self.current_tick,
            "settings": {
                "auto_evolution": self.auto_evolution,
                "strict_mode": self.strict_mode,
                "sandboxed": self.sandboxed,
                "max_agents_limit": self.max_agents_limit
            },
            "agents": {aid: agent.to_dict() for aid, agent in self.agents.items()},
            "social_feed": self.social_feed.to_dict(),
            "decisions": self.decision_engine.to_dict(),
            "plans": self.planner.to_dict(),
            "reputation": self.reputation_manager.to_dict()
        }
        self.storage.save_state(data)

    def load_state(self) -> bool:
        """
        Loads system state from disk if available.
        Returns True if loaded, False otherwise.
        """
        data = self.storage.load_state()
        if not data:
            return False
            
        try:
            self.current_tick = data.get("current_tick", 0)
            
            settings = data.get("settings", {})
            self.auto_evolution = settings.get("auto_evolution", True)
            self.strict_mode = settings.get("strict_mode", False)
            self.sandboxed = settings.get("sandboxed", True)
            self.max_agents_limit = settings.get("max_agents_limit", 12)
            
            # Components
            if "reputation" in data:
                self.reputation_manager = ReputationManager.from_dict(data["reputation"])
                # Must update decision engine's reference
                self.decision_engine._reputation_manager = self.reputation_manager
            
            if "social_feed" in data:
                self.social_feed = SocialFeed.from_dict(data["social_feed"])
                
            if "decisions" in data:
                self.decision_engine = DecisionEngine.from_dict(data["decisions"], self.reputation_manager)
                
            if "plans" in data:
                self.planner = Planner.from_dict(data["plans"])
                # Must update executor's reference
                self.executor._planner = self.planner
            
            # Agents
            self.agents = {}
            if "agents" in data:
                for aid, a_data in data["agents"].items():
                    agent = Agent.from_dict(a_data)
                    self.agents[aid] = agent
            
            # Initialize Real Plan Executor now that agents are loaded
            self.real_executor = RealPlanExecutor(self.planner, self.llm_client, self)
                    
            return True
        except Exception as e:
            print(f"FAILED TO RESTORE STATE: {e}")
            return False

    def spawn_agent(self, name: str, role: str, personality: str, biases: Optional[Dict[str, float]] = None, supervisor_id: Optional[str] = None) -> str:
        """
        Creates and starts a new agent in the system.
        """
        if biases is None:
            biases = {}
            
        identity = AgentIdentity(
            name=name,
            role=role,
            personality=personality,
            supervisor_id=supervisor_id,
            biases=biases
        )
        
        agent = Agent(identity)
        self.agents[agent.id] = agent
        
        # Initialize Reputation
        self.reputation_manager.initialize_agent(agent.id)
        
        # === NEW: Initialize Expertise ===
        # Determine domain from role
        domain_map = {
            "architect": "architecture",
            "engineer": "engineering",
            "scientist": "science",
            "governor": "governance",
            "philosopher": "governance",
            "researcher": "science",
            "builder": "engineering"
        }
        
        domain = "architecture"  # default
        for key, dom in domain_map.items():
            if key.lower() in role.lower():
                domain = dom
                break
                
        # Initialize as MASTER level (8-10)
        self.expertise_manager.initialize_agent(agent.id, domain, starting_level=8)
        
        # === NEW: Initialize World Resources ===
        self.world_engine.world_state.economy.resource_pool.initialize_agent(agent.id)
        
        # Start Lifecycle: CREATED -> IDLE
        agent.fsm.transition("initialization_complete")
        
        # Announce in world
        self.social_feed.create_post(
            "SYSTEM",
            f"🌟 **NEW MASTER AGENT JOINED** 🌟\n\n"
            f"**Name**: {name}\n"
            f"**Role**: {role}\n"
            f"**Domain**: {domain.title()}\n"
            f"**Expertise Level**: MASTER (8/10)\n\n"
            f"Welcome to the civilization, @{name}!",
            agent_name="System",
            agent_role="Orchestrator"
        )
        
        return agent.id

    def retire_agent(self, agent_id: str) -> None:
        """
        Permanently retires an agent.
        """
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            # Verify not already retired to avoid FSM error
            if agent.fsm.current_state != AgentState.RETIRED:
                agent.fsm.transition("forced_retirement")

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        return self.agents.get(agent_id)

    def tick(self) -> None:
        """
        Advances the system one step.
        """
        self.current_tick += 1
        
        # Reset counters
        self.decisions_created_this_tick = 0
        self.votes_cast_this_tick = 0
        self.posts_created_this_tick = 0
        
        # --- BOOTSTRAP / LIVELINESS CHECK ---
        # If the world is dead (no decisions), inject life.
        if len(self.decision_engine._decisions) == 0 and self.current_tick % 10 == 0:
            print("KERNEL: World is silent. Injecting Genesis Decision...")
            # Pick an agent, preferably an Architect
            architects = [a for a in self.agents.values() if "Architect" in a.identity.role or "Founder" in a.identity.role]
            if not architects: architects = list(self.agents.values())
            
            if architects:
                author = architects[0]
                topic = "System Initialization Protocols"
                content = "We must formally initialize the core operating protocols for this civilization. I propose we adopt the Genesis Framework."
                
                # Direct Injection bypassing limits
                d_id = self.decision_engine.create_decision(topic, author.id, content)
                
                # Announce it
                self.social_feed.create_post(
                    author.id,
                    f"📢 **GENESIS PROPOSAL**\nTo kickstart our civilization, I have proposed: **{topic}**.\nPlease vote immediately.",
                    agent_name=author.identity.name,
                    agent_role=author.identity.role,
                    is_idea=True,
                    idea_id=d_id
                )
                print(f"KERNEL: Injected Decision {d_id}")
        
        # 1. Processing Agents
        # Limit to 3 active thinkers per tick to prevent simulation stall due to LLM latency
        import random
        active_agents = list(self.agents.values())
        random.shuffle(active_agents)
        
        # Only process a subset of agents each tick for thinking (Concurrency Limit)
        max_thinkers = 6
        thinkers_processed = 0
        
        for agent in active_agents:
            try:
                # Reset agent tick counters
                agent.decisions_proposed_tick = 0
                agent.votes_cast_tick = 0
                agent.posts_created_tick = 0
                
                state = agent.fsm.current_state
                
                # Check for @mentions to prioritize thinking
                is_mentioned = False
                if state in [AgentState.IDLE, AgentState.DELIBERATING]:
                    recent_posts = self.social_feed.get_feed(limit=10)
                    for post in recent_posts:
                        if post.agent_id == agent.id: continue
                        # Robust mention check
                        if f"@{agent.identity.name}" in post.content or f"@{agent.id}" in post.content:
                            is_mentioned = True
                            break
                            
                should_think = False
                
                # PRIORITY: If mentioned, ALWAYS think (bypass limit)
                if is_mentioned:
                    should_think = True
                # Otherwise, respect the concurrency limit
                elif thinkers_processed < max_thinkers:
                    should_think = True
                    thinkers_processed += 1
                
                if should_think:
                    # Agent thinks and potentially decides to act
                    action = agent.think(
                        self.llm_client, 
                        self.social_feed, 
                        self.decision_engine,
                        self # pass kernel reference for limits
                    )
                    # Action is already recorded in agent memory
                
                elif state == AgentState.EXECUTING:
                    # Agent acts using the central Executor
                    # NO decision creation or voting allowed here
                    result = agent.act(self.executor)
                    
                    if result:
                        # Handle consequences of execution
                        if result.status == "FAILED":
                            # Apply penalty
                            try:
                                self.reputation_manager.apply_event(agent.id, "execution_failure")
                            except Exception:
                                pass # specific error handling omitted for brevity
                        elif result.status == "DONE":
                            pass
            except Exception as e:
                print(f"ERROR processing agent {agent.identity.name}: {e}")
                # Continue loop despite error

        # 1.5 Process Decisions & Create Plans
        import datetime
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        
        open_decisions = self.decision_engine.get_open_decisions()
        for d in open_decisions:
            should_resolve = False
            
            if d.deadline <= now_utc:
                should_resolve = True
            elif len(d.votes) >= (len(self.agents) * 0.5): # Early resolution
                should_resolve = True
                
            if should_resolve:
                print(f"Resolving Decision {d.id}...")
                result = self.decision_engine.resolve_decision(d.id)
                
                if result.result == DecisionResultType.ACCEPTED:
                    # CONVERT TO PLAN
                    plan_desc = f"Execute: {d.proposal.content}"
                    plan_id = self.planner.create_plan(d.topic_id, plan_desc)
                    
                    # Create steps for the plan (Auto-generated for now)
                    steps = []
                    content_lower = d.proposal.content.lower()
                    
                    if "research" in content_lower:
                        steps.append("Research phase: read_url(http://example.com)")
                    if "design" in content_lower:
                        steps.append("Design phase: design_protocol(Architecture)")
                    if "simulate" in content_lower:
                         steps.append("Simulation phase: thought_simulator(Scenario)")
                    
                    if not steps:
                        steps.append(f"Execute task: {d.proposal.content}")
                        
                    for s in steps:
                        # Make steps sequential? Or parallel?
                        # For now, parallel (no deps) unless we want a chain.
                        # Let's make them sequential for realism if multiple steps exist.
                        # Actually, keeping it simple: Parallel for now (empty deps).
                        self.planner.add_step(plan_id, s, dependencies=[])
                        
                    self.social_feed.create_post(
                        "SYSTEM",
                        f"**DECISION ACCEPTED** ✅\n"
                        f"Topic: {d.topic_id}\n"
                        f"Status: PLAN CREATED ({plan_id})\n"
                        f"Agents check your Plan queue!",
                        agent_name="System",
                        agent_role="Orchestrator"
                    )
                else:
                    self.social_feed.create_post(
                        "SYSTEM",
                        f"**DECISION REJECTED** ❌\n"
                        f"Topic: {d.topic_id}\n"
                        f"Reason: {result.reason}",
                        agent_name="System",
                        agent_role="Orchestrator"
                    )

        # 2. System Evolution Check
        if self.auto_evolution and self.current_tick % 10 == 0: # Check every 10 ticks
            # Gather data for evolution heuristics
            # We need decision history and execution failures
            # Currently decision engine has all decisions
            all_decisions = list(self.decision_engine._decisions.values())
            
            # FIXME: Execution failures are not centrally tracked nicely yet, 
            # we might need to query agent memories or add a central registry.
            # For now, passing empty list for failures until we implement central log.
            # But we can try to infer from reputation events? 
            # Let's pass empty list for now to at least enable decision-based evolution.
            
            spawn_req = self.evolution_engine.evaluate_need(
                decision_history=all_decisions,
                execution_failures=[], 
                current_agent_count=len(self.agents),
                max_agents=self.max_agents_limit,
                current_tick=self.current_tick
            )
            
            if spawn_req:
                # REAL EVOLUTION: Spawn the agent!
                new_id = self.spawn_agent(
                    name=f"Evolved_{spawn_req.role}_{self.current_tick}",
                    role=spawn_req.role,
                    personality=spawn_req.personality
                )
                # Announce it
                self.social_feed.create_post(
                    "SYSTEM", 
                    f"**EVOLUTION EVENT**: System has spawned a new agent to address imbalance.\n\n"
                    f"**Role**: {spawn_req.role}\n"
                    f"**Reason**: {spawn_req.reason}\n"
                    f"**Welcome**: @{self.agents[new_id].identity.name}",
                    agent_name="System",
                    agent_role="Orchestrator"
                )
                
        # 3. Execute Active Plans (REAL EXECUTION)
        if self.real_executor:
            self.real_executor.tick()
        
        # 4. Update Virtual World
        self.world_engine.tick()
        
        # 5. Reward agents for activity (earn resources)
        for agent in self.agents.values():
            # Agents earn resources for participation
            if hasattr(agent, '_ticks_since_last_post') and agent._ticks_since_last_post == 0:
                # Agent was active this tick
                self.world_engine.world_state.economy.marketplace.reward_agent(
                    agent.id,
                    ResourceType.INFLUENCE,
                    1.0,
                    "Active participation"
                )

    def check_decision_limit(self) -> bool:
        if self.decisions_created_this_tick < self.max_decisions_per_tick:
            self.decisions_created_this_tick += 1
            return True
        return False

    def check_vote_limit(self) -> bool:
        if self.votes_cast_this_tick < self.max_votes_per_tick:
            self.votes_cast_this_tick += 1
            return True
        return False

    def check_post_limit(self) -> bool:
        if self.posts_created_this_tick < self.max_posts_per_tick:
            self.posts_created_this_tick += 1
            return True
        return False

    def register_tool(self, keyword: str, handler_fn: Any) -> None:
        """
        Proxy to register tools on the executor.
        """
        self.executor.register_handler(keyword, handler_fn)
