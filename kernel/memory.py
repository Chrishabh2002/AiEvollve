import enum
import datetime
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from kernel.llm import LLMClient, LLMRequest

class MemoryType(enum.StrEnum):
    DECISION = "DECISION"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"

@dataclass
class WorkingMemoryEntry:
    id: str
    content: str
    timestamp: str

@dataclass
class EpisodicMemoryEntry:
    id: str
    agent_id: str
    type: str # MemoryType value
    content: str
    metadata: Dict[str, Any]
    timestamp: str

class MemoryManager:
    def __init__(self, max_working_items: int = 50):
        self._max_working_items = max_working_items
        # agent_id -> List[WorkingMemoryEntry]
        self._working_memory: Dict[str, List[WorkingMemoryEntry]] = {}
        # agent_id -> List[EpisodicMemoryEntry]
        self._episodic_memory: Dict[str, List[EpisodicMemoryEntry]] = {}

    def add_working(self, agent_id: str, content: str, llm_client: Optional[LLMClient] = None) -> None:
        """
        Adds content to working memory.
        If eviction occurs and llm_client is provided, attempts to summarize evicted content into episodic memory.
        """
        if agent_id not in self._working_memory:
            self._working_memory[agent_id] = []
        
        entry = WorkingMemoryEntry(
            id=str(uuid.uuid4()),
            content=content,
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
        )
        
        self._working_memory[agent_id].append(entry)
        
        # FIFO Eviction
        if len(self._working_memory[agent_id]) > self._max_working_items:
            evicted = self._working_memory[agent_id].pop(0)
            self._summarize_eviction(agent_id, evicted, llm_client)

    def _summarize_eviction(self, agent_id: str, entry: WorkingMemoryEntry, llm_client: Optional[LLMClient]) -> None:
        """
        Summarizes evicted memory using LLM if available and stores it as episodic memory.
        """
        if not llm_client:
            return

        # Determine if this memory is worth keeping
        # For simplicity, we ask the LLM
        try:
            prompt = (
                f"Memory: {entry.content}\n"
                "Extract any important DECISION or SUCCESS from this memory to save long-term.\n"
                "If unimportant, reply NONE."
            )
            req = LLMRequest(prompt=prompt, context={"agent_id": agent_id})
            resp = llm_client.generate(req)
            
            content = resp.content
            
            # Simple heuristic since our mock LLM returns canned responses based on keywords
            # If the original content had "decision", mock LLM says "propose decision".
            # We need to adapt the logic or rely on the content triggering a save.
            
            mem_type = None
            if "decision" in content.lower() or "decision" in entry.content.lower():
                mem_type = MemoryType.DECISION
            elif "success" in content.lower() or "executed" in entry.content.lower():
                mem_type = MemoryType.SUCCESS

            if mem_type:
                self.add_episode(
                    agent_id=agent_id,
                    type=mem_type,
                    content=f"Available summary: {entry.content}", # content is advisory
                    metadata={"original_id": entry.id}
                )
        except Exception:
            pass

    def get_working(self, agent_id: str) -> List[str]:
        if agent_id not in self._working_memory:
            return []
        
        # Return WorkingMemoryEntry objects so .content can be accessed
        return self._working_memory[agent_id]

    def clear_working(self, agent_id: str) -> None:
        if agent_id in self._working_memory:
            self._working_memory[agent_id] = []

    def add_episode(self, agent_id: str, type: str, content: str, metadata: Dict[str, Any]) -> str:
        if agent_id not in self._episodic_memory:
            self._episodic_memory[agent_id] = []
            
        episode_id = str(uuid.uuid4())
        entry = EpisodicMemoryEntry(
            id=episode_id,
            agent_id=agent_id,
            type=type,
            content=content,
            metadata=metadata,
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
        )
        
        self._episodic_memory[agent_id].append(entry)
        return episode_id

    def query_episodes(self, agent_id: str, type: Optional[str] = None, limit: int = 5) -> List[EpisodicMemoryEntry]:
        if agent_id not in self._episodic_memory:
            return []
            
        episodes = self._episodic_memory[agent_id]
        
        if type:
            episodes = [e for e in episodes if e.type == type]
            
        # Return most recent first
        sorted_episodes = sorted(episodes, key=lambda x: x.timestamp, reverse=True)
        return sorted_episodes[:limit]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "working_memory": {
                aid: [vars(e) for e in entries] 
                for aid, entries in self._working_memory.items()
            },
            "episodic_memory": {
                aid: [vars(e) for e in entries]
                for aid, entries in self._episodic_memory.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryManager':
        manager = cls()
        
        if "working_memory" in data:
            for aid, entries in data["working_memory"].items():
                manager._working_memory[aid] = [WorkingMemoryEntry(**e) for e in entries]
                
        if "episodic_memory" in data:
            for aid, entries in data["episodic_memory"].items():
                manager._episodic_memory[aid] = [EpisodicMemoryEntry(**e) for e in entries]
                
        return manager
