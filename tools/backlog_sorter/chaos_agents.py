#!/usr/bin/env python3
"""
Chaos agents that add randomness and unconventional perspectives.

These agents introduce controlled chaos to avoid groupthink and
surface unexpected priorities.
"""

import random
import hashlib

try:
    from backlog_sorter.agents import BacklogItem, Agent
except ImportError:
    from agents import BacklogItem, Agent


class RandomAgent(Agent):
    """Pure chaos - random scores to break ties and avoid bias."""
    
    name = "RandomAgent"
    weight = 0.3  # Low weight - just for tie-breaking
    
    def evaluate(self, item: BacklogItem) -> int:
        # Use item title as seed for reproducibility
        seed = int(hashlib.md5(item.title.encode()).hexdigest()[:8], 16)
        random.seed(seed)
        return random.randint(1, 5)


class ContrarianAgent(Agent):
    """Deliberately contrarian - questions conventional wisdom."""
    
    name = "ContrarianAgent"
    weight = 0.4
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Contrarian on "obvious" priorities
        if any(kw in title_lower for kw in ["demo", "benchmark", "showcase"]):
            return 2  # "Marketing fluff"
        
        # Loves the unsexy work
        if any(kw in title_lower for kw in ["cleanup", "refactor", "internal"]):
            return 5  # "This is the real work"
        
        # Skeptical of big projects
        if any(kw in title_lower for kw in ["wasm", "gpu", "self-hosting"]):
            return 1  # "Scope creep"
        
        return 3


class YOLOAgent(Agent):
    """Go big or go home - favors ambitious projects."""
    
    name = "YOLOAgent"
    weight = 0.5
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # YOLO loves big ambitious stuff
        ambitious = ["self-hosting", "gpu", "wasm", "windows", "autodiff"]
        if any(kw in title_lower for kw in ambitious):
            return 5
        
        # Boring stuff is boring
        boring = ["cleanup", "fix", "rename", "docs"]
        if any(kw in title_lower for kw in boring):
            return 1
        
        return 3


class MinimalistAgent(Agent):
    """Less is more - favors simplification and removal."""
    
    name = "MinimalistAgent"
    weight = 0.5
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Loves cleanup and simplification
        simple = ["cleanup", "remove", "simplify", "flatten", "delete"]
        if any(kw in title_lower for kw in simple):
            return 5
        
        # Hates adding complexity
        complex_kw = ["add", "new", "feature", "system"]
        if any(kw in title_lower for kw in complex_kw):
            return 2
        
        return 3


class PerfectionistAgent(Agent):
    """Nothing ships until it's perfect."""
    
    name = "PerfectionistAgent"
    weight = 0.4
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Loves polish and correctness
        polish = ["fix", "exhaustive", "complete", "full", "proper"]
        if any(kw in title_lower for kw in polish):
            return 5
        
        # Hates quick hacks
        if "demo" in title_lower or "quick" in title_lower:
            return 2
        
        return 3


class PragmatistAgent(Agent):
    """Ship it! Perfect is the enemy of good."""
    
    name = "PragmatistAgent"
    weight = 0.6
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Ship visible progress
        ship = ["demo", "example", "showcase", "benchmark"]
        if any(kw in title_lower for kw in ship):
            return 5
        
        # Don't gold-plate
        if "exhaustive" in title_lower or "complete" in title_lower:
            return 2
        
        return 3


class CuriousAgent(Agent):
    """Follows interesting technical challenges."""
    
    name = "CuriousAgent"
    weight = 0.5
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Interesting technical challenges
        interesting = ["mlir", "llvm", "gpu", "autodiff", "effect", "wasm"]
        if any(kw in title_lower for kw in interesting):
            return 5
        
        # Routine work is boring
        routine = ["cleanup", "rename", "docs", "demo"]
        if any(kw in title_lower for kw in routine):
            return 2
        
        return 3


class LazyAgent(Agent):
    """Minimum effort for maximum impact."""
    
    name = "LazyAgent"
    weight = 0.4
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Easy wins
        easy = ["demo", "gif", "rename", "cleanup"]
        if any(kw in title_lower for kw in easy):
            return 5
        
        # Hard work? No thanks
        hard = ["self-hosting", "wasm", "gpu", "windows"]
        if any(kw in title_lower for kw in hard):
            return 1
        
        return 3


class ParanoidAgent(Agent):
    """What could go wrong? Everything."""
    
    name = "ParanoidAgent"
    weight = 0.5
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Safety and correctness
        safe = ["safety", "fix", "bug", "test", "verify", "exhaustive"]
        if any(kw in title_lower for kw in safe):
            return 5
        
        # Risky new features
        risky = ["new", "experimental", "wasm", "gpu"]
        if any(kw in title_lower for kw in risky):
            return 2
        
        return 3


class OptimistAgent(Agent):
    """Everything will work out! Ship it!"""
    
    name = "OptimistAgent"
    weight = 0.4
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Big ambitious projects will totally work
        ambitious = ["self-hosting", "wasm", "gpu", "windows"]
        if any(kw in title_lower for kw in ambitious):
            return 5
        
        # Boring safety stuff - we'll be fine
        if "safety" in title_lower or "fix" in title_lower:
            return 2
        
        return 4  # Everything is great!


# Export all chaos agents
CHAOS_AGENTS = [
    RandomAgent,
    ContrarianAgent,
    YOLOAgent,
    MinimalistAgent,
    PerfectionistAgent,
    PragmatistAgent,
    CuriousAgent,
    LazyAgent,
    ParanoidAgent,
    OptimistAgent,
]
