#!/usr/bin/env python3
"""
Persona-based agents that simulate different stakeholder perspectives.

Each agent embodies a different user type or role, evaluating backlog
items from their unique viewpoint.
"""

try:
    from backlog_sorter.agents import BacklogItem, Agent
except ImportError:
    from agents import BacklogItem, Agent


class NewcomerDeveloperAgent(Agent):
    """A developer just discovering Flow - what would make them stay?"""
    
    name = "NewcomerDeveloperAgent"
    weight = 1.0
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Things that help newcomers
        helpful = ["tutorial", "docs", "example", "demo", "playground", "repl", "getting started"]
        if any(kw in title_lower for kw in helpful):
            return 5
        
        # Visible, impressive features
        impressive = ["graphics", "gpu", "wasm", "gif", "benchmark"]
        if any(kw in title_lower for kw in impressive):
            return 4
        
        # Internal stuff newcomers don't care about
        internal = ["refactor", "cleanup", "internal", "mlir", "codegen"]
        if any(kw in title_lower for kw in internal):
            return 1
        
        return 3


class SystemsProgrammerAgent(Agent):
    """An experienced systems programmer evaluating Flow for real work."""
    
    name = "SystemsProgrammerAgent"
    weight = 1.2
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Systems programmers care about
        important = ["memory", "safety", "performance", "optimization", "simd", "ffi", "c"]
        if any(kw in title_lower for kw in important):
            return 5
        
        # Platform support matters
        platforms = ["windows", "linux", "cross-platform"]
        if any(kw in title_lower for kw in platforms):
            return 4
        
        # Compiler quality
        compiler = ["codegen", "type", "error", "debugger"]
        if any(kw in title_lower for kw in compiler):
            return 4
        
        return 2


class AudioEngineerAgent(Agent):
    """An audio/DSP engineer looking for a better tool than C++."""
    
    name = "AudioEngineerAgent"
    weight = 1.3  # Flow's target audience
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Audio-specific
        audio = ["audio", "dsp", "rt-safety", "real-time", "no-alloc", "buffer", "plugin"]
        if any(kw in title_lower for kw in audio):
            return 5
        
        # Performance matters for audio
        perf = ["simd", "optimization", "vectorization", "gpu"]
        if any(kw in title_lower for kw in perf):
            return 4
        
        # Safety matters
        safety = ["safety", "memory", "bounds", "crash"]
        if any(kw in title_lower for kw in safety):
            return 4
        
        return 2


class MLResearcherAgent(Agent):
    """An ML researcher comparing Flow to Mojo/Julia/JAX."""
    
    name = "MLResearcherAgent"
    weight = 1.1
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # ML-specific
        ml = ["autodiff", "tensor", "neural", "gpu", "cuda", "optimization"]
        if any(kw in title_lower for kw in ml):
            return 5
        
        # Performance for ML
        perf = ["vectorization", "simd", "parallel", "benchmark"]
        if any(kw in title_lower for kw in perf):
            return 4
        
        # Interop with Python ecosystem
        interop = ["python", "wasm", "ffi"]
        if any(kw in title_lower for kw in interop):
            return 4
        
        return 2


class GameDeveloperAgent(Agent):
    """A game developer looking for a modern systems language."""
    
    name = "GameDeveloperAgent"
    weight = 1.0
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Graphics and games
        games = ["graphics", "gpu", "metal", "vulkan", "simd", "demo", "tetris"]
        if any(kw in title_lower for kw in games):
            return 5
        
        # Platform support
        platforms = ["windows", "linux", "wasm", "cross-platform"]
        if any(kw in title_lower for kw in platforms):
            return 4
        
        # Performance
        perf = ["optimization", "vectorization", "performance"]
        if any(kw in title_lower for kw in perf):
            return 4
        
        return 2


class LanguageDesignerAgent(Agent):
    """A PL enthusiast interested in Flow's unique features."""
    
    name = "LanguageDesignerAgent"
    weight = 1.2
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Unique language features
        unique = ["effect", "capability", "autodiff", "temporal", "pattern", "match"]
        if any(kw in title_lower for kw in unique):
            return 5
        
        # Type system
        types = ["type", "generic", "trait", "closure", "exhaustive"]
        if any(kw in title_lower for kw in types):
            return 4
        
        # Self-hosting is the ultimate test
        if "self-hosting" in title_lower:
            return 5
        
        return 2


class OpenSourceMaintainerAgent(Agent):
    """Evaluates from a project health perspective."""
    
    name = "OpenSourceMaintainerAgent"
    weight = 0.9
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        category_lower = item.category.lower()
        
        # Project health
        health = ["ci", "test", "docs", "contributing", "cleanup", "refactor"]
        if any(kw in title_lower for kw in health):
            return 5
        
        # Community growth
        community = ["demo", "tutorial", "example", "playground"]
        if any(kw in title_lower for kw in community):
            return 4
        
        # Technical debt
        if "cleanup" in category_lower:
            return 5
        
        return 2


class VCInvestorAgent(Agent):
    """A VC evaluating Flow's market potential (tongue in cheek)."""
    
    name = "VCInvestorAgent"
    weight = 0.5  # Low weight - we're not optimizing for VCs
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Buzzwords VCs love
        buzzwords = ["gpu", "ml", "ai", "wasm", "cloud", "scale", "platform"]
        if any(kw in title_lower for kw in buzzwords):
            return 5
        
        # Competitive positioning
        competitive = ["benchmark", "comparison", "vs", "mojo", "julia"]
        if any(kw in title_lower for kw in competitive):
            return 5
        
        # Growth metrics
        growth = ["demo", "showcase", "community", "ecosystem"]
        if any(kw in title_lower for kw in growth):
            return 4
        
        return 2


class SkepticalEngineerAgent(Agent):
    """A skeptic who's seen too many 'revolutionary' languages fail."""
    
    name = "SkepticalEngineerAgent"
    weight = 1.0
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Skeptics want proof it works
        proof = ["benchmark", "test", "example", "demo", "real-world"]
        if any(kw in title_lower for kw in proof):
            return 5
        
        # Stability and reliability
        stable = ["fix", "bug", "error", "crash", "safety"]
        if any(kw in title_lower for kw in stable):
            return 5
        
        # Skeptical of hype
        hype = ["revolutionary", "breakthrough", "novel"]
        if any(kw in title_lower for kw in hype):
            return 1
        
        # Self-hosting proves it's real
        if "self-hosting" in title_lower:
            return 5
        
        return 3


class ProductManagerAgent(Agent):
    """A PM balancing user needs, business value, and engineering effort."""
    
    name = "ProductManagerAgent"
    weight = 1.1
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        category_lower = item.category.lower()
        
        # User-facing features
        user_facing = ["graphics", "demo", "playground", "debugger", "error message"]
        if any(kw in title_lower for kw in user_facing):
            return 5
        
        # Platform expansion = more users
        platforms = ["windows", "linux", "wasm"]
        if any(kw in title_lower for kw in platforms):
            return 4
        
        # Immediate priorities
        if "immediate" in category_lower:
            return 5
        if "short term" in category_lower:
            return 4
        
        # Internal work is lower priority
        internal = ["refactor", "cleanup", "internal"]
        if any(kw in title_lower for kw in internal):
            return 2
        
        return 3


class CompilerEngineerAgent(Agent):
    """A compiler engineer focused on correctness and performance."""
    
    name = "CompilerEngineerAgent"
    weight = 1.2
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Compiler work
        compiler = ["codegen", "parser", "type", "mlir", "llvm", "optimization"]
        if any(kw in title_lower for kw in compiler):
            return 5
        
        # Correctness
        correct = ["exhaustive", "pattern", "closure", "bug", "fix"]
        if any(kw in title_lower for kw in correct):
            return 4
        
        # Performance
        perf = ["vectorization", "inlining", "dead code", "constant"]
        if any(kw in title_lower for kw in perf):
            return 5
        
        return 2


class TechWriterAgent(Agent):
    """A technical writer focused on documentation quality."""
    
    name = "TechWriterAgent"
    weight = 0.7
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Documentation
        docs = ["doc", "tutorial", "guide", "example", "readme", "wiki"]
        if any(kw in title_lower for kw in docs):
            return 5
        
        # Things that need documenting
        features = ["demo", "showcase", "comparison"]
        if any(kw in title_lower for kw in features):
            return 4
        
        return 2


class SecurityEngineerAgent(Agent):
    """A security engineer focused on safety and correctness."""
    
    name = "SecurityEngineerAgent"
    weight = 1.3
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Security-relevant
        security = ["safety", "bounds", "memory", "crash", "injection", "sanitize"]
        if any(kw in title_lower for kw in security):
            return 5
        
        # Type safety
        types = ["type", "exhaustive", "strict"]
        if any(kw in title_lower for kw in types):
            return 4
        
        # Fuzzing and testing
        testing = ["fuzz", "test", "verify"]
        if any(kw in title_lower for kw in testing):
            return 5
        
        return 2


class DevOpsEngineerAgent(Agent):
    """A DevOps engineer focused on CI/CD and deployment."""
    
    name = "DevOpsEngineerAgent"
    weight = 0.8
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # CI/CD
        cicd = ["ci", "test", "build", "deploy", "wasm"]
        if any(kw in title_lower for kw in cicd):
            return 5
        
        # Cross-platform
        platforms = ["windows", "linux", "cross-platform"]
        if any(kw in title_lower for kw in platforms):
            return 4
        
        return 2


class EmbeddedDeveloperAgent(Agent):
    """An embedded systems developer with strict resource constraints."""
    
    name = "EmbeddedDeveloperAgent"
    weight = 0.9
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # Embedded concerns
        embedded = ["memory", "no-alloc", "safety", "rt-safety", "size"]
        if any(kw in title_lower for kw in embedded):
            return 5
        
        # Performance
        perf = ["optimization", "simd", "inline"]
        if any(kw in title_lower for kw in perf):
            return 4
        
        # C interop is crucial
        if "ffi" in title_lower or "c " in title_lower:
            return 5
        
        return 2


# Export all persona agents
PERSONA_AGENTS = [
    NewcomerDeveloperAgent,
    SystemsProgrammerAgent,
    AudioEngineerAgent,
    MLResearcherAgent,
    GameDeveloperAgent,
    LanguageDesignerAgent,
    OpenSourceMaintainerAgent,
    VCInvestorAgent,
    SkepticalEngineerAgent,
    ProductManagerAgent,
    CompilerEngineerAgent,
    TechWriterAgent,
    SecurityEngineerAgent,
    DevOpsEngineerAgent,
    EmbeddedDeveloperAgent,
]
