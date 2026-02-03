"""
Virtual Economy System
Marketplace for resource trading and value exchange
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import time
import uuid

from .resources import ResourceType, ResourcePool

class TransactionType(Enum):
    TRADE = "trade"
    PAYMENT = "payment"
    REWARD = "reward"
    PENALTY = "penalty"

@dataclass
class Transaction:
    """A record of resource exchange"""
    id: str
    type: TransactionType
    from_agent: str
    to_agent: str
    resource_type: ResourceType
    amount: float
    timestamp: float
    reason: str = ""
    metadata: Dict = field(default_factory=dict)

class Marketplace:
    """Trading platform for resources"""
    
    def __init__(self, resource_pool: ResourcePool):
        self.resource_pool = resource_pool
        self.transactions: List[Transaction] = []
        self.prices: Dict[ResourceType, float] = {
            ResourceType.COMPUTE: 1.0,
            ResourceType.MEMORY: 1.0,
            ResourceType.KNOWLEDGE: 2.0,
            ResourceType.INFLUENCE: 5.0,
            ResourceType.TIME: 3.0
        }
        
    def trade(self, from_agent: str, to_agent: str, give_type: ResourceType, 
              give_amount: float, receive_type: ResourceType, receive_amount: float,
              reason: str = "") -> Optional[str]:
        """Execute a trade between two agents"""
        
        # Check if both agents have sufficient resources
        if self.resource_pool.get_balance(from_agent, give_type) < give_amount:
            return None
        if self.resource_pool.get_balance(to_agent, receive_type) < receive_amount:
            return None
            
        # Execute transfers
        success1 = self.resource_pool.transfer(from_agent, to_agent, give_type, give_amount)
        success2 = self.resource_pool.transfer(to_agent, from_agent, receive_type, receive_amount)
        
        if not (success1 and success2):
            # Rollback if either failed
            if success1:
                self.resource_pool.transfer(to_agent, from_agent, give_type, give_amount)
            if success2:
                self.resource_pool.transfer(from_agent, to_agent, receive_type, receive_amount)
            return None
            
        # Record transaction
        tx_id = str(uuid.uuid4())
        tx = Transaction(
            id=tx_id,
            type=TransactionType.TRADE,
            from_agent=from_agent,
            to_agent=to_agent,
            resource_type=give_type,
            amount=give_amount,
            timestamp=time.time(),
            reason=reason,
            metadata={"receive_type": receive_type.value, "receive_amount": receive_amount}
        )
        self.transactions.append(tx)
        
        return tx_id
        
    def reward_agent(self, agent_id: str, resource_type: ResourceType, amount: float, reason: str):
        """Reward an agent with resources"""
        self.resource_pool.earn(agent_id, resource_type, amount)
        
        tx = Transaction(
            id=str(uuid.uuid4()),
            type=TransactionType.REWARD,
            from_agent="SYSTEM",
            to_agent=agent_id,
            resource_type=resource_type,
            amount=amount,
            timestamp=time.time(),
            reason=reason
        )
        self.transactions.append(tx)
        
    def penalize_agent(self, agent_id: str, resource_type: ResourceType, amount: float, reason: str):
        """Penalize an agent by taking resources"""
        self.resource_pool.spend(agent_id, resource_type, amount)
        
        tx = Transaction(
            id=str(uuid.uuid4()),
            type=TransactionType.PENALTY,
            from_agent=agent_id,
            to_agent="SYSTEM",
            resource_type=resource_type,
            amount=amount,
            timestamp=time.time(),
            reason=reason
        )
        self.transactions.append(tx)
        
    def get_agent_transactions(self, agent_id: str, limit: int = 10) -> List[Transaction]:
        """Get recent transactions for an agent"""
        agent_txs = [tx for tx in self.transactions if tx.from_agent == agent_id or tx.to_agent == agent_id]
        return sorted(agent_txs, key=lambda x: x.timestamp, reverse=True)[:limit]
        
    def get_market_price(self, resource_type: ResourceType) -> float:
        """Get current market price of a resource"""
        return self.prices.get(resource_type, 1.0)
        
    def update_prices(self):
        """Update prices based on supply and demand (simplified)"""
        # In a real system, this would use more sophisticated economics
        for rt in ResourceType:
            allocated = self.resource_pool.allocated.get(rt, 0.0)
            total = self.resource_pool.total_supply.get(rt, 1.0)
            scarcity = allocated / total if total > 0 else 0.5
            
            # Price increases with scarcity
            self.prices[rt] = 1.0 + (scarcity * 2.0)

class Economy:
    """Overall economic system"""
    
    def __init__(self):
        self.resource_pool = ResourcePool()
        self.marketplace = Marketplace(self.resource_pool)
        
    def tick(self):
        """Update economy each tick"""
        self.marketplace.update_prices()
        
    def to_dict(self) -> Dict:
        """Serialize to dictionary"""
        return {
            "resource_pool": self.resource_pool.to_dict(),
            "prices": {rt.value: price for rt, price in self.marketplace.prices.items()},
            "transaction_count": len(self.marketplace.transactions)
        }
