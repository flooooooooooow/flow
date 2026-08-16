#!/usr/bin/env python3
"""
Meta-agents that analyze the analysis itself.

These agents operate at a higher level, considering how other agents
might be biased or how the overall system should behave.
"""

import hashlib
from datetime import datetime

try:
    from backlog_sorter.agents import BacklogItem, Agent
except ImportError:
    from agents import BacklogItem, Agent


class BiasDetectorAgent(Agent):
    """Detects and counteracts potential biases in other agents."""
    
    name = "BiasDetectorAgent"
    weight = 0.8
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Items that might be over-hyped
        overhyped = ["demo", "showcase", "benchmark", "gif"]
        if any(kw in title_lower for kw in overhyped):
            return 2  # Counter the hype
        
        # Items that might be under-valued
        undervalued = ["cleanup", "refactor", "fix", "internal"]
        if any(kw in title_lower for kw in undervalued):
            return 4  # Boost the unsexy work
        
        return 3


class ConsensusBuilderAgent(Agent):
    """Favors items that would likely achieve consensus."""
    
    name = "ConsensusBuilderAgent"
    weight = 0.7
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Non-controversial items
        safe = ["fix", "docs", "test", "cleanup"]
        if any(kw in title_lower for kw in safe):
            return 5
        
        # Potentially divisive items
        divisive = ["new", "experimental", "redesign"]
        if any(kw in title_lower for kw in divisive):
            return 2
        
        return 3


class StrategicPatternAgent(Agent):
    """Looks for strategic patterns in the backlog."""
    
    name = "StrategicPatternAgent"
    weight = 1.0
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        category_lower = item.category.lower()
        
        # Platform expansion pattern
        if any(kw in title_lower for kw in ["windows", "linux", "wasm"]):
            return 5
        
        # Compiler maturity pattern
        if any(kw in title_lower for kw in ["codegen", "type", "pattern"]):
            return 4
        
        # Immediate priorities
        if "immediate" in category_lower:
            return 5
        
        return 3


class ResourceAllocationAgent(Agent):
    """Considers resource allocation and parallelization."""
    
    name = "ResourceAllocationAgent"
    weight = 0.9
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Items that can be parallelized
        parallel = ["demo", "docs", "test", "benchmark"]
        if any(kw in title_lower for kw in parallel):
            return 5
        
        # Items that need focused attention
        focused = ["compiler", "type", "codegen", "mlir"]
        if any(kw in title_lower for kw in focused):
            return 3
        
        return 3


class OpportunityCostAgent(Agent):
    """Evaluates opportunity cost of doing this vs something else."""
    
    name = "OpportunityCostAgent"
    weight = 1.1
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # High opportunity cost to delay
        urgent = ["fix", "bug", "crash", "security"]
        if any(kw in title_lower for kw in urgent):
            return 5
        
        # Low opportunity cost
        can_wait = ["cleanup", "refactor", "docs"]
        if any(kw in title_lower for kw in can_wait):
            return 2
        
        return 3


class NetworkEffectAgent(Agent):
    """Evaluates network effects and ecosystem impact."""
    
    name = "NetworkEffectAgent"
    weight = 1.0
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Items that create network effects
        network = ["wasm", "package", "registry", "community", "docs"]
        if any(kw in title_lower for kw in network):
            return 5
        
        # Internal improvements
        internal = ["refactor", "cleanup", "internal"]
        if any(kw in title_lower for kw in internal):
            return 2
        
        return 3


class TechnicalLeverageAgent(Agent):
    """Evaluates technical leverage - does this make other things easier?"""
    
    name = "TechnicalLeverageAgent"
    weight = 1.2
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # High leverage items
        leverage = ["codegen", "type", "compiler", "mlir", "pattern"]
        if any(kw in title_lower for kw in leverage):
            return 5
        
        # Low leverage (one-off)
        one_off = ["demo", "gif", "benchmark"]
        if any(kw in title_lower for kw in one_off):
            return 2
        
        return 3


class UserJourneyAgent(Agent):
    """Evaluates impact on user journey and onboarding."""
    
    name = "UserJourneyAgent"
    weight = 1.0
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # First impression items
        first_impression = ["demo", "tutorial", "docs", "playground", "repl"]
        if any(kw in title_lower for kw in first_impression):
            return 5
        
        # Advanced user items
        advanced = ["mlir", "optimization", "simd"]
        if any(kw in title_lower for kw in advanced):
            return 2
        
        return 3


class InnovationAgent(Agent):
    """Evaluates innovation and differentiation potential."""
    
    name = "InnovationAgent"
    weight = 1.1
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Innovative/unique features
        innovative = ["effect", "capability", "autodiff", "temporal"]
        if any(kw in title_lower for kw in innovative):
            return 5
        
        # Table stakes features
        table_stakes = ["windows", "linux", "fix", "docs"]
        if any(kw in title_lower for kw in table_stakes):
            return 2
        
        return 3


class MaintenanceBurdenAgent(Agent):
    """Evaluates ongoing maintenance burden."""
    
    name = "MaintenanceBurdenAgent"
    weight = 0.8
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Low maintenance items
        low_maint = ["docs", "demo", "cleanup"]
        if any(kw in title_lower for kw in low_maint):
            return 5
        
        # High maintenance items
        high_maint = ["windows", "gpu", "wasm", "async"]
        if any(kw in title_lower for kw in high_maint):
            return 2
        
        return 3


class ReversibilityAgent(Agent):
    """Evaluates how reversible/changeable the decision is."""
    
    name = "ReversibilityAgent"
    weight = 0.7
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Easily reversible
        reversible = ["demo", "docs", "benchmark", "cleanup"]
        if any(kw in title_lower for kw in reversible):
            return 5
        
        # Hard to reverse (API changes, etc)
        irreversible = ["type", "syntax", "abi", "breaking"]
        if any(kw in title_lower for kw in irreversible):
            return 2
        
        return 3


class EnergyLevelAgent(Agent):
    """Matches tasks to energy levels (complex vs routine)."""
    
    name = "EnergyLevelAgent"
    weight = 0.6
    
    def evaluate(self, item: BacklogItem) -> int:
        # Time of day consideration
        hour = datetime.now().hour
        
        title_lower = item.title.lower()
        
        # Morning = high energy, complex tasks
        if 9 <= hour <= 12:
            complex_tasks = ["compiler", "type", "mlir", "optimization"]
            if any(kw in title_lower for kw in complex_tasks):
                return 5
        
        # Afternoon = medium energy
        if 13 <= hour <= 17:
            medium_tasks = ["fix", "test", "docs"]
            if any(kw in title_lower for kw in medium_tasks):
                return 5
        
        # Evening = low energy, routine tasks
        if hour >= 18 or hour <= 8:
            routine_tasks = ["cleanup", "demo", "rename"]
            if any(kw in title_lower for kw in routine_tasks):
                return 5
        
        return 3


class FlowStateAgent(Agent):
    """Evaluates tasks for flow state potential."""
    
    name = "FlowStateAgent"
    weight = 0.7
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Good for flow state (clear, challenging, feedback)
        flow_friendly = ["compiler", "codegen", "optimization", "algorithm"]
        if any(kw in title_lower for kw in flow_friendly):
            return 5
        
        # Interruption-prone
        interrupt_prone = ["docs", "review", "meeting", "discuss"]
        if any(kw in title_lower for kw in interrupt_prone):
            return 2
        
        return 3


class ContextSwitchAgent(Agent):
    """Minimizes context switching cost."""
    
    name = "ContextSwitchAgent"
    weight = 0.6
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        category_lower = item.category.lower()
        
        # Same category = less context switch
        if "compiler" in category_lower or "phase" in category_lower:
            if any(kw in title_lower for kw in ["codegen", "type", "parser"]):
                return 5
        
        # Standalone tasks
        standalone = ["demo", "docs", "benchmark"]
        if any(kw in title_lower for kw in standalone):
            return 4
        
        return 3


class FunFactorAgent(Agent):
    """Evaluates how fun/enjoyable the task is."""
    
    name = "FunFactorAgent"
    weight = 0.5
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Fun tasks
        fun = ["demo", "game", "graphics", "gpu", "visual", "tetris"]
        if any(kw in title_lower for kw in fun):
            return 5
        
        # Less fun tasks
        boring = ["cleanup", "docs", "fix", "refactor"]
        if any(kw in title_lower for kw in boring):
            return 2
        
        return 3


class LegacyImpactAgent(Agent):
    """Evaluates impact on legacy code and backwards compatibility."""
    
    name = "LegacyImpactAgent"
    weight = 0.8
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # No legacy impact
        safe = ["demo", "docs", "benchmark", "new"]
        if any(kw in title_lower for kw in safe):
            return 5
        
        # Potential breaking changes
        risky = ["refactor", "redesign", "breaking", "remove"]
        if any(kw in title_lower for kw in risky):
            return 2
        
        return 3


class DocumentationDebtAgent(Agent):
    """Tracks documentation debt."""
    
    name = "DocumentationDebtAgent"
    weight = 0.7
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Reduces doc debt
        reduces_debt = ["docs", "tutorial", "example", "readme"]
        if any(kw in title_lower for kw in reduces_debt):
            return 5
        
        # Creates doc debt (new features without docs)
        creates_debt = ["new", "add", "feature"]
        if any(kw in title_lower for kw in creates_debt):
            return 2
        
        return 3


class TestCoverageAgent(Agent):
    """Evaluates test coverage implications."""
    
    name = "TestCoverageAgent"
    weight = 0.8
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Improves coverage
        improves = ["test", "fuzz", "coverage", "verify"]
        if any(kw in title_lower for kw in improves):
            return 5
        
        # Needs testing
        needs_testing = ["new", "feature", "add"]
        if any(kw in title_lower for kw in needs_testing):
            return 2
        
        return 3


class ArchitecturalFitAgent(Agent):
    """Evaluates fit with overall architecture."""
    
    name = "ArchitecturalFitAgent"
    weight = 1.0
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Aligns with architecture
        aligned = ["effect", "capability", "type", "compiler"]
        if any(kw in title_lower for kw in aligned):
            return 5
        
        # Orthogonal to architecture
        orthogonal = ["demo", "docs", "benchmark"]
        if any(kw in title_lower for kw in orthogonal):
            return 3
        
        return 3


# Export all meta agents


# Export all meta agents
class FlowIdiomAgent(Agent):
    """Encourages Flow idioms and best practices."""

    name = "FlowIdiomAgent"
    weight = 0.9

    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()

        # Tasks related to encouraging idioms, style, effects, pointers
        idioms = ["idiom", "style", "lint", "effect", "pointer", "mutability"]
        if any(kw in title_lower for kw in idioms):
            return 5

        return 3


META_AGENTS = [
    BiasDetectorAgent,
    ConsensusBuilderAgent,
    StrategicPatternAgent,
    ResourceAllocationAgent,
    OpportunityCostAgent,
    NetworkEffectAgent,
    TechnicalLeverageAgent,
    UserJourneyAgent,
    InnovationAgent,
    MaintenanceBurdenAgent,
    ReversibilityAgent,
    EnergyLevelAgent,
    FlowStateAgent,
    ContextSwitchAgent,
    FunFactorAgent,
    LegacyImpactAgent,
    DocumentationDebtAgent,
    TestCoverageAgent,
    ArchitecturalFitAgent,
    FlowIdiomAgent,
]


# Need to update META_AGENTS list
