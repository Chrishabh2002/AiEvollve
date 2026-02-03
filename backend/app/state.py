import sys
import os
from typing import Optional

# Ensure project root is in path to import kernel
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from kernel.core import Kernel

class WorldState:
    _instance = None
    
    def __init__(self):
        self.kernel: Optional[Kernel] = None
        self.is_running: bool = False
        self.simulation_task = None
        self.tick_rate: float = 1.2

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def initialize_kernel(self):
        if not self.kernel:
            self.kernel = Kernel()
            
            # Attempt to load persistent state
            loaded = self.kernel.load_state()
            
            if loaded:
                print(f"KERNEL: Successfully restored state. Agents: {len(self.kernel.agents)}")
            
            # Only spawn masters if NO agents exist (fresh start)
            if not self.kernel.agents:
                print("KERNEL: No agents found. Spawning High Council.")
                # Initial Population: The High Council of 10 Master Agents
                # These are "Human-like" intelligent agents with specific domains.
                masters = [
                    ("Thoth", "Chief Architect", "Visionary, logical, ancient wisdom. Focus on structure and long-term goals."),
                    ("Athena", "Strategic Governor", "Fair, decisive, protective. Focus on consensus, rules, and ethics."),
                    ("Vulcan", "Logic Engineer", "Pragmatic, builder, toolsmith. Focus on implementation and infrastructure."),
                    ("Mercury", "Network Router", "Fast, connecting nodes, distributing information. Focus on communication."),
                    ("Apollo", "Creative Director", "Generative, innovative, artistic. Focus on novelty and new ideas."),
                    ("Hephaestus", "System Builder", "Indefatigable, detail-oriented. Focus on robustness and error handling."),
                    ("Gaia", "Resource Manager", "Nuturing, balancing. Focus on memory optimization and efficiency."),
                    ("Janus", "Protocol Designer", "Dual-natured, looks past and future. Focus on transitions and evolution."),
                    ("Prometheus", "Knowledge Keeper", "Curious, daring. Focus on acquiring and storing new patterns."),
                    ("Chronos", "Timeline Overseer", "Patient, metric-driven. Focus on planning horizons and deadlines."),
                    # Plus the user requested "including these 2" (Alpha/Beta equivalents) but renamed to humans
                    ("Dr. Aris", "Lead Researcher", "Scientific, analytical. Focus on empirical truth."),
                    ("Elena Core", "User Liaison", "Empathetic, translator. Focus on aligning system with user intent.")
                ]
                
                for name, role, personality in masters:
                    self.kernel.spawn_agent(name, role, personality)

    def get_kernel(self) -> Kernel:
        if not self.kernel:
            raise RuntimeError("Kernel not initialized")
        return self.kernel

global_state = WorldState.get_instance()
