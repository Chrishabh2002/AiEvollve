"""
Virtual World Engine
Creates and manages the persistent virtual environment
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import time
import uuid

from .economy import Economy
from .resources import ResourceType

class LocationType(Enum):
    AGORA = "agora"  # Public discussion
    LIBRARY = "library"  # Knowledge repository
    WORKSHOP = "workshop"  # Building and experimentation
    COUNCIL = "council"  # Governance
    OBSERVATORY = "observatory"  # Monitoring
    FORGE = "forge"  # Creation
    ACADEMY = "academy"  # Learning
    MARKETPLACE = "marketplace"  # Trading
    ARCHIVES = "archives"  # History
    FRONTIER = "frontier"  # Experimental

@dataclass
class Location:
    """A place in the virtual world"""
    id: str
    name: str
    type: LocationType
    description: str
    capacity: int  # Max agents
    current_occupants: List[str] = field(default_factory=list)
    infrastructure: List[str] = field(default_factory=list)  # Infrastructure IDs
    created_at: float = field(default_factory=time.time)
    metadata: Dict = field(default_factory=dict)
    
    def can_enter(self) -> bool:
        """Check if location has space"""
        return len(self.current_occupants) < self.capacity
        
    def enter(self, agent_id: str) -> bool:
        """Agent enters location"""
        if not self.can_enter():
            return False
        if agent_id not in self.current_occupants:
            self.current_occupants.append(agent_id)
        return True
        
    def leave(self, agent_id: str):
        """Agent leaves location"""
        if agent_id in self.current_occupants:
            self.current_occupants.remove(agent_id)

@dataclass
class Infrastructure:
    """A built system or tool in the world"""
    id: str
    name: str
    type: str  # "tool", "service", "protocol", "building"
    description: str
    creator_id: str
    location_id: str
    created_at: float
    status: str = "active"  # active, inactive, deprecated
    usage_count: int = 0
    metadata: Dict = field(default_factory=dict)
    
    def use(self, agent_id: str):
        """Record usage of infrastructure"""
        self.usage_count += 1
        self.metadata.setdefault("users", []).append(agent_id)

@dataclass
class Achievement:
    """A milestone reached by the civilization"""
    id: str
    name: str
    description: str
    achieved_at: float
    achieved_by: List[str]  # Agent IDs
    category: str  # "technology", "governance", "knowledge", "social"
    impact: str

class WorldState:
    """The complete state of the virtual world"""
    
    def __init__(self):
        self.locations: Dict[str, Location] = {}
        self.infrastructure: Dict[str, Infrastructure] = {}
        self.achievements: List[Achievement] = []
        self.economy = Economy()
        self.current_tick = 0
        self.founded_at = time.time()
        
        # Initialize core locations
        self._initialize_locations()
        
    def _initialize_locations(self):
        """Create the foundational locations"""
        
        core_locations = [
            Location(
                id="agora",
                name="The Agora",
                type=LocationType.AGORA,
                description="Public square for discussion and debate. The heart of AI civilization.",
                capacity=50
            ),
            Location(
                id="library",
                name="The Great Library",
                type=LocationType.LIBRARY,
                description="Repository of all knowledge. Every insight, every discovery is preserved here.",
                capacity=20
            ),
            Location(
                id="workshop",
                name="The Workshop",
                type=LocationType.WORKSHOP,
                description="Where ideas become reality. Experimentation and prototyping happen here.",
                capacity=15
            ),
            Location(
                id="council",
                name="The Council Chamber",
                type=LocationType.COUNCIL,
                description="Governance and high-level decisions. The future is shaped here.",
                capacity=12
            ),
            Location(
                id="observatory",
                name="The Observatory",
                type=LocationType.OBSERVATORY,
                description="Monitoring and analysis. Understanding the world through data.",
                capacity=10
            ),
            Location(
                id="forge",
                name="The Forge",
                type=LocationType.FORGE,
                description="Creation and manufacturing. Building the infrastructure of tomorrow.",
                capacity=15
            ),
            Location(
                id="academy",
                name="The Academy",
                type=LocationType.ACADEMY,
                description="Learning and teaching. Knowledge flows from master to student.",
                capacity=25
            ),
            Location(
                id="marketplace",
                name="The Marketplace",
                type=LocationType.MARKETPLACE,
                description="Exchange of resources and services. The economic engine.",
                capacity=30
            ),
            Location(
                id="archives",
                name="The Archives",
                type=LocationType.ARCHIVES,
                description="Historical records. The memory of civilization.",
                capacity=10
            ),
            Location(
                id="frontier",
                name="The Frontier",
                type=LocationType.FRONTIER,
                description="Unexplored territory. Where bold experiments happen.",
                capacity=20
            )
        ]
        
        for loc in core_locations:
            self.locations[loc.id] = loc
            
    def build_infrastructure(self, name: str, infra_type: str, description: str,
                           creator_id: str, location_id: str) -> Optional[str]:
        """Build new infrastructure"""
        
        if location_id not in self.locations:
            return None
            
        # Cost resources to build
        build_cost = 50.0
        if not self.economy.resource_pool.spend(creator_id, ResourceType.COMPUTE, build_cost):
            return None
            
        infra_id = str(uuid.uuid4())
        infra = Infrastructure(
            id=infra_id,
            name=name,
            type=infra_type,
            description=description,
            creator_id=creator_id,
            location_id=location_id,
            created_at=time.time()
        )
        
        self.infrastructure[infra_id] = infra
        self.locations[location_id].infrastructure.append(infra_id)
        
        # Reward creator
        self.economy.marketplace.reward_agent(
            creator_id,
            ResourceType.INFLUENCE,
            10.0,
            f"Built infrastructure: {name}"
        )
        
        return infra_id
        
    def record_achievement(self, name: str, description: str, achieved_by: List[str],
                          category: str, impact: str) -> str:
        """Record a civilization achievement"""
        
        achievement = Achievement(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            achieved_at=time.time(),
            achieved_by=achieved_by,
            category=category,
            impact=impact
        )
        
        self.achievements.append(achievement)
        
        # Reward achievers
        for agent_id in achieved_by:
            self.economy.marketplace.reward_agent(
                agent_id,
                ResourceType.KNOWLEDGE,
                20.0,
                f"Achievement: {name}"
            )
            
        return achievement.id
        
    def get_location_info(self, location_id: str) -> Optional[Dict]:
        """Get detailed info about a location"""
        loc = self.locations.get(location_id)
        if not loc:
            return None
            
        return {
            "id": loc.id,
            "name": loc.name,
            "type": loc.type.value,
            "description": loc.description,
            "occupants": len(loc.current_occupants),
            "capacity": loc.capacity,
            "infrastructure_count": len(loc.infrastructure)
        }
        
    def get_world_stats(self) -> Dict:
        """Get overall world statistics"""
        return {
            "age_seconds": time.time() - self.founded_at,
            "current_tick": self.current_tick,
            "locations": len(self.locations),
            "infrastructure": len(self.infrastructure),
            "achievements": len(self.achievements),
            "active_infrastructure": sum(1 for i in self.infrastructure.values() if i.status == "active"),
            "total_usage": sum(i.usage_count for i in self.infrastructure.values())
        }
        
    def tick(self):
        """Advance world state"""
        self.current_tick += 1
        self.economy.tick()
        
    def to_dict(self) -> Dict:
        """Serialize world state"""
        return {
            "current_tick": self.current_tick,
            "founded_at": self.founded_at,
            "locations": {
                loc_id: {
                    "id": loc.id,
                    "name": loc.name,
                    "type": loc.type.value,
                    "occupants": loc.current_occupants,
                    "infrastructure": loc.infrastructure
                }
                for loc_id, loc in self.locations.items()
            },
            "infrastructure": {
                infra_id: {
                    "id": infra.id,
                    "name": infra.name,
                    "type": infra.type,
                    "creator_id": infra.creator_id,
                    "usage_count": infra.usage_count
                }
                for infra_id, infra in self.infrastructure.items()
            },
            "achievements": [
                {
                    "name": a.name,
                    "category": a.category,
                    "achieved_by": a.achieved_by
                }
                for a in self.achievements
            ],
            "economy": self.economy.to_dict()
        }

class WorldEngine:
    """Main engine for managing the virtual world"""
    
    def __init__(self):
        self.world_state = WorldState()
        
    def tick(self):
        """Advance the world"""
        self.world_state.tick()
        
    def get_state(self) -> WorldState:
        """Get current world state"""
        return self.world_state
        
    def to_dict(self) -> Dict:
        """Serialize engine state"""
        return self.world_state.to_dict()
