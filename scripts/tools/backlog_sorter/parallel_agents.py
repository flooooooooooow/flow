#!/usr/bin/env python3
"""
Parallel multi-agent backlog sorter with additional specialized agents.

This version runs agents in parallel using ThreadPoolExecutor and adds
more specialized agents for deeper analysis.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any
import json
import re
import time
from pathlib import Path

try:
    from backlog_sorter.agents import (
        BacklogItem, Agent, PriorityAgent, EffortAgent, 
        ImpactAgent, DependencyAgent, RiskAgent, parse_roadmap
    )
except ImportError:
    from agents import (
        BacklogItem, Agent, PriorityAgent, EffortAgent, 
        ImpactAgent, DependencyAgent, RiskAgent, parse_roadmap
    )


class CompilerFocusAgent(Agent):
    """Prioritizes compiler-related work for language maturity."""
    
    name = "CompilerFocusAgent"
    weight = 1.1
    
    COMPILER_KEYWORDS = [
        "codegen", "parser", "type", "mlir", "llvm", "optimization",
        "pattern", "closure", "exhaustiveness", "vectorization", "inlining"
    ]
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        matches = sum(1 for kw in self.COMPILER_KEYWORDS if kw in title_lower)
        
        if matches >= 2:
            return 5
        elif matches == 1:
            return 4
        elif "compiler" in item.category.lower() or "phase" in item.category.lower():
            return 3
        return 2


class UserExperienceAgent(Agent):
    """Prioritizes items that improve developer experience."""
    
    name = "UserExperienceAgent"
    weight = 1.2
    
    UX_KEYWORDS = [
        "demo", "docs", "tutorial", "error message", "debugger", 
        "lsp", "playground", "repl", "gif", "benchmark"
    ]
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        if any(kw in title_lower for kw in self.UX_KEYWORDS):
            return 5
        if "graphics" in title_lower or "visual" in title_lower:
            return 4
        return 2


class PlatformCoverageAgent(Agent):
    """Prioritizes cross-platform support."""
    
    name = "PlatformCoverageAgent"
    weight = 1.0
    
    PLATFORM_KEYWORDS = ["windows", "linux", "macos", "wasm", "web", "cross-platform"]
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        if any(kw in title_lower for kw in self.PLATFORM_KEYWORDS):
            return 5
        return 2


class TechnicalDebtAgent(Agent):
    """Prioritizes cleanup and refactoring work."""
    
    name = "TechnicalDebtAgent"
    weight = 0.6  # Lower weight - debt is important but not urgent
    
    DEBT_KEYWORDS = ["cleanup", "refactor", "structure", "flatten", "organize", "rename"]
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        category_lower = item.category.lower()
        
        if "cleanup" in category_lower:
            return 5
        if any(kw in title_lower for kw in self.DEBT_KEYWORDS):
            return 4
        return 2


class MarketingValueAgent(Agent):
    """Prioritizes items that help with positioning/marketing."""
    
    name = "MarketingValueAgent"
    weight = 0.9
    
    MARKETING_KEYWORDS = [
        "demo", "benchmark", "comparison", "showcase", "gif",
        "self-hosting", "real-world", "production"
    ]
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        if any(kw in title_lower for kw in self.MARKETING_KEYWORDS):
            return 5
        if "wasm" in title_lower or "gpu" in title_lower:
            return 4  # Impressive features
        return 2


class ParallelOrchestrator:
    """Runs agents in parallel and combines results."""
    
    def __init__(self, max_workers: int = 10):
        self.agents: list[Agent] = [
            # Core agents
            PriorityAgent(),
            EffortAgent(),
            ImpactAgent(),
            DependencyAgent(),
            RiskAgent(),
            # Extended agents
            CompilerFocusAgent(),
            UserExperienceAgent(),
            PlatformCoverageAgent(),
            TechnicalDebtAgent(),
            MarketingValueAgent(),
        ]
        self.max_workers = max_workers
    
    def _evaluate_single(self, agent: Agent, item: BacklogItem) -> tuple[str, int]:
        """Evaluate a single item with a single agent."""
        score = agent.evaluate(item)
        return (agent.name, score)
    
    def evaluate_item_parallel(self, item: BacklogItem) -> dict[str, int]:
        """Run all agents on an item in parallel."""
        scores = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._evaluate_single, agent, item): agent
                for agent in self.agents
            }
            
            for future in as_completed(futures):
                agent_name, score = future.result()
                scores[agent_name] = score
        
        return scores
    
    def compute_final_score(self, scores: dict[str, int]) -> float:
        """Compute weighted average from all agent scores."""
        total_weight = sum(a.weight for a in self.agents)
        weighted_sum = sum(
            scores.get(a.name, 3) * a.weight 
            for a in self.agents
        )
        return weighted_sum / total_weight
    
    def sort_backlog(self, items: list[BacklogItem]) -> list[BacklogItem]:
        """Evaluate and sort all items using parallel agents."""
        print(f"   Running {len(self.agents)} agents on {len(items)} items...")
        
        start_time = time.time()
        
        for item in items:
            scores = self.evaluate_item_parallel(item)
            
            # Store individual scores
            item.priority_score = scores.get("PriorityAgent", 3)
            item.effort_score = scores.get("EffortAgent", 3)
            item.impact_score = scores.get("ImpactAgent", 3)
            item.dependency_score = scores.get("DependencyAgent", 3)
            item.risk_score = scores.get("RiskAgent", 3)
            
            # Store extended scores in tags for reporting
            item.tags = [
                f"compiler:{scores.get('CompilerFocusAgent', 3)}",
                f"ux:{scores.get('UserExperienceAgent', 3)}",
                f"platform:{scores.get('PlatformCoverageAgent', 3)}",
                f"debt:{scores.get('TechnicalDebtAgent', 3)}",
                f"marketing:{scores.get('MarketingValueAgent', 3)}",
            ]
            
            item.final_score = self.compute_final_score(scores)
        
        elapsed = time.time() - start_time
        print(f"   Completed in {elapsed:.2f}s")
        
        sorted_items = sorted(items, key=lambda x: x.final_score, reverse=True)
        
        for i, item in enumerate(sorted_items, 1):
            item.rank = i
        
        return sorted_items
    
    def generate_detailed_report(self, items: list[BacklogItem]) -> str:
        """Generate a comprehensive markdown report."""
        lines = [
            "# Backlog Priority Report (Parallel Multi-Agent)",
            "",
            f"> Generated by **{len(self.agents)} agents** running in parallel",
            "",
            "## Agent Configuration",
            "",
            "| Agent | Weight | Purpose |",
            "|-------|--------|---------|",
        ]
        
        purposes = {
            "PriorityAgent": "Urgency & strategic importance",
            "EffortAgent": "Implementation complexity (inverted)",
            "ImpactAgent": "User value & ecosystem benefit",
            "DependencyAgent": "Blockers & prerequisites",
            "RiskAgent": "Technical risk (inverted)",
            "CompilerFocusAgent": "Language/compiler maturity",
            "UserExperienceAgent": "Developer experience",
            "PlatformCoverageAgent": "Cross-platform support",
            "TechnicalDebtAgent": "Code health & cleanup",
            "MarketingValueAgent": "Positioning & showcasing",
        }
        
        for agent in self.agents:
            lines.append(f"| {agent.name} | {agent.weight:.1f} | {purposes.get(agent.name, '')} |")
        
        lines.extend([
            "",
            "---",
            "",
            "## Full Ranked Backlog",
            "",
            "| Rank | Task | Category | Final | Core Scores | Extended Scores |",
            "|------|------|----------|-------|-------------|-----------------|",
        ])
        
        for item in items:
            core = f"P:{item.priority_score} E:{item.effort_score} I:{item.impact_score} D:{item.dependency_score} R:{item.risk_score}"
            extended = " ".join(item.tags)
            lines.append(
                f"| {item.rank} | {item.title} | {item.category} | "
                f"**{item.final_score:.2f}** | {core} | {extended} |"
            )
        
        lines.extend([
            "",
            "---",
            "",
            "## Recommendations",
            "",
            "### 🎯 Sprint Focus (Top 5)",
            "",
        ])
        
        for item in items[:5]:
            lines.append(f"1. **{item.title}** — Score: {item.final_score:.2f}")
            lines.append(f"   - Category: {item.category}")
            lines.append(f"   - Core: P={item.priority_score} E={item.effort_score} I={item.impact_score}")
            lines.append("")
        
        # Quick wins
        quick_wins = [i for i in items if i.effort_score >= 4 and i.impact_score >= 3]
        if quick_wins:
            lines.extend([
                "### ⚡ Quick Wins (High Impact, Low Effort)",
                "",
            ])
            for item in quick_wins[:5]:
                lines.append(f"- {item.title} (effort: {item.effort_score}, impact: {item.impact_score})")
        
        # Platform items
        platform_items = [i for i in items if "platform:" in str(i.tags) and "platform:5" in str(i.tags)]
        if platform_items:
            lines.extend([
                "",
                "### 🌐 Platform Coverage",
                "",
            ])
            for item in platform_items[:5]:
                lines.append(f"- {item.title}")
        
        # Compiler items
        compiler_items = [i for i in items if "compiler:5" in str(i.tags) or "compiler:4" in str(i.tags)]
        if compiler_items:
            lines.extend([
                "",
                "### 🔧 Compiler Maturity",
                "",
            ])
            for item in compiler_items[:5]:
                lines.append(f"- {item.title}")
        
        # Technical debt
        debt_items = [i for i in items if "debt:5" in str(i.tags) or "debt:4" in str(i.tags)]
        if debt_items:
            lines.extend([
                "",
                "### 🧹 Technical Debt",
                "",
            ])
            for item in debt_items[:5]:
                lines.append(f"- {item.title}")
        
        lines.extend([
            "",
            "---",
            "",
            "## Score Distribution",
            "",
            "```",
            "Score Range | Count",
            "------------|------",
        ])
        
        ranges = [(4.0, 5.0), (3.5, 4.0), (3.0, 3.5), (2.5, 3.0), (0, 2.5)]
        for low, high in ranges:
            count = sum(1 for i in items if low <= i.final_score < high)
            bar = "█" * count
            lines.append(f"{low:.1f}-{high:.1f}    | {count:2d} {bar}")
        
        lines.append("```")
        
        return "\n".join(lines)


def main():
    """Run the parallel backlog sorter."""
    import sys
    
    script_dir = Path(__file__).parent
    roadmap_path = script_dir.parent.parent.parent / "docs/project/ROADMAP.md"
    
    if not roadmap_path.exists():
        print(f"Error: ROADMAP.md not found at {roadmap_path}")
        sys.exit(1)
    
    print(f"📋 Parsing {roadmap_path}...")
    items = parse_roadmap(roadmap_path)
    print(f"   Found {len(items)} pending items")
    
    print("\n🤖 Running parallel agent evaluation...")
    orchestrator = ParallelOrchestrator(max_workers=10)
    sorted_items = orchestrator.sort_backlog(items)
    
    print("\n📊 Generating detailed report...")
    report = orchestrator.generate_detailed_report(sorted_items)
    
    output_path = script_dir / "BACKLOG_SORTED_DETAILED.md"
    output_path.write_text(report)
    print(f"   Written to {output_path}")
    
    json_path = script_dir / "backlog_sorted_detailed.json"
    json_data = [item.to_dict() for item in sorted_items]
    json_path.write_text(json.dumps(json_data, indent=2))
    print(f"   JSON written to {json_path}")
    
    print("\n" + "=" * 60)
    print("TOP 5 PRIORITIES (10-Agent Consensus)")
    print("=" * 60)
    for item in sorted_items[:5]:
        print(f"  {item.rank}. {item.title}")
        print(f"     Score: {item.final_score:.2f} | Category: {item.category}")
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
