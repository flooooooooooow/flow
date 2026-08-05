#!/usr/bin/env python3
"""
Multi-agent backlog sorter for Flow ROADMAP.md

Each agent evaluates tasks from a different perspective:
- PriorityAgent: Urgency and strategic importance
- EffortAgent: Implementation complexity and time
- ImpactAgent: User value and ecosystem benefit
- DependencyAgent: Blockers and prerequisites
- RiskAgent: Technical risk and uncertainty

The orchestrator combines all agent scores to produce a final ranking.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable
import json
import re
from pathlib import Path


class Priority(Enum):
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    NICE_TO_HAVE = 1


class Effort(Enum):
    TRIVIAL = 1      # < 1 day
    SMALL = 2        # 1-3 days
    MEDIUM = 3       # 1 week
    LARGE = 4        # 2-4 weeks
    EPIC = 5         # > 1 month


class Impact(Enum):
    TRANSFORMATIVE = 5   # Changes how people use Flow
    HIGH = 4             # Major feature or fix
    MEDIUM = 3           # Useful improvement
    LOW = 2              # Minor enhancement
    MINIMAL = 1          # Cosmetic or internal


@dataclass
class BacklogItem:
    id: str
    title: str
    category: str
    description: str = ""
    status: str = "pending"
    tags: list[str] = field(default_factory=list)
    
    # Agent scores (filled by agents)
    priority_score: int = 0
    effort_score: int = 0
    impact_score: int = 0
    dependency_score: int = 0
    risk_score: int = 0
    
    # Computed
    final_score: float = 0.0
    rank: int = 0
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "description": self.description,
            "status": self.status,
            "tags": self.tags,
            "scores": {
                "priority": self.priority_score,
                "effort": self.effort_score,
                "impact": self.impact_score,
                "dependency": self.dependency_score,
                "risk": self.risk_score,
                "final": self.final_score,
            },
            "rank": self.rank,
        }


class Agent:
    """Base agent class."""
    
    name: str = "BaseAgent"
    weight: float = 1.0
    
    def evaluate(self, item: BacklogItem) -> int:
        """Return a score from 1-5."""
        raise NotImplementedError
    
    def explain(self, item: BacklogItem) -> str:
        """Return reasoning for the score."""
        return ""


class PriorityAgent(Agent):
    """Evaluates urgency and strategic importance."""
    
    name = "PriorityAgent"
    weight = 1.5  # Priority matters most
    
    # Keywords that indicate high priority
    CRITICAL_KEYWORDS = ["security", "crash", "broken", "critical", "blocker"]
    HIGH_KEYWORDS = ["bug", "fix", "error", "fail", "missing"]
    STRATEGIC_KEYWORDS = ["windows", "linux", "wasm", "gpu", "self-hosting"]
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        desc_lower = item.description.lower()
        combined = f"{title_lower} {desc_lower}"
        
        # Check for critical issues
        if any(kw in combined for kw in self.CRITICAL_KEYWORDS):
            return 5
        
        # Check for high priority
        if any(kw in combined for kw in self.HIGH_KEYWORDS):
            return 4
        
        # Strategic importance
        if any(kw in combined for kw in self.STRATEGIC_KEYWORDS):
            return 4
        
        # Category-based priority
        category_priority = {
            "Immediate": 5,
            "Short Term": 4,
            "Medium Term": 3,
            "Phase 2": 3,
            "Phase 4": 2,
            "Cleanup": 2,
            "Next": 3,
        }
        
        return category_priority.get(item.category, 3)


class EffortAgent(Agent):
    """Evaluates implementation complexity."""
    
    name = "EffortAgent"
    weight = 0.8  # Lower weight - we want high-impact items even if hard
    
    # Keywords indicating effort levels
    TRIVIAL_KEYWORDS = ["demo", "gif", "rename", "move", "cleanup"]
    SMALL_KEYWORDS = ["fix", "update", "add", "simple"]
    LARGE_KEYWORDS = ["system", "framework", "backend", "compiler"]
    EPIC_KEYWORDS = ["self-hosting", "gpu", "wasm", "windows"]
    
    def evaluate(self, item: BacklogItem) -> int:
        """Returns inverted effort (5 = easy, 1 = hard) for ranking."""
        title_lower = item.title.lower()
        
        if any(kw in title_lower for kw in self.TRIVIAL_KEYWORDS):
            return 5  # Easy = high score
        if any(kw in title_lower for kw in self.EPIC_KEYWORDS):
            return 1  # Hard = low score
        if any(kw in title_lower for kw in self.LARGE_KEYWORDS):
            return 2
        if any(kw in title_lower for kw in self.SMALL_KEYWORDS):
            return 4
        
        return 3  # Medium effort


class ImpactAgent(Agent):
    """Evaluates user value and ecosystem benefit."""
    
    name = "ImpactAgent"
    weight = 1.3
    
    # High impact keywords
    TRANSFORMATIVE = ["self-hosting", "wasm", "gpu autodiff"]
    HIGH_IMPACT = ["windows", "linux", "graphics", "async", "debugger"]
    MEDIUM_IMPACT = ["pattern", "closure", "optimization"]
    LOW_IMPACT = ["cleanup", "structure", "rename"]
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        if any(kw in title_lower for kw in self.TRANSFORMATIVE):
            return 5
        if any(kw in title_lower for kw in self.HIGH_IMPACT):
            return 4
        if any(kw in title_lower for kw in self.LOW_IMPACT):
            return 2
        if any(kw in title_lower for kw in self.MEDIUM_IMPACT):
            return 3
        
        return 3


class DependencyAgent(Agent):
    """Evaluates blockers and prerequisites."""
    
    name = "DependencyAgent"
    weight = 1.0
    
    # Items that are prerequisites for others
    ENABLES_OTHERS = {
        "pattern matching": ["exhaustiveness", "guards", "nested"],
        "wasm": ["playground", "web"],
        "windows graphics": ["full platform"],
        "codegen": ["examples", "demos"],
    }
    
    # Items that depend on others
    BLOCKED_BY = {
        "exhaustiveness": "pattern matching",
        "nested patterns": "pattern matching",
        "match guards": "pattern matching",
        "gpu autodiff": "gpu codegen",
    }
    
    def evaluate(self, item: BacklogItem) -> int:
        title_lower = item.title.lower()
        
        # High score if this enables other work
        for enabler, dependents in self.ENABLES_OTHERS.items():
            if enabler in title_lower:
                return 5
        
        # Lower score if blocked by something else
        for blocked, blocker in self.BLOCKED_BY.items():
            if blocked in title_lower:
                return 2
        
        # Check if it's a standalone item (good for parallelization)
        standalone_keywords = ["demo", "benchmark", "cleanup", "docs"]
        if any(kw in title_lower for kw in standalone_keywords):
            return 4
        
        return 3


class RiskAgent(Agent):
    """Evaluates technical risk and uncertainty."""
    
    name = "RiskAgent"
    weight = 0.7  # Lower weight - some risk is acceptable
    
    HIGH_RISK = ["self-hosting", "gpu", "wasm", "async"]
    MEDIUM_RISK = ["windows", "optimization", "vectorization"]
    LOW_RISK = ["demo", "cleanup", "docs", "benchmark", "gif"]
    
    def evaluate(self, item: BacklogItem) -> int:
        """Returns inverted risk (5 = low risk, 1 = high risk)."""
        title_lower = item.title.lower()
        
        if any(kw in title_lower for kw in self.LOW_RISK):
            return 5
        if any(kw in title_lower for kw in self.HIGH_RISK):
            return 1
        if any(kw in title_lower for kw in self.MEDIUM_RISK):
            return 3
        
        return 3


class Orchestrator:
    """Coordinates all agents and produces final ranking."""
    
    def __init__(self):
        self.agents: list[Agent] = [
            PriorityAgent(),
            EffortAgent(),
            ImpactAgent(),
            DependencyAgent(),
            RiskAgent(),
        ]
    
    def evaluate_item(self, item: BacklogItem) -> BacklogItem:
        """Run all agents on an item and compute final score."""
        item.priority_score = self.agents[0].evaluate(item)
        item.effort_score = self.agents[1].evaluate(item)
        item.impact_score = self.agents[2].evaluate(item)
        item.dependency_score = self.agents[3].evaluate(item)
        item.risk_score = self.agents[4].evaluate(item)
        
        # Weighted average
        total_weight = sum(a.weight for a in self.agents)
        weighted_sum = (
            item.priority_score * self.agents[0].weight +
            item.effort_score * self.agents[1].weight +
            item.impact_score * self.agents[2].weight +
            item.dependency_score * self.agents[3].weight +
            item.risk_score * self.agents[4].weight
        )
        item.final_score = weighted_sum / total_weight
        
        return item
    
    def sort_backlog(self, items: list[BacklogItem]) -> list[BacklogItem]:
        """Evaluate and sort all items."""
        evaluated = [self.evaluate_item(item) for item in items]
        sorted_items = sorted(evaluated, key=lambda x: x.final_score, reverse=True)
        
        for i, item in enumerate(sorted_items, 1):
            item.rank = i
        
        return sorted_items
    
    def generate_report(self, items: list[BacklogItem]) -> str:
        """Generate a markdown report of sorted items."""
        lines = [
            "# Backlog Priority Report",
            "",
            f"> Generated by {len(self.agents)} agents",
            "",
            "## Agent Weights",
            "",
            "| Agent | Weight | Focus |",
            "|-------|--------|-------|",
        ]
        
        focus_map = {
            "PriorityAgent": "Urgency & strategic importance",
            "EffortAgent": "Implementation complexity (inverted)",
            "ImpactAgent": "User value & ecosystem benefit",
            "DependencyAgent": "Blockers & prerequisites",
            "RiskAgent": "Technical risk (inverted)",
        }
        
        for agent in self.agents:
            lines.append(f"| {agent.name} | {agent.weight} | {focus_map.get(agent.name, '')} |")
        
        lines.extend([
            "",
            "## Sorted Backlog",
            "",
            "| Rank | Task | Category | Score | P | E | I | D | R |",
            "|------|------|----------|-------|---|---|---|---|---|",
        ])
        
        for item in items:
            lines.append(
                f"| {item.rank} | {item.title} | {item.category} | "
                f"{item.final_score:.2f} | {item.priority_score} | {item.effort_score} | "
                f"{item.impact_score} | {item.dependency_score} | {item.risk_score} |"
            )
        
        lines.extend([
            "",
            "### Legend",
            "- **P**: Priority (5=critical, 1=nice-to-have)",
            "- **E**: Effort (5=trivial, 1=epic) — inverted so easy tasks score higher",
            "- **I**: Impact (5=transformative, 1=minimal)",
            "- **D**: Dependency (5=enables others, 1=blocked)",
            "- **R**: Risk (5=low risk, 1=high risk) — inverted so safe tasks score higher",
            "",
            "## Recommended Sprint",
            "",
            "Top 5 items for immediate focus:",
            "",
        ])
        
        for item in items[:5]:
            lines.append(f"1. **{item.title}** ({item.category}) — Score: {item.final_score:.2f}")
        
        lines.extend([
            "",
            "## Quick Wins",
            "",
            "High impact, low effort items:",
            "",
        ])
        
        quick_wins = [i for i in items if i.effort_score >= 4 and i.impact_score >= 3]
        for item in quick_wins[:5]:
            lines.append(f"- {item.title}")
        
        return "\n".join(lines)


def parse_roadmap(roadmap_path: Path) -> list[BacklogItem]:
    """Extract pending items from ROADMAP.md."""
    content = roadmap_path.read_text()
    items = []
    
    # Pattern for pending items: 🔲 or [ ] or - [ ]
    pending_patterns = [
        r"\| ([^|]+) \| 🔲 \|",  # Table format with 🔲
        r"- \[ \] (.+)",         # Checkbox format
    ]
    
    current_category = "Uncategorized"
    item_id = 0
    
    for line in content.split("\n"):
        # Track category from headers
        if line.startswith("### "):
            current_category = line[4:].strip()
            # Clean up category name
            current_category = re.sub(r"[🎯📅🧹🔮]", "", current_category).strip()
        elif line.startswith("## "):
            section = line[3:].strip()
            if "Immediate" in section:
                current_category = "Immediate"
            elif "Short Term" in section:
                current_category = "Short Term"
            elif "Medium Term" in section:
                current_category = "Medium Term"
        
        # Extract pending items
        for pattern in pending_patterns:
            match = re.search(pattern, line)
            if match:
                title = match.group(1).strip()
                # Skip if it's just a header or empty
                if title and not title.startswith("#"):
                    item_id += 1
                    items.append(BacklogItem(
                        id=f"item-{item_id:03d}",
                        title=title,
                        category=current_category,
                    ))
    
    # Also extract from the "What's Next?" section
    next_section = content.split("## What's Next?")
    if len(next_section) > 1:
        for line in next_section[1].split("\n"):
            if "🔲" in line:
                # Extract the task name
                match = re.search(r"\*\*([^*]+)\*\*", line)
                if match:
                    title = match.group(1).strip()
                    item_id += 1
                    items.append(BacklogItem(
                        id=f"item-{item_id:03d}",
                        title=title,
                        category="Next",
                    ))
    
    return items


def main():
    """Run the backlog sorter."""
    import sys
    
    # Find ROADMAP.md
    script_dir = Path(__file__).parent
    roadmap_path = script_dir.parent.parent.parent / "docs/project/ROADMAP.md"
    
    if not roadmap_path.exists():
        print(f"Error: ROADMAP.md not found at {roadmap_path}")
        sys.exit(1)
    
    print(f"📋 Parsing {roadmap_path}...")
    items = parse_roadmap(roadmap_path)
    print(f"   Found {len(items)} pending items")
    
    print("\n🤖 Running agent evaluation...")
    orchestrator = Orchestrator()
    sorted_items = orchestrator.sort_backlog(items)
    
    print("\n📊 Generating report...")
    report = orchestrator.generate_report(sorted_items)
    
    # Write report
    output_path = script_dir / "BACKLOG_SORTED.md"
    output_path.write_text(report)
    print(f"   Written to {output_path}")
    
    # Also write JSON for programmatic access
    json_path = script_dir / "backlog_sorted.json"
    json_data = [item.to_dict() for item in sorted_items]
    json_path.write_text(json.dumps(json_data, indent=2))
    print(f"   JSON written to {json_path}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("TOP 5 PRIORITIES")
    print("=" * 60)
    for item in sorted_items[:5]:
        print(f"  {item.rank}. {item.title} (score: {item.final_score:.2f})")
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
