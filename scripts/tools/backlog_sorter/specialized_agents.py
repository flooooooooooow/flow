#!/usr/bin/env python3
"""
Specialized agents for deep backlog analysis.

These agents focus on specific aspects of the Flow language project.
"""

from dataclasses import dataclass
from typing import Optional
import re

try:
    from backlog_sorter.agents import BacklogItem, Agent
except ImportError:
    from agents import BacklogItem, Agent


class LanguageDesignAgent(Agent):
    """Evaluates items that affect language semantics and design."""
    
    name = "LanguageDesignAgent"
    weight = 1.4
    
    CORE_LANGUAGE = [
        "pattern", "match", "closure", "generic", "trait", "enum",
        "type", "effect", "capability", "autodiff"
    ]
    
    SYNTAX_SUGAR = ["async", "await", "guard", "exhaustive"]
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        core_matches = sum(1 for kw in self.CORE_LANGUAGE if kw in title_lower)
        if core_matches >= 2:
            return 5
        if core_matches == 1:
            return 4
        
        if any(kw in title_lower for kw in self.SYNTAX_SUGAR):
            return 3
        
        return 2


class EcosystemReadinessAgent(Agent):
    """Evaluates items that make Flow production-ready."""
    
    name = "EcosystemReadinessAgent"
    weight = 1.2
    
    PRODUCTION_KEYWORDS = [
        "package", "registry", "debugger", "profiler", "benchmark",
        "documentation", "tutorial", "example", "demo"
    ]
    
    ENTERPRISE_KEYWORDS = [
        "security", "audit", "compliance", "logging", "monitoring"
    ]
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        if any(kw in title_lower for kw in self.ENTERPRISE_KEYWORDS):
            return 5
        
        prod_matches = sum(1 for kw in self.PRODUCTION_KEYWORDS if kw in title_lower)
        if prod_matches >= 2:
            return 5
        if prod_matches == 1:
            return 4
        
        return 2


class DifferentiatorAgent(Agent):
    """Prioritizes features that differentiate Flow from other languages."""
    
    name = "DifferentiatorAgent"
    weight = 1.5  # High weight - unique features matter
    
    UNIQUE_TO_FLOW = [
        "effect", "capability", "autodiff", "temporal", "evolution"
    ]
    
    COMPETITIVE_EDGE = [
        "gpu", "simd", "vectorization", "metal", "cuda", "wasm"
    ]
    
    MOJO_JULIA_COMPETITION = [
        "ml", "tensor", "neural", "optimization", "scientific"
    ]
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        if any(kw in title_lower for kw in self.UNIQUE_TO_FLOW):
            return 5
        
        if any(kw in title_lower for kw in self.COMPETITIVE_EDGE):
            return 4
        
        if any(kw in title_lower for kw in self.MOJO_JULIA_COMPETITION):
            return 4
        
        return 2


class CommunityGrowthAgent(Agent):
    """Prioritizes items that help grow the community."""
    
    name = "CommunityGrowthAgent"
    weight = 1.0
    
    COMMUNITY_KEYWORDS = [
        "demo", "tutorial", "docs", "example", "playground",
        "getting started", "showcase", "gif", "video"
    ]
    
    CONTRIBUTION_KEYWORDS = [
        "contributing", "issue", "pr", "template", "ci", "test"
    ]
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        if any(kw in title_lower for kw in self.COMMUNITY_KEYWORDS):
            return 5
        
        if any(kw in title_lower for kw in self.CONTRIBUTION_KEYWORDS):
            return 4
        
        return 2


class PerformanceAgent(Agent):
    """Evaluates performance-related improvements."""
    
    name = "PerformanceAgent"
    weight = 1.1
    
    PERF_KEYWORDS = [
        "optimization", "vectorization", "inlining", "simd",
        "gpu", "parallel", "concurrent", "fast", "speed"
    ]
    
    MLIR_LLVM = ["mlir", "llvm", "codegen", "backend"]
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        perf_matches = sum(1 for kw in self.PERF_KEYWORDS if kw in title_lower)
        if perf_matches >= 2:
            return 5
        if perf_matches == 1:
            return 4
        
        if any(kw in title_lower for kw in self.MLIR_LLVM):
            return 4
        
        return 2


class SafetyAgent(Agent):
    """Prioritizes memory safety and correctness features."""
    
    name = "SafetyAgent"
    weight = 1.3
    
    SAFETY_KEYWORDS = [
        "safety", "bounds", "check", "verify", "exhaustive",
        "type", "strict", "error", "crash", "bug"
    ]
    
    MEMORY_KEYWORDS = [
        "memory", "alloc", "leak", "pool", "arena", "gc"
    ]
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        if any(kw in title_lower for kw in self.SAFETY_KEYWORDS):
            return 5
        
        if any(kw in title_lower for kw in self.MEMORY_KEYWORDS):
            return 4
        
        return 2


class InteropAgent(Agent):
    """Evaluates FFI and interoperability features."""
    
    name = "InteropAgent"
    weight = 0.9
    
    INTEROP_KEYWORDS = [
        "ffi", "extern", "c", "python", "wasm", "javascript",
        "binding", "interop", "abi"
    ]
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        if any(kw in title_lower for kw in self.INTEROP_KEYWORDS):
            return 5
        
        return 2


class AudioDSPAgent(Agent):
    """Prioritizes audio/DSP-related features (Flow's domain focus)."""
    
    name = "AudioDSPAgent"
    weight = 1.2
    
    AUDIO_KEYWORDS = [
        "audio", "dsp", "rt-safety", "real-time", "buffer",
        "sample", "plugin", "vst", "au", "live"
    ]
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        if any(kw in title_lower for kw in self.AUDIO_KEYWORDS):
            return 5
        
        if "no-alloc" in title_lower or "lock-free" in title_lower:
            return 5
        
        return 2


class DocumentationAgent(Agent):
    """Prioritizes documentation and learning resources."""
    
    name = "DocumentationAgent"
    weight = 0.8
    
    DOC_KEYWORDS = [
        "doc", "tutorial", "guide", "example", "readme",
        "wiki", "spec", "reference", "api"
    ]
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        if any(kw in title_lower for kw in self.DOC_KEYWORDS):
            return 5
        
        return 2


class TestingAgent(Agent):
    """Evaluates testing and quality assurance items."""
    
    name = "TestingAgent"
    weight = 0.9
    
    TEST_KEYWORDS = [
        "test", "fuzz", "coverage", "ci", "regression",
        "benchmark", "verify", "validate"
    ]
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        if any(kw in title_lower for kw in self.TEST_KEYWORDS):
            return 5
        
        return 2


class MomentumAgent(Agent):
    """Prioritizes items that build momentum (quick wins, visible progress)."""
    
    name = "MomentumAgent"
    weight = 1.1
    
    QUICK_WIN_KEYWORDS = [
        "demo", "gif", "fix", "cleanup", "rename", "simple"
    ]
    
    VISIBLE_PROGRESS = [
        "graphics", "visual", "ui", "playground", "showcase"
    ]
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        if any(kw in title_lower for kw in self.QUICK_WIN_KEYWORDS):
            return 5
        
        if any(kw in title_lower for kw in self.VISIBLE_PROGRESS):
            return 4
        
        return 2


class StrategicAlignmentAgent(Agent):
    """Evaluates alignment with Flow's vision and roadmap."""
    
    name = "StrategicAlignmentAgent"
    weight = 1.3
    
    VISION_KEYWORDS = [
        "temporal", "evolution", "effect", "capability",
        "epistemic", "explicit", "portable"
    ]
    
    ROADMAP_PRIORITIES = [
        "v0.4", "v0.5", "v1.0", "immediate", "this week", "this month"
    ]
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        category_lower = item.category.lower()
        
        if any(kw in title_lower for kw in self.VISION_KEYWORDS):
            return 5
        
        if any(kw in category_lower for kw in self.ROADMAP_PRIORITIES):
            return 4
        
        if "immediate" in category_lower:
            return 5
        if "short term" in category_lower:
            return 4
        if "medium term" in category_lower:
            return 3
        
        return 2


class BlockerDetectionAgent(Agent):
    """Identifies items that are blocking other work."""
    
    name = "BlockerDetectionAgent"
    weight = 1.4
    
    BLOCKER_PATTERNS = {
        "codegen": ["examples", "demos", "benchmarks"],
        "pattern matching": ["exhaustiveness", "guards"],
        "wasm": ["playground", "web"],
        "graphics": ["demos", "visual"],
    }
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        for blocker, blocked in self.BLOCKER_PATTERNS.items():
            if blocker in title_lower:
                return 5  # This is a blocker - high priority
        
        for blocker, blocked_list in self.BLOCKER_PATTERNS.items():
            for blocked in blocked_list:
                if blocked in title_lower:
                    return 2  # This is blocked - lower priority
        
        return 3


class FreshEyesAgent(Agent):
    """Simulates a newcomer's perspective - what would impress them?"""
    
    name = "FreshEyesAgent"
    weight = 0.8
    
    IMPRESSIVE_KEYWORDS = [
        "demo", "gif", "video", "playground", "repl",
        "gpu", "wasm", "self-hosting", "benchmark"
    ]
    
    CONFUSING_KEYWORDS = [
        "internal", "refactor", "cleanup", "structure"
    ]
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        if any(kw in title_lower for kw in self.IMPRESSIVE_KEYWORDS):
            return 5
        
        if any(kw in title_lower for kw in self.CONFUSING_KEYWORDS):
            return 2  # Newcomers don't care about internals
        
        return 3


class LongTermValueAgent(Agent):
    """Evaluates long-term strategic value vs short-term gains."""
    
    name = "LongTermValueAgent"
    weight = 1.0
    
    FOUNDATIONAL = [
        "self-hosting", "type system", "effect", "compiler",
        "mlir", "llvm", "architecture"
    ]
    
    SHORT_TERM = [
        "demo", "gif", "fix", "cleanup", "rename"
    ]
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        if any(kw in title_lower for kw in self.FOUNDATIONAL):
            return 5
        
        if any(kw in title_lower for kw in self.SHORT_TERM):
            return 2  # Important but not foundational
        
        return 3


# Export all specialized agents
SPECIALIZED_AGENTS = [
    LanguageDesignAgent,
    EcosystemReadinessAgent,
    DifferentiatorAgent,
    CommunityGrowthAgent,
    PerformanceAgent,
    SafetyAgent,
    InteropAgent,
    AudioDSPAgent,
    DocumentationAgent,
    TestingAgent,
    MomentumAgent,
    StrategicAlignmentAgent,
    BlockerDetectionAgent,
    FreshEyesAgent,
    LongTermValueAgent,
]
