"""
Virtual World Engine
Creates a persistent virtual environment for AI agents to inhabit
"""

from .world_engine import WorldEngine, Location, Infrastructure, WorldState
from .resources import ResourcePool, Resource, ResourceType
from .economy import Economy, Transaction, Marketplace

__all__ = [
    'WorldEngine', 'Location', 'Infrastructure', 'WorldState',
    'ResourcePool', 'Resource', 'ResourceType',
    'Economy', 'Transaction', 'Marketplace'
]
