#!/usr/bin/env python3
"""
Temporal agents that consider time-based factors.

These agents evaluate items based on timing, momentum, and strategic windows.
"""

import random
from datetime import datetime

try:
    from backlog_sorter.agents import BacklogItem, Agent
except ImportError:
    from agents import BacklogItem, Agent


class MomentumWindowAgent(Agent):
    """Evaluates if now is the right time for this item."""
    
    name = "MomentumWindowAgent"
    weight = 0.9
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        category_lower = item.category.lower()
        
        # Immediate items have momentum
        if "immediate" in category_lower or "this week" in category_lower:
            return 5
        
        # Short term items are timely
        if "short term" in category_lower or "this month" in category_lower:
            return 4
        
        # Demo/showcase items build momentum
        if any(kw in title_lower for kw in ["demo", "gif", "showcase", "benchmark"]):
            return 5
        
        return 3


class TechnicalDebtAccrualAgent(Agent):
    """Evaluates how much debt is accruing by delaying this item."""
    
    name = "TechnicalDebtAccrualAgent"
    weight = 0.8
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Cleanup items accrue debt if delayed
        if any(kw in title_lower for kw in ["cleanup", "refactor", "fix", "bug"]):
            return 4
        
        # Codegen issues block other work
        if "codegen" in title_lower:
            return 5
        
        # New features don't accrue debt
        if any(kw in title_lower for kw in ["new", "add", "feature"]):
            return 2
        
        return 3


class CompetitivePressureAgent(Agent):
    """Evaluates competitive pressure from Mojo/Julia/Rust."""
    
    name = "CompetitivePressureAgent"
    weight = 1.0
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Features that competitors have
        competitive = ["gpu", "wasm", "simd", "autodiff", "benchmark"]
        if any(kw in title_lower for kw in competitive):
            return 5
        
        # Platform support is table stakes
        if any(kw in title_lower for kw in ["windows", "linux"]):
            return 4
        
        # Unique features that differentiate
        unique = ["effect", "capability", "temporal"]
        if any(kw in title_lower for kw in unique):
            return 5
        
        return 2


class CommunityMomentumAgent(Agent):
    """Evaluates items that would generate community excitement."""
    
    name = "CommunityMomentumAgent"
    weight = 1.1
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Exciting announcements
        exciting = ["demo", "gif", "video", "showcase", "benchmark", "comparison"]
        if any(kw in title_lower for kw in exciting):
            return 5
        
        # Platform expansion
        if any(kw in title_lower for kw in ["wasm", "windows", "linux"]):
            return 4
        
        # Self-hosting is a milestone
        if "self-hosting" in title_lower:
            return 5
        
        return 2


class SeasonalRelevanceAgent(Agent):
    """Considers seasonal/calendar relevance."""
    
    name = "SeasonalRelevanceAgent"
    weight = 0.5
    
    def evaluate(self, item: BacklogItem) -> int:
        # Get current month
        month = datetime.now().month
        
        title_lower = item.title.lower()
        
        # Conference season (spring/fall) - demos matter more
        if month in [3, 4, 5, 9, 10, 11]:
            if any(kw in title_lower for kw in ["demo", "benchmark", "showcase"]):
                return 5
        
        # End of year - cleanup and stability
        if month in [11, 12]:
            if any(kw in title_lower for kw in ["cleanup", "fix", "stable"]):
                return 4
        
        # New year - big features
        if month in [1, 2]:
            if any(kw in title_lower for kw in ["wasm", "gpu", "self-hosting"]):
                return 5
        
        return 3


class DependencyChainAgent(Agent):
    """Evaluates position in dependency chains."""
    
    name = "DependencyChainAgent"
    weight = 1.2
    
    DEPENDENCY_CHAINS = {
        # Item -> what it enables
        "codegen": ["examples", "demos", "benchmarks"],
        "pattern matching": ["exhaustiveness", "guards"],
        "wasm": ["playground", "web demos"],
        "graphics": ["demos", "games", "visual"],
        "windows": ["cross-platform", "adoption"],
    }
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Check if this item enables others
        for enabler, enabled in self.DEPENDENCY_CHAINS.items():
            if enabler in title_lower:
                return 5  # High priority - unblocks work
        
        # Check if this item is blocked
        for enabler, enabled_list in self.DEPENDENCY_CHAINS.items():
            for enabled in enabled_list:
                if enabled in title_lower:
                    return 2  # Lower priority - blocked
        
        return 3


class VersionMilestoneAgent(Agent):
    """Evaluates alignment with version milestones."""
    
    name = "VersionMilestoneAgent"
    weight = 1.0
    
    def evaluate(self, item: BacklogItem) -> int:
        category_lower = item.category.lower()
        
        # v0.4.0 focus items
        if "immediate" in category_lower or "this week" in category_lower:
            return 5
        
        # v0.5.0 items
        if "short term" in category_lower or "this month" in category_lower:
            return 4
        
        # v1.0.0 items
        if "medium term" in category_lower:
            return 3
        
        return 2


class BurndownVelocityAgent(Agent):
    """Simulates sprint velocity considerations."""
    
    name = "BurndownVelocityAgent"
    weight = 0.7
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Quick items help velocity
        quick = ["demo", "gif", "fix", "cleanup", "rename"]
        if any(kw in title_lower for kw in quick):
            return 5
        
        # Large items slow velocity
        large = ["self-hosting", "wasm", "gpu", "windows"]
        if any(kw in title_lower for kw in large):
            return 2
        
        return 3


class TeamMoraleAgent(Agent):
    """Evaluates impact on team morale and motivation."""
    
    name = "TeamMoraleAgent"
    weight = 0.8
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Visible progress boosts morale
        visible = ["demo", "gif", "showcase", "graphics", "visual"]
        if any(kw in title_lower for kw in visible):
            return 5
        
        # Fixing bugs feels good
        if "fix" in title_lower or "bug" in title_lower:
            return 4
        
        # Cleanup is satisfying
        if "cleanup" in title_lower:
            return 4
        
        # Large uncertain projects can be draining
        if any(kw in title_lower for kw in ["self-hosting", "wasm"]):
            return 2
        
        return 3


class LearningCurveAgent(Agent):
    """Evaluates learning/skill development opportunities."""
    
    name = "LearningCurveAgent"
    weight = 0.6
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Deep technical work = learning
        learning = ["mlir", "llvm", "gpu", "wasm", "optimization"]
        if any(kw in title_lower for kw in learning):
            return 5
        
        # Compiler work is educational
        if any(kw in title_lower for kw in ["codegen", "parser", "type"]):
            return 4
        
        # Routine work = less learning
        if any(kw in title_lower for kw in ["cleanup", "rename", "demo"]):
            return 2
        
        return 3


# Export all temporal agents
TEMPORAL_AGENTS = [
    MomentumWindowAgent,
    TechnicalDebtAccrualAgent,
    CompetitivePressureAgent,
    CommunityMomentumAgent,
    SeasonalRelevanceAgent,
    DependencyChainAgent,
    VersionMilestoneAgent,
    BurndownVelocityAgent,
    TeamMoraleAgent,
    LearningCurveAgent,
]
