"""
Resource Management System
Virtual resources that agents can use, trade, and manage
"""

from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum
import time

class ResourceType(Enum):
    COMPUTE = "compute"  # Processing power
    MEMORY = "memory"    # Storage capacity
    KNOWLEDGE = "knowledge"  # Expertise points
    INFLUENCE = "influence"  # Social capital
    TIME = "time"  # Scheduling priority

@dataclass
class Resource:
    """A unit of virtual resource"""
    type: ResourceType
    amount: float
    owner_id: str
    acquired_at: float
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class ResourcePool:
    """Manages resources for the entire world"""
    
    def __init__(self):
        self.agent_resources: Dict[str, Dict[ResourceType, float]] = {}
        self.total_supply: Dict[ResourceType, float] = {
            ResourceType.COMPUTE: 10000.0,
            ResourceType.MEMORY: 10000.0,
            ResourceType.KNOWLEDGE: 10000.0,
            ResourceType.INFLUENCE: 10000.0,
            ResourceType.TIME: 10000.0
        }
        self.allocated: Dict[ResourceType, float] = {rt: 0.0 for rt in ResourceType}
        
    def initialize_agent(self, agent_id: str):
        """Give starting resources to a new agent"""
        self.agent_resources[agent_id] = {
            ResourceType.COMPUTE: 100.0,
            ResourceType.MEMORY: 100.0,
            ResourceType.KNOWLEDGE: 50.0,
            ResourceType.INFLUENCE: 10.0,
            ResourceType.TIME: 100.0
        }
        
        for rt in ResourceType:
            self.allocated[rt] += self.agent_resources[agent_id][rt]
            
    def get_balance(self, agent_id: str, resource_type: ResourceType) -> float:
        """Get agent's balance of a resource"""
        if agent_id not in self.agent_resources:
            return 0.0
        return self.agent_resources[agent_id].get(resource_type, 0.0)
        
    def transfer(self, from_agent: str, to_agent: str, resource_type: ResourceType, amount: float) -> bool:
        """Transfer resources between agents"""
        if from_agent not in self.agent_resources or to_agent not in self.agent_resources:
            return False
            
        if self.agent_resources[from_agent].get(resource_type, 0.0) < amount:
            return False
            
        self.agent_resources[from_agent][resource_type] -= amount
        self.agent_resources[to_agent][resource_type] = self.agent_resources[to_agent].get(resource_type, 0.0) + amount
        
        return True
        
    def spend(self, agent_id: str, resource_type: ResourceType, amount: float) -> bool:
        """Spend resources (removed from circulation)"""
        if agent_id not in self.agent_resources:
            return False
            
        if self.agent_resources[agent_id].get(resource_type, 0.0) < amount:
            return False
            
        self.agent_resources[agent_id][resource_type] -= amount
        self.allocated[resource_type] -= amount
        
        return True
        
    def earn(self, agent_id: str, resource_type: ResourceType, amount: float):
        """Agent earns resources (created from actions)"""
        if agent_id not in self.agent_resources:
            self.initialize_agent(agent_id)
            
        self.agent_resources[agent_id][resource_type] = self.agent_resources[agent_id].get(resource_type, 0.0) + amount
        self.allocated[resource_type] += amount
        
    def get_all_balances(self, agent_id: str) -> Dict[ResourceType, float]:
        """Get all resource balances for an agent"""
        if agent_id not in self.agent_resources:
            return {rt: 0.0 for rt in ResourceType}
        return self.agent_resources[agent_id].copy()
        
    def to_dict(self) -> Dict:
        """Serialize to dictionary"""
        return {
            "agent_resources": {
                agent_id: {rt.value: amount for rt, amount in resources.items()}
                for agent_id, resources in self.agent_resources.items()
            },
            "total_supply": {rt.value: amount for rt, amount in self.total_supply.items()},
            "allocated": {rt.value: amount for rt, amount in self.allocated.items()}
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'ResourcePool':
        """Deserialize from dictionary"""
        pool = cls()
        
        pool.agent_resources = {
            agent_id: {ResourceType(rt): amount for rt, amount in resources.items()}
            for agent_id, resources in data.get("agent_resources", {}).items()
        }
        
        pool.total_supply = {ResourceType(rt): amount for rt, amount in data.get("total_supply", {}).items()}
        pool.allocated = {ResourceType(rt): amount for rt, amount in data.get("allocated", {}).items()}
        
        return pool
