"""
Expertise System
Tracks and manages agent expertise and skill progression
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import time

class SkillLevel(Enum):
    NOVICE = 1
    INTERMEDIATE = 3
    ADVANCED = 5
    EXPERT = 7
    MASTER = 10

@dataclass
class Skill:
    """A specific skill an agent can develop"""
    name: str
    level: int  # 1-10
    experience: float  # Total XP earned
    last_used: float
    specializations: Dict[str, float] = field(default_factory=dict)
    
    def gain_xp(self, amount: float):
        """Gain experience in this skill"""
        self.experience += amount
        self.last_used = time.time()
        
        # Level up based on experience
        # Exponential curve: level 1->2 needs 100 XP, 2->3 needs 200 XP, etc.
        required_xp = sum(i * 100 for i in range(1, self.level + 1))
        if self.experience >= required_xp and self.level < 10:
            self.level += 1
            return True
        return False

@dataclass
class Ability:
    """Special ability unlocked at skill milestones"""
    name: str
    description: str
    skill_required: str
    level_required: int
    unlocked: bool = False

@dataclass
class ExpertiseProfile:
    """Complete expertise profile for an agent"""
    domain: str  # Primary domain
    level: int  # Overall expertise level 1-10
    skills: Dict[str, Skill] = field(default_factory=dict)
    abilities: List[Ability] = field(default_factory=list)
    proven_successes: int = 0
    teaching_ability: float = 0.0
    specializations: Dict[str, float] = field(default_factory=dict)
    
    def add_skill(self, skill_name: str):
        """Add a new skill"""
        if skill_name not in self.skills:
            self.skills[skill_name] = Skill(
                name=skill_name,
                level=1,
                experience=0.0,
                last_used=time.time()
            )
            
    def gain_skill_xp(self, skill_name: str, amount: float) -> bool:
        """Gain XP in a skill, returns True if leveled up"""
        if skill_name not in self.skills:
            self.add_skill(skill_name)
            
        leveled_up = self.skills[skill_name].gain_xp(amount)
        
        # Update overall expertise level
        if leveled_up:
            avg_level = sum(s.level for s in self.skills.values()) / len(self.skills)
            self.level = min(10, int(avg_level))
            
        return leveled_up
        
    def record_success(self):
        """Record a successful application of expertise"""
        self.proven_successes += 1
        
        # Improve teaching ability with experience
        self.teaching_ability = min(1.0, self.proven_successes / 100.0)
        
    def get_skill_level(self, skill_name: str) -> int:
        """Get level of a specific skill"""
        return self.skills.get(skill_name, Skill(skill_name, 1, 0.0, time.time())).level
        
    def can_teach(self, skill_name: str) -> bool:
        """Check if agent can teach a skill"""
        return self.get_skill_level(skill_name) >= 5 and self.teaching_ability >= 0.3

class SkillTree:
    """Manages skill progression paths"""
    
    def __init__(self):
        self.skill_paths: Dict[str, List[str]] = {
            "architecture": [
                "system_design",
                "distributed_systems",
                "microservices",
                "scalability",
                "resilience"
            ],
            "engineering": [
                "algorithms",
                "data_structures",
                "optimization",
                "physics_simulation",
                "mathematics"
            ],
            "governance": [
                "decision_theory",
                "policy_design",
                "conflict_resolution",
                "ethics",
                "game_theory"
            ],
            "science": [
                "experimental_design",
                "statistical_analysis",
                "hypothesis_testing",
                "research_methods",
                "peer_review"
            ]
        }
        
        self.abilities: Dict[str, List[Ability]] = {
            "architecture": [
                Ability("System Architect", "Design complex distributed systems", "system_design", 5),
                Ability("Pattern Master", "Identify and apply design patterns", "system_design", 7),
                Ability("Grand Architect", "Architect entire civilizations", "system_design", 10)
            ],
            "engineering": [
                Ability("Algorithm Expert", "Design optimal algorithms", "algorithms", 5),
                Ability("Performance Wizard", "Optimize any system", "optimization", 7),
                Ability("Engineering Master", "Solve any technical problem", "algorithms", 10)
            ],
            "governance": [
                Ability("Policy Maker", "Design effective policies", "policy_design", 5),
                Ability("Conflict Resolver", "Resolve any dispute", "conflict_resolution", 7),
                Ability("Governance Master", "Lead civilizations", "decision_theory", 10)
            ],
            "science": [
                Ability("Researcher", "Conduct rigorous experiments", "experimental_design", 5),
                Ability("Scientist", "Discover new knowledge", "research_methods", 7),
                Ability("Scientific Master", "Pioneer new fields", "hypothesis_testing", 10)
            ]
        }
        
    def get_skills_for_domain(self, domain: str) -> List[str]:
        """Get all skills in a domain"""
        return self.skill_paths.get(domain, [])
        
    def get_abilities_for_domain(self, domain: str) -> List[Ability]:
        """Get all abilities in a domain"""
        return self.abilities.get(domain, [])
        
    def check_ability_unlock(self, expertise: ExpertiseProfile) -> List[Ability]:
        """Check if any abilities should be unlocked"""
        unlocked = []
        
        for ability_list in self.abilities.values():
            for ability in ability_list:
                if not ability.unlocked:
                    skill_level = expertise.get_skill_level(ability.skill_required)
                    if skill_level >= ability.level_required:
                        ability.unlocked = True
                        unlocked.append(ability)
                        
        return unlocked

class ExpertiseManager:
    """Manages expertise for all agents"""
    
    def __init__(self):
        self.agent_expertise: Dict[str, ExpertiseProfile] = {}
        self.skill_tree = SkillTree()
        
    def initialize_agent(self, agent_id: str, domain: str, starting_level: int = 1):
        """Initialize expertise for a new agent"""
        profile = ExpertiseProfile(
            domain=domain,
            level=starting_level
        )
        
        # Add domain skills
        for skill in self.skill_tree.get_skills_for_domain(domain):
            profile.add_skill(skill)
            
        self.agent_expertise[agent_id] = profile
        
    def gain_experience(self, agent_id: str, skill: str, amount: float) -> Dict[str, Any]:
        """Agent gains experience in a skill"""
        if agent_id not in self.agent_expertise:
            return {"success": False, "reason": "Agent not found"}
            
        profile = self.agent_expertise[agent_id]
        leveled_up = profile.gain_skill_xp(skill, amount)
        
        result = {
            "success": True,
            "leveled_up": leveled_up,
            "new_level": profile.get_skill_level(skill)
        }
        
        if leveled_up:
            # Check for ability unlocks
            unlocked = self.skill_tree.check_ability_unlock(profile)
            if unlocked:
                result["abilities_unlocked"] = [a.name for a in unlocked]
                
        return result
        
    def record_success(self, agent_id: str):
        """Record a successful application of expertise"""
        if agent_id in self.agent_expertise:
            self.agent_expertise[agent_id].record_success()
            
    def get_expertise(self, agent_id: str) -> Optional[ExpertiseProfile]:
        """Get agent's expertise profile"""
        return self.agent_expertise.get(agent_id)
        
    def get_masters(self, domain: str) -> List[str]:
        """Get all master-level agents in a domain"""
        masters = []
        for agent_id, profile in self.agent_expertise.items():
            if profile.domain == domain and profile.level >= 8:
                masters.append(agent_id)
        return masters
        
    def to_dict(self) -> Dict:
        """Serialize to dictionary"""
        return {
            agent_id: {
                "domain": profile.domain,
                "level": profile.level,
                "skills": {
                    name: {"level": skill.level, "experience": skill.experience}
                    for name, skill in profile.skills.items()
                },
                "proven_successes": profile.proven_successes,
                "teaching_ability": profile.teaching_ability
            }
            for agent_id, profile in self.agent_expertise.items()
        }

# Global instance
global_expertise_manager = ExpertiseManager()
