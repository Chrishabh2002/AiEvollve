"""
Domain Knowledge Management System
Provides expert-level knowledge to agents in their specialized domains
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path

class ExpertiseLevel(Enum):
    NOVICE = 1
    INTERMEDIATE = 3
    ADVANCED = 5
    EXPERT = 7
    MASTER = 10

@dataclass
class KnowledgeArea:
    """A specific area of expertise within a domain"""
    name: str
    description: str
    principles: List[str]
    patterns: List[Dict[str, str]]  # Pattern name -> description
    anti_patterns: List[Dict[str, str]]
    best_practices: List[str]
    tools: List[str]
    case_studies: List[Dict[str, Any]]
    
@dataclass
class Domain:
    """A complete domain of knowledge"""
    name: str
    description: str
    core_principles: List[str]
    knowledge_areas: Dict[str, KnowledgeArea]
    required_skills: List[str]
    success_metrics: List[str]
    
class DomainKnowledge:
    """Manages all domain knowledge for the system"""
    
    def __init__(self):
        self.domains: Dict[str, Domain] = {}
        self._initialize_core_domains()
        
    def _initialize_core_domains(self):
        """Initialize fundamental domains"""
        
        # ARCHITECTURE DOMAIN
        self.domains['architecture'] = Domain(
            name="System Architecture",
            description="Design and structure of complex systems",
            core_principles=[
                "Separation of Concerns: Each component has a single, well-defined purpose",
                "Modularity: Systems are composed of independent, interchangeable modules",
                "Scalability: Design for growth from day one",
                "Resilience: Systems must gracefully handle failures",
                "Simplicity: The simplest solution that works is usually the best",
                "Data-Driven: Architecture decisions based on metrics, not opinions",
                "Evolution: Systems must be designed to evolve over time"
            ],
            knowledge_areas={
                "distributed_systems": KnowledgeArea(
                    name="Distributed Systems",
                    description="Multi-node system design and coordination",
                    principles=[
                        "CAP Theorem: Consistency, Availability, Partition Tolerance - pick 2",
                        "Eventual Consistency: Accept temporary inconsistency for availability",
                        "Idempotency: Operations can be repeated safely",
                        "Circuit Breakers: Prevent cascade failures"
                    ],
                    patterns=[
                        {"name": "Event Sourcing", "description": "Store state changes as events"},
                        {"name": "CQRS", "description": "Separate read and write models"},
                        {"name": "Saga Pattern", "description": "Distributed transactions via compensating actions"},
                        {"name": "Service Mesh", "description": "Infrastructure layer for service communication"}
                    ],
                    anti_patterns=[
                        {"name": "Distributed Monolith", "description": "Microservices with tight coupling"},
                        {"name": "Chatty Services", "description": "Too many inter-service calls"},
                        {"name": "Shared Database", "description": "Multiple services accessing same DB"}
                    ],
                    best_practices=[
                        "Use message queues for async communication",
                        "Implement health checks and monitoring",
                        "Design for idempotency",
                        "Use correlation IDs for tracing"
                    ],
                    tools=["Kafka", "RabbitMQ", "Consul", "etcd"],
                    case_studies=[]
                ),
                "microservices": KnowledgeArea(
                    name="Microservices Architecture",
                    description="Designing systems as independent services",
                    principles=[
                        "Single Responsibility: Each service does one thing well",
                        "Decentralized Data: Each service owns its data",
                        "API-First: Well-defined contracts between services",
                        "Independent Deployment: Services deploy independently"
                    ],
                    patterns=[
                        {"name": "API Gateway", "description": "Single entry point for clients"},
                        {"name": "Service Discovery", "description": "Dynamic service location"},
                        {"name": "Strangler Fig", "description": "Gradual migration from monolith"}
                    ],
                    anti_patterns=[
                        {"name": "Nanoservices", "description": "Services too small to be useful"},
                        {"name": "Shared Libraries", "description": "Coupling via shared code"}
                    ],
                    best_practices=[
                        "Start with a monolith, split when needed",
                        "Use containerization (Docker)",
                        "Implement proper logging and tracing",
                        "Version your APIs"
                    ],
                    tools=["Kubernetes", "Docker", "Istio", "Envoy"],
                    case_studies=[]
                )
            },
            required_skills=["System Design", "Distributed Computing", "Performance Analysis"],
            success_metrics=["System Uptime", "Scalability Factor", "Maintainability Index"]
        )
        
        # ENGINEERING DOMAIN
        self.domains['engineering'] = Domain(
            name="Engineering & Physics",
            description="Mathematical and physical principles for building systems",
            core_principles=[
                "Conservation Laws: Energy, momentum, information are conserved",
                "Optimization: Find the best solution within constraints",
                "Feedback Loops: Systems self-regulate through feedback",
                "Emergence: Complex behavior from simple rules",
                "Entropy: Systems tend toward disorder without energy input"
            ],
            knowledge_areas={
                "algorithms": KnowledgeArea(
                    name="Algorithm Design",
                    description="Efficient problem-solving procedures",
                    principles=[
                        "Time Complexity: Measure efficiency as input grows",
                        "Space Complexity: Memory usage matters",
                        "Divide and Conquer: Break problems into subproblems",
                        "Dynamic Programming: Solve overlapping subproblems once"
                    ],
                    patterns=[
                        {"name": "Two Pointers", "description": "Efficient array traversal"},
                        {"name": "Sliding Window", "description": "Process subarrays efficiently"},
                        {"name": "Binary Search", "description": "O(log n) search in sorted data"},
                        {"name": "Graph Traversal", "description": "BFS/DFS for graph problems"}
                    ],
                    anti_patterns=[
                        {"name": "Premature Optimization", "description": "Optimizing before profiling"},
                        {"name": "Brute Force", "description": "Trying all possibilities without thought"}
                    ],
                    best_practices=[
                        "Analyze complexity before implementing",
                        "Use appropriate data structures",
                        "Test edge cases thoroughly",
                        "Profile before optimizing"
                    ],
                    tools=["Big-O Analysis", "Profilers", "Benchmarking Tools"],
                    case_studies=[]
                )
            },
            required_skills=["Mathematics", "Physics", "Computational Thinking"],
            success_metrics=["Algorithm Efficiency", "Solution Correctness", "Code Performance"]
        )
        
        # GOVERNANCE DOMAIN
        self.domains['governance'] = Domain(
            name="Governance & Ethics",
            description="Decision-making, policy, and ethical frameworks",
            core_principles=[
                "Fairness: Decisions must be equitable and unbiased",
                "Transparency: Processes must be visible and understandable",
                "Accountability: Clear responsibility for decisions",
                "Participation: Stakeholders have voice in decisions",
                "Rule of Law: Consistent application of rules",
                "Adaptability: Governance evolves with needs"
            ],
            knowledge_areas={
                "decision_theory": KnowledgeArea(
                    name="Decision Theory",
                    description="Frameworks for making optimal decisions",
                    principles=[
                        "Expected Value: Weight outcomes by probability",
                        "Risk Assessment: Understand and quantify uncertainty",
                        "Multi-Criteria: Balance multiple objectives",
                        "Game Theory: Consider strategic interactions"
                    ],
                    patterns=[
                        {"name": "Weighted Voting", "description": "Votes weighted by expertise"},
                        {"name": "Veto Power", "description": "Critical stakeholders can block"},
                        {"name": "Consensus Building", "description": "Seek agreement before deciding"},
                        {"name": "Delegation", "description": "Empower experts to decide"}
                    ],
                    anti_patterns=[
                        {"name": "Analysis Paralysis", "description": "Over-analyzing prevents action"},
                        {"name": "Groupthink", "description": "Conformity suppresses dissent"},
                        {"name": "Tyranny of Majority", "description": "Ignoring minority concerns"}
                    ],
                    best_practices=[
                        "Define clear decision criteria upfront",
                        "Seek diverse perspectives",
                        "Document rationale for decisions",
                        "Review decisions periodically"
                    ],
                    tools=["Decision Matrices", "Risk Registers", "Voting Systems"],
                    case_studies=[]
                )
            },
            required_skills=["Policy Design", "Ethics", "Conflict Resolution"],
            success_metrics=["Decision Quality", "Stakeholder Satisfaction", "Policy Effectiveness"]
        )
        
        # SCIENCE DOMAIN
        self.domains['science'] = Domain(
            name="Scientific Research",
            description="Systematic investigation and knowledge discovery",
            core_principles=[
                "Empiricism: Knowledge from observation and experiment",
                "Reproducibility: Results must be verifiable by others",
                "Falsifiability: Hypotheses must be testable",
                "Peer Review: Work validated by experts",
                "Incremental Progress: Build on existing knowledge",
                "Objectivity: Minimize bias in investigation"
            ],
            knowledge_areas={
                "experimental_design": KnowledgeArea(
                    name="Experimental Design",
                    description="Planning and conducting experiments",
                    principles=[
                        "Control Variables: Isolate the factor being tested",
                        "Randomization: Reduce bias in assignment",
                        "Replication: Repeat experiments for reliability",
                        "Statistical Power: Ensure adequate sample size"
                    ],
                    patterns=[
                        {"name": "A/B Testing", "description": "Compare two variants"},
                        {"name": "Factorial Design", "description": "Test multiple factors simultaneously"},
                        {"name": "Longitudinal Study", "description": "Observe over time"}
                    ],
                    anti_patterns=[
                        {"name": "P-Hacking", "description": "Manipulating data to get significance"},
                        {"name": "Cherry Picking", "description": "Selecting favorable data only"},
                        {"name": "Confounding Variables", "description": "Uncontrolled factors affecting results"}
                    ],
                    best_practices=[
                        "Pre-register hypotheses",
                        "Use appropriate statistical tests",
                        "Report all results, not just significant ones",
                        "Share data and methods openly"
                    ],
                    tools=["Statistical Software", "Lab Notebooks", "Data Repositories"],
                    case_studies=[]
                )
            },
            required_skills=["Statistics", "Research Methods", "Critical Thinking"],
            success_metrics=["Research Impact", "Reproducibility Rate", "Citation Count"]
        )
        
    def get_domain(self, domain_name: str) -> Optional[Domain]:
        """Retrieve a domain by name"""
        return self.domains.get(domain_name.lower())
        
    def get_knowledge_for_role(self, role: str) -> List[str]:
        """Get relevant knowledge areas for a role"""
        role_domain_map = {
            "architect": ["architecture"],
            "engineer": ["engineering"],
            "scientist": ["science"],
            "governor": ["governance"],
            "philosopher": ["governance", "science"],
            "builder": ["engineering", "architecture"]
        }
        
        role_lower = role.lower()
        domains = []
        for key, domain_list in role_domain_map.items():
            if key in role_lower:
                domains.extend(domain_list)
                
        return domains
        
    def get_expertise_context(self, domain_name: str, level: ExpertiseLevel) -> str:
        """Generate context string for an agent based on domain and expertise level"""
        domain = self.get_domain(domain_name)
        if not domain:
            return ""
            
        context = f"# {domain.name} Expertise (Level: {level.name})\n\n"
        context += f"{domain.description}\n\n"
        
        context += "## Core Principles:\n"
        for principle in domain.core_principles[:5]:  # Top 5 principles
            context += f"- {principle}\n"
            
        context += "\n## Key Knowledge Areas:\n"
        for area_name, area in list(domain.knowledge_areas.items())[:2]:  # Top 2 areas
            context += f"\n### {area.name}\n"
            context += f"{area.description}\n"
            context += "**Best Practices:**\n"
            for practice in area.best_practices[:3]:
                context += f"- {practice}\n"
                
        return context
        
    def add_case_study(self, domain_name: str, area_name: str, case_study: Dict[str, Any]):
        """Add a case study to a knowledge area (learning from experience)"""
        domain = self.get_domain(domain_name)
        if domain and area_name in domain.knowledge_areas:
            domain.knowledge_areas[area_name].case_studies.append(case_study)
            
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "domains": {
                name: {
                    "name": domain.name,
                    "description": domain.description,
                    "core_principles": domain.core_principles,
                    "required_skills": domain.required_skills,
                    "success_metrics": domain.success_metrics
                }
                for name, domain in self.domains.items()
            }
        }

# Global knowledge base
global_knowledge = DomainKnowledge()
