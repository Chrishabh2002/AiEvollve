import asyncio
from typing import Callable, Awaitable, List, Dict, Any
import json
import time

class EventBus:
    _instance = None
    
    def __init__(self):
        self.subscribers: List[Callable[[Dict[str, Any]], Awaitable[None]]] = []

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def subscribe(self, callback: Callable[[Dict[str, Any]], Awaitable[None]]):
        self.subscribers.append(callback)

    async def unsubscribe(self, callback: Callable[[Dict[str, Any]], Awaitable[None]]):
        if callback in self.subscribers:
            self.subscribers.remove(callback)

    async def publish(self, event_type: str, payload: Dict[str, Any]):
        event = {
            "type": event_type,
            "timestamp": time.time(),
            "payload": payload
        }
        # Run all callbacks
        # We use asyncio.gather to broadcast in parallel
        if self.subscribers:
            await asyncio.gather(*[cb(event) for cb in self.subscribers])

event_bus = EventBus.get_instance()
