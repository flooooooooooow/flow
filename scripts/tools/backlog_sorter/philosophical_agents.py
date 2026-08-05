#!/usr/bin/env python3
"""
Philosophical agents that consider deeper questions.

These agents bring philosophical perspectives to backlog prioritization.
"""

import hashlib
from datetime import datetime

try:
    from backlog_sorter.agents import BacklogItem, Agent
except ImportError:
    from agents import BacklogItem, Agent


class StoicAgent(Agent):
    """Focus on what you can control. Accept what you cannot."""
    
    name = "StoicAgent"
    weight = 0.6
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Things we control
        controllable = ["fix", "cleanup", "docs", "test", "refactor"]
        if any(kw in title_lower for kw in controllable):
            return 5
        
        # External dependencies
        external = ["windows", "gpu", "wasm"]  # Platform dependencies
        if any(kw in title_lower for kw in external):
            return 2
        
        return 3


class UtilitarianAgent(Agent):
    """Greatest good for the greatest number."""
    
    name = "UtilitarianAgent"
    weight = 0.8
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Benefits many users
        broad_impact = ["docs", "tutorial", "demo", "platform", "wasm"]
        if any(kw in title_lower for kw in broad_impact):
            return 5
        
        # Benefits few users
        narrow_impact = ["internal", "refactor", "cleanup"]
        if any(kw in title_lower for kw in narrow_impact):
            return 2
        
        return 3


class MinimalistPhilosophyAgent(Agent):
    """Perfection is achieved when there is nothing left to remove."""
    
    name = "MinimalistPhilosophyAgent"
    weight = 0.7
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Simplification
        simplify = ["cleanup", "remove", "simplify", "flatten", "delete"]
        if any(kw in title_lower for kw in simplify):
            return 5
        
        # Adding complexity
        complexity = ["add", "new", "feature", "system"]
        if any(kw in title_lower for kw in complexity):
            return 2
        
        return 3


class PragmatistPhilosophyAgent(Agent):
    """Truth is what works. Ship it and iterate."""
    
    name = "PragmatistPhilosophyAgent"
    weight = 0.9
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Practical, shippable
        practical = ["demo", "fix", "example", "benchmark"]
        if any(kw in title_lower for kw in practical):
            return 5
        
        # Theoretical, perfectionist
        theoretical = ["exhaustive", "complete", "perfect"]
        if any(kw in title_lower for kw in theoretical):
            return 2
        
        return 3


class ExistentialistAgent(Agent):
    """Existence precedes essence. Define yourself through action."""
    
    name = "ExistentialistAgent"
    weight = 0.5
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Defining actions
        defining = ["self-hosting", "unique", "effect", "capability"]
        if any(kw in title_lower for kw in defining):
            return 5
        
        # Following others
        following = ["comparison", "vs", "like"]
        if any(kw in title_lower for kw in following):
            return 2
        
        return 3


class ZenAgent(Agent):
    """Before enlightenment: chop wood, carry water. After: same."""
    
    name = "ZenAgent"
    weight = 0.5
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Simple, present-moment tasks
        present = ["fix", "cleanup", "test", "docs"]
        if any(kw in title_lower for kw in present):
            return 5
        
        # Future-oriented complexity
        future = ["roadmap", "plan", "design", "architecture"]
        if any(kw in title_lower for kw in future):
            return 2
        
        return 3


class KaizenAgent(Agent):
    """Continuous improvement. Small steps, big results."""
    
    name = "KaizenAgent"
    weight = 0.8
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Small improvements
        small = ["fix", "cleanup", "improve", "enhance", "polish"]
        if any(kw in title_lower for kw in small):
            return 5
        
        # Big bang changes
        big = ["rewrite", "redesign", "overhaul"]
        if any(kw in title_lower for kw in big):
            return 2
        
        return 3


class FirstPrinciplesAgent(Agent):
    """Reason from fundamentals, not by analogy."""
    
    name = "FirstPrinciplesAgent"
    weight = 1.0
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Fundamental work
        fundamental = ["type", "compiler", "parser", "codegen", "core"]
        if any(kw in title_lower for kw in fundamental):
            return 5
        
        # Surface-level work
        surface = ["demo", "docs", "benchmark"]
        if any(kw in title_lower for kw in surface):
            return 2
        
        return 3


class AgileManifestoAgent(Agent):
    """Working software over comprehensive documentation."""
    
    name = "AgileManifestoAgent"
    weight = 0.8
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Working software
        working = ["demo", "example", "fix", "feature"]
        if any(kw in title_lower for kw in working):
            return 5
        
        # Documentation (still valuable, just less)
        docs = ["docs", "spec", "design"]
        if any(kw in title_lower for kw in docs):
            return 3
        
        return 3


class WabiSabiAgent(Agent):
    """Beauty in imperfection. Ship the imperfect."""
    
    name = "WabiSabiAgent"
    weight = 0.6
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Accepting imperfection
        imperfect = ["demo", "prototype", "draft", "wip"]
        if any(kw in title_lower for kw in imperfect):
            return 5
        
        # Perfectionism
        perfect = ["complete", "exhaustive", "full", "perfect"]
        if any(kw in title_lower for kw in perfect):
            return 2
        
        return 3


class YAGNIAgent(Agent):
    """You Ain't Gonna Need It. Build what's needed now."""
    
    name = "YAGNIAgent"
    weight = 0.9
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        category_lower = item.category.lower()
        
        # Needed now
        if "immediate" in category_lower:
            return 5
        
        # Speculative features
        speculative = ["might", "could", "future", "eventually"]
        if any(kw in title_lower for kw in speculative):
            return 1
        
        return 3


# Export all philosophical agents
PHILOSOPHICAL_AGENTS = [
    StoicAgent,
    UtilitarianAgent,
    MinimalistPhilosophyAgent,
    PragmatistPhilosophyAgent,
    ExistentialistAgent,
    ZenAgent,
    KaizenAgent,
    FirstPrinciplesAgent,
    AgileManifestoAgent,
    WabiSabiAgent,
    YAGNIAgent,
]
