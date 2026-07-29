#!/usr/bin/env python3
"""
ULTRA ORCHESTRATOR - 40 agents running in parallel!

The ultimate backlog sorting system combining:
- 5 core agents
- 5 extended agents
- 15 specialized agents
- 15 persona agents

Total: 40 agents providing comprehensive multi-perspective prioritization.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any
import json
import time
from pathlib import Path
from collections import defaultdict

try:
    from backlog_sorter.agents import (
        BacklogItem, Agent, PriorityAgent, EffortAgent,
        ImpactAgent, DependencyAgent, RiskAgent, parse_roadmap
    )
    from backlog_sorter.parallel_agents import (
        CompilerFocusAgent, UserExperienceAgent, PlatformCoverageAgent,
        TechnicalDebtAgent, MarketingValueAgent
    )
    from backlog_sorter.specialized_agents import SPECIALIZED_AGENTS
    from backlog_sorter.persona_agents import PERSONA_AGENTS
except ImportError:
    from agents import (
        BacklogItem, Agent, PriorityAgent, EffortAgent,
        ImpactAgent, DependencyAgent, RiskAgent, parse_roadmap
    )
    from parallel_agents import (
        CompilerFocusAgent, UserExperienceAgent, PlatformCoverageAgent,
        TechnicalDebtAgent, MarketingValueAgent
    )
    from specialized_agents import SPECIALIZED_AGENTS
    from persona_agents import PERSONA_AGENTS


@dataclass
class UltraVote:
    """A single agent's vote with full context."""
    agent_name: str
    agent_type: str  # core, extended, specialized, persona
    score: int
    weight: float
    reasoning: str = ""


@dataclass
class UltraResult:
    """Comprehensive result from all 40 agents."""
    item: BacklogItem
    votes: list[UltraVote]
    
    # Final scores
    final_score: float = 0.0
    rank: int = 0
    
    # Category breakdowns
    core_score: float = 0.0
    extended_score: float = 0.0
    specialized_score: float = 0.0
    persona_score: float = 0.0
    
    # Analysis
    confidence: float = 0.0
    consensus_level: str = ""  # strong, moderate, weak, controversial
    top_supporters: list[str] = field(default_factory=list)
    top_detractors: list[str] = field(default_factory=list)
    
    # Persona insights
    persona_breakdown: dict = field(default_factory=dict)


class UltraOrchestrator:
    """Coordinates 40 agents for ultimate backlog analysis."""
    
    def __init__(self, max_workers: int = 40):
        # Core agents (5)
        self.core_agents = [
            PriorityAgent(),
            EffortAgent(),
            ImpactAgent(),
            DependencyAgent(),
            RiskAgent(),
        ]
        
        # Extended agents (5)
        self.extended_agents = [
            CompilerFocusAgent(),
            UserExperienceAgent(),
            PlatformCoverageAgent(),
            TechnicalDebtAgent(),
            MarketingValueAgent(),
        ]
        
        # Specialized agents (15)
        self.specialized_agents = [cls() for cls in SPECIALIZED_AGENTS]
        
        # Persona agents (15)
        self.persona_agents = [cls() for cls in PERSONA_AGENTS]
        
        # All agents
        self.all_agents = (
            self.core_agents +
            self.extended_agents +
            self.specialized_agents +
            self.persona_agents
        )
        
        self.max_workers = max_workers
        
        print("=" * 70)
        print("🚀 ULTRA ORCHESTRATOR INITIALIZED")
        print("=" * 70)
        print(f"   Total agents: {len(self.all_agents)}")
        print(f"   - Core:        {len(self.core_agents)}")
        print(f"   - Extended:    {len(self.extended_agents)}")
        print(f"   - Specialized: {len(self.specialized_agents)}")
        print(f"   - Persona:     {len(self.persona_agents)}")
        print("=" * 70)
    
    def _get_agent_type(self, agent: Agent) -> str:
        if agent in self.core_agents:
            return "core"
        elif agent in self.extended_agents:
            return "extended"
        elif agent in self.specialized_agents:
            return "specialized"
        else:
            return "persona"
    
    def _evaluate_single(self, agent: Agent, item: BacklogItem) -> UltraVote:
        score = agent.evaluate(item)
        return UltraVote(
            agent_name=agent.name,
            agent_type=self._get_agent_type(agent),
            score=score,
            weight=agent.weight,
        )
    
    def evaluate_item(self, item: BacklogItem) -> UltraResult:
        """Run all 40 agents on an item."""
        votes = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._evaluate_single, agent, item): agent
                for agent in self.all_agents
            }
            
            for future in as_completed(futures):
                vote = future.result()
                votes.append(vote)
        
        # Calculate scores by type
        def weighted_avg(vote_list):
            if not vote_list:
                return 0.0
            total_weight = sum(v.weight for v in vote_list)
            return sum(v.score * v.weight for v in vote_list) / total_weight
        
        core_votes = [v for v in votes if v.agent_type == "core"]
        extended_votes = [v for v in votes if v.agent_type == "extended"]
        specialized_votes = [v for v in votes if v.agent_type == "specialized"]
        persona_votes = [v for v in votes if v.agent_type == "persona"]
        
        core_score = weighted_avg(core_votes)
        extended_score = weighted_avg(extended_votes)
        specialized_score = weighted_avg(specialized_votes)
        persona_score = weighted_avg(persona_votes)
        
        # Final score: weighted combination
        # Core: 30%, Extended: 20%, Specialized: 25%, Persona: 25%
        final_score = (
            core_score * 0.30 +
            extended_score * 0.20 +
            specialized_score * 0.25 +
            persona_score * 0.25
        )
        
        # Calculate confidence
        scores = [v.score for v in votes]
        mean_score = sum(scores) / len(scores)
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        std_dev = variance ** 0.5
        confidence = max(0, 1 - (std_dev / 2))
        
        # Consensus level
        if std_dev < 0.8:
            consensus_level = "strong"
        elif std_dev < 1.2:
            consensus_level = "moderate"
        elif std_dev < 1.6:
            consensus_level = "weak"
        else:
            consensus_level = "controversial"
        
        # Top supporters and detractors
        sorted_votes = sorted(votes, key=lambda v: v.score * v.weight, reverse=True)
        top_supporters = [v.agent_name for v in sorted_votes[:3]]
        top_detractors = [v.agent_name for v in sorted_votes[-3:]]
        
        # Persona breakdown
        persona_breakdown = {v.agent_name: v.score for v in persona_votes}
        
        return UltraResult(
            item=item,
            votes=votes,
            final_score=final_score,
            core_score=core_score,
            extended_score=extended_score,
            specialized_score=specialized_score,
            persona_score=persona_score,
            confidence=confidence,
            consensus_level=consensus_level,
            top_supporters=top_supporters,
            top_detractors=top_detractors,
            persona_breakdown=persona_breakdown,
        )
    
    def sort_backlog(self, items: list[BacklogItem]) -> list[UltraResult]:
        """Evaluate and sort all items with 40 agents."""
        total_evals = len(self.all_agents) * len(items)
        print(f"\n⚡ Running {len(self.all_agents)} agents on {len(items)} items...")
        print(f"   Total evaluations: {total_evals}")
        
        start_time = time.time()
        
        results = []
        for i, item in enumerate(items, 1):
            result = self.evaluate_item(item)
            results.append(result)
            
            # Progress
            pct = (i / len(items)) * 100
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            print(f"\r   [{bar}] {pct:.0f}% ({i}/{len(items)})", end="", flush=True)
        
        print()  # Newline after progress bar
        
        elapsed = time.time() - start_time
        print(f"   Completed in {elapsed:.2f}s ({total_evals / elapsed:.0f} evals/sec)")
        
        # Sort
        sorted_results = sorted(results, key=lambda r: r.final_score, reverse=True)
        for i, result in enumerate(sorted_results, 1):
            result.rank = i
        
        return sorted_results
    
    def generate_ultra_report(self, results: list[UltraResult]) -> str:
        """Generate the ultimate markdown report."""
        lines = [
            "# 🔥 ULTRA Backlog Priority Report",
            "",
            f"> **{len(self.all_agents)} agents** analyzed **{len(results)} items**",
            "> with **{} total evaluations**".format(len(self.all_agents) * len(results)),
            "",
            "## 🤖 Agent Army Overview",
            "",
            "| Category | Count | Weight Share | Purpose |",
            "|----------|-------|--------------|---------|",
            f"| Core | {len(self.core_agents)} | 30% | Fundamental prioritization |",
            f"| Extended | {len(self.extended_agents)} | 20% | Technical analysis |",
            f"| Specialized | {len(self.specialized_agents)} | 25% | Domain expertise |",
            f"| Persona | {len(self.persona_agents)} | 25% | Stakeholder perspectives |",
            "",
            "---",
            "",
            "## 🏆 Final Rankings",
            "",
        ]
        
        # Emoji for consensus
        consensus_emoji = {
            "strong": "🟢",
            "moderate": "🟡",
            "weak": "🟠",
            "controversial": "🔴",
        }
        
        lines.extend([
            "| Rank | Task | Score | Consensus | Core | Ext | Spec | Persona |",
            "|------|------|-------|-----------|------|-----|------|---------|",
        ])
        
        for r in results:
            emoji = consensus_emoji.get(r.consensus_level, "⚪")
            lines.append(
                f"| {r.rank} | {r.item.title} | **{r.final_score:.2f}** | "
                f"{emoji} {r.consensus_level} | {r.core_score:.1f} | "
                f"{r.extended_score:.1f} | {r.specialized_score:.1f} | "
                f"{r.persona_score:.1f} |"
            )
        
        lines.extend([
            "",
            "---",
            "",
            "## 🎯 Sprint Recommendations",
            "",
            "### Top 5 Priorities",
            "",
        ])
        
        for r in results[:5]:
            emoji = consensus_emoji.get(r.consensus_level, "⚪")
            lines.append(f"#### {r.rank}. {r.item.title}")
            lines.append(f"")
            lines.append(f"- **Score:** {r.final_score:.2f}")
            lines.append(f"- **Consensus:** {emoji} {r.consensus_level} ({r.confidence:.0%} confidence)")
            lines.append(f"- **Top supporters:** {', '.join(r.top_supporters)}")
            lines.append(f"- **Category:** {r.item.category}")
            lines.append("")
        
        # Persona insights
        lines.extend([
            "---",
            "",
            "## 👥 Persona Insights",
            "",
            "How different stakeholders view the top items:",
            "",
        ])
        
        for r in results[:5]:
            lines.append(f"### {r.item.title}")
            lines.append("")
            lines.append("| Persona | Score | Verdict |")
            lines.append("|---------|-------|---------|")
            
            for persona, score in sorted(r.persona_breakdown.items(), key=lambda x: x[1], reverse=True):
                verdict = "👍 Loves it" if score >= 4 else "👌 Okay" if score >= 3 else "👎 Meh"
                lines.append(f"| {persona.replace('Agent', '')} | {score} | {verdict} |")
            
            lines.append("")
        
        # Consensus analysis
        strong_consensus = [r for r in results if r.consensus_level == "strong"]
        controversial = [r for r in results if r.consensus_level == "controversial"]
        
        if strong_consensus:
            lines.extend([
                "---",
                "",
                "## 🟢 Strong Consensus Items",
                "",
                "All 40 agents agree on these:",
                "",
            ])
            for r in strong_consensus[:5]:
                lines.append(f"- {r.item.title} (score: {r.final_score:.2f})")
        
        if controversial:
            lines.extend([
                "",
                "## 🔴 Controversial Items",
                "",
                "Agents disagree significantly - needs human judgment:",
                "",
            ])
            for r in controversial:
                lines.append(f"- **{r.item.title}**")
                lines.append(f"  - Supporters: {', '.join(r.top_supporters)}")
                lines.append(f"  - Detractors: {', '.join(r.top_detractors)}")
        
        # Score distribution
        lines.extend([
            "",
            "---",
            "",
            "## 📊 Score Distribution",
            "",
            "```",
        ])
        
        ranges = [(4.0, 5.0), (3.5, 4.0), (3.0, 3.5), (2.5, 3.0), (2.0, 2.5), (0, 2.0)]
        max_count = max(sum(1 for r in results if low <= r.final_score < high) for low, high in ranges)
        
        for low, high in ranges:
            count = sum(1 for r in results if low <= r.final_score < high)
            bar_len = int((count / max(max_count, 1)) * 20)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            lines.append(f"{low:.1f}-{high:.1f} | {bar} {count}")
        
        lines.extend([
            "```",
            "",
            "---",
            "",
            "## 🔍 Agent Influence Analysis",
            "",
        ])
        
        # Calculate agent influence
        agent_scores = defaultdict(list)
        for r in results:
            for v in r.votes:
                agent_scores[v.agent_name].append(v.score * v.weight)
        
        avg_influence = {
            name: sum(scores) / len(scores)
            for name, scores in agent_scores.items()
        }
        
        sorted_influence = sorted(avg_influence.items(), key=lambda x: x[1], reverse=True)
        
        lines.extend([
            "### Most Influential Agents",
            "",
            "| Rank | Agent | Avg Weighted Score |",
            "|------|-------|-------------------|",
        ])
        
        for i, (name, score) in enumerate(sorted_influence[:10], 1):
            lines.append(f"| {i} | {name} | {score:.2f} |")
        
        lines.extend([
            "",
            "### Least Influential Agents",
            "",
            "| Rank | Agent | Avg Weighted Score |",
            "|------|-------|-------------------|",
        ])
        
        for i, (name, score) in enumerate(sorted_influence[-5:], 1):
            lines.append(f"| {i} | {name} | {score:.2f} |")
        
        lines.extend([
            "",
            "---",
            "",
            f"*Generated by UltraOrchestrator with {len(self.all_agents)} agents*",
        ])
        
        return "\n".join(lines)


def main():
    """Run the ultra orchestrator."""
    import sys
    
    script_dir = Path(__file__).parent
    roadmap_path = script_dir.parent.parent / "ROADMAP.md"
    
    if not roadmap_path.exists():
        print(f"Error: ROADMAP.md not found at {roadmap_path}")
        sys.exit(1)
    
    print(f"📋 Parsing {roadmap_path}...")
    items = parse_roadmap(roadmap_path)
    print(f"   Found {len(items)} pending items")
    
    orchestrator = UltraOrchestrator(max_workers=40)
    results = orchestrator.sort_backlog(items)
    
    print("\n📊 Generating ultra report...")
    report = orchestrator.generate_ultra_report(results)
    
    output_path = script_dir / "BACKLOG_ULTRA_SORTED.md"
    output_path.write_text(report)
    print(f"   Written to {output_path}")
    
    # JSON
    json_path = script_dir / "backlog_ultra_sorted.json"
    json_data = []
    for r in results:
        json_data.append({
            "rank": r.rank,
            "title": r.item.title,
            "category": r.item.category,
            "final_score": r.final_score,
            "confidence": r.confidence,
            "consensus_level": r.consensus_level,
            "scores": {
                "core": r.core_score,
                "extended": r.extended_score,
                "specialized": r.specialized_score,
                "persona": r.persona_score,
            },
            "top_supporters": r.top_supporters,
            "top_detractors": r.top_detractors,
            "persona_breakdown": r.persona_breakdown,
        })
    json_path.write_text(json.dumps(json_data, indent=2))
    print(f"   JSON written to {json_path}")
    
    print("\n" + "=" * 70)
    print("🔥 TOP 5 PRIORITIES (40-Agent Ultra Consensus)")
    print("=" * 70)
    
    consensus_emoji = {
        "strong": "🟢",
        "moderate": "🟡", 
        "weak": "🟠",
        "controversial": "🔴",
    }
    
    for r in results[:5]:
        emoji = consensus_emoji.get(r.consensus_level, "⚪")
        print(f"\n  {r.rank}. {r.item.title}")
        print(f"     Score: {r.final_score:.2f} | Consensus: {emoji} {r.consensus_level}")
        print(f"     Supporters: {', '.join(r.top_supporters)}")
    
    print("\n" + "=" * 70)
    print("✅ Done!")


if __name__ == "__main__":
    main()
