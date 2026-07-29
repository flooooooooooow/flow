#!/usr/bin/env python3
"""
MEGA ORCHESTRATOR - 25 agents running in parallel!

Combines all agent types for comprehensive backlog analysis:
- 5 core agents
- 5 extended agents  
- 15 specialized agents

Total: 25 agents providing multi-perspective prioritization.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any
import json
import time
from pathlib import Path

try:
    from backlog_sorter.agents import (
        BacklogItem, Agent, PriorityAgent, EffortAgent,
        ImpactAgent, DependencyAgent, RiskAgent, parse_roadmap, Orchestrator
    )
    from backlog_sorter.parallel_agents import (
        CompilerFocusAgent, UserExperienceAgent, PlatformCoverageAgent,
        TechnicalDebtAgent, MarketingValueAgent
    )
    from backlog_sorter.specialized_agents import SPECIALIZED_AGENTS
except ImportError:
    from agents import (
        BacklogItem, Agent, PriorityAgent, EffortAgent,
        ImpactAgent, DependencyAgent, RiskAgent, parse_roadmap, Orchestrator
    )
    from parallel_agents import (
        CompilerFocusAgent, UserExperienceAgent, PlatformCoverageAgent,
        TechnicalDebtAgent, MarketingValueAgent
    )
    from specialized_agents import SPECIALIZED_AGENTS


@dataclass
class AgentVote:
    """A single agent's vote on an item."""
    agent_name: str
    score: int
    weight: float
    category: str  # core, extended, specialized


@dataclass 
class ConsensusResult:
    """Aggregated result from all agents."""
    item: BacklogItem
    votes: list[AgentVote]
    final_score: float
    confidence: float  # How much agents agree (0-1)
    rank: int = 0
    
    # Breakdown by category
    core_score: float = 0.0
    extended_score: float = 0.0
    specialized_score: float = 0.0
    
    # Analysis
    strongest_signal: str = ""
    weakest_signal: str = ""
    controversial: bool = False


class MegaOrchestrator:
    """Coordinates 25 agents for comprehensive analysis."""
    
    def __init__(self, max_workers: int = 25):
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
        
        # All agents combined
        self.all_agents = (
            self.core_agents + 
            self.extended_agents + 
            self.specialized_agents
        )
        
        self.max_workers = max_workers
        
        print(f"🤖 Initialized {len(self.all_agents)} agents:")
        print(f"   - {len(self.core_agents)} core agents")
        print(f"   - {len(self.extended_agents)} extended agents")
        print(f"   - {len(self.specialized_agents)} specialized agents")
    
    def _get_agent_category(self, agent: Agent) -> str:
        if agent in self.core_agents:
            return "core"
        elif agent in self.extended_agents:
            return "extended"
        else:
            return "specialized"
    
    def _evaluate_single(self, agent: Agent, item: BacklogItem) -> AgentVote:
        """Evaluate a single item with a single agent."""
        score = agent.evaluate(item)
        return AgentVote(
            agent_name=agent.name,
            score=score,
            weight=agent.weight,
            category=self._get_agent_category(agent)
        )
    
    def evaluate_item(self, item: BacklogItem) -> ConsensusResult:
        """Run all 25 agents on an item in parallel."""
        votes = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._evaluate_single, agent, item): agent
                for agent in self.all_agents
            }
            
            for future in as_completed(futures):
                vote = future.result()
                votes.append(vote)
        
        # Calculate scores by category
        core_votes = [v for v in votes if v.category == "core"]
        extended_votes = [v for v in votes if v.category == "extended"]
        specialized_votes = [v for v in votes if v.category == "specialized"]
        
        def weighted_avg(vote_list):
            if not vote_list:
                return 0.0
            total_weight = sum(v.weight for v in vote_list)
            return sum(v.score * v.weight for v in vote_list) / total_weight
        
        core_score = weighted_avg(core_votes)
        extended_score = weighted_avg(extended_votes)
        specialized_score = weighted_avg(specialized_votes)
        
        # Final score: weighted combination of categories
        # Core: 40%, Extended: 30%, Specialized: 30%
        final_score = (
            core_score * 0.40 +
            extended_score * 0.30 +
            specialized_score * 0.30
        )
        
        # Calculate confidence (agreement between agents)
        scores = [v.score for v in votes]
        mean_score = sum(scores) / len(scores)
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        std_dev = variance ** 0.5
        confidence = max(0, 1 - (std_dev / 2))  # Lower std = higher confidence
        
        # Find strongest and weakest signals
        max_vote = max(votes, key=lambda v: v.score * v.weight)
        min_vote = min(votes, key=lambda v: v.score * v.weight)
        
        # Controversial if high variance
        controversial = std_dev > 1.2
        
        return ConsensusResult(
            item=item,
            votes=votes,
            final_score=final_score,
            confidence=confidence,
            core_score=core_score,
            extended_score=extended_score,
            specialized_score=specialized_score,
            strongest_signal=max_vote.agent_name,
            weakest_signal=min_vote.agent_name,
            controversial=controversial,
        )
    
    def sort_backlog(self, items: list[BacklogItem]) -> list[ConsensusResult]:
        """Evaluate and sort all items."""
        print(f"\n⚡ Running {len(self.all_agents)} agents on {len(items)} items...")
        print(f"   Total evaluations: {len(self.all_agents) * len(items)}")
        
        start_time = time.time()
        
        results = []
        for i, item in enumerate(items, 1):
            result = self.evaluate_item(item)
            results.append(result)
            
            # Progress indicator
            if i % 5 == 0 or i == len(items):
                print(f"   Processed {i}/{len(items)} items...")
        
        elapsed = time.time() - start_time
        print(f"   Completed in {elapsed:.2f}s")
        
        # Sort by final score
        sorted_results = sorted(results, key=lambda r: r.final_score, reverse=True)
        
        for i, result in enumerate(sorted_results, 1):
            result.rank = i
        
        return sorted_results
    
    def generate_mega_report(self, results: list[ConsensusResult]) -> str:
        """Generate comprehensive markdown report."""
        lines = [
            "# 🚀 MEGA Backlog Priority Report",
            "",
            f"> **{len(self.all_agents)} agents** analyzed **{len(results)} items**",
            "",
            "## Agent Army",
            "",
            "### Core Agents (40% weight)",
            "",
            "| Agent | Weight | Focus |",
            "|-------|--------|-------|",
        ]
        
        for agent in self.core_agents:
            lines.append(f"| {agent.name} | {agent.weight:.1f} | Core prioritization |")
        
        lines.extend([
            "",
            "### Extended Agents (30% weight)",
            "",
            "| Agent | Weight | Focus |",
            "|-------|--------|-------|",
        ])
        
        for agent in self.extended_agents:
            lines.append(f"| {agent.name} | {agent.weight:.1f} | Extended analysis |")
        
        lines.extend([
            "",
            "### Specialized Agents (30% weight)",
            "",
            "| Agent | Weight | Focus |",
            "|-------|--------|-------|",
        ])
        
        for agent in self.specialized_agents:
            lines.append(f"| {agent.name} | {agent.weight:.1f} | Domain expertise |")
        
        lines.extend([
            "",
            "---",
            "",
            "## 🏆 Final Rankings",
            "",
            "| Rank | Task | Score | Confidence | Core | Ext | Spec | Signal |",
            "|------|------|-------|------------|------|-----|------|--------|",
        ])
        
        for r in results:
            conf_emoji = "🟢" if r.confidence > 0.7 else "🟡" if r.confidence > 0.5 else "🔴"
            controversial = "⚡" if r.controversial else ""
            lines.append(
                f"| {r.rank} | {r.item.title} | **{r.final_score:.2f}** | "
                f"{conf_emoji} {r.confidence:.0%} | {r.core_score:.1f} | "
                f"{r.extended_score:.1f} | {r.specialized_score:.1f} | "
                f"{r.strongest_signal} {controversial} |"
            )
        
        lines.extend([
            "",
            "---",
            "",
            "## 🎯 Sprint Recommendations",
            "",
            "### Immediate Focus (Top 5)",
            "",
        ])
        
        for r in results[:5]:
            lines.append(f"1. **{r.item.title}**")
            lines.append(f"   - Score: {r.final_score:.2f} | Confidence: {r.confidence:.0%}")
            lines.append(f"   - Strongest signal: {r.strongest_signal}")
            lines.append(f"   - Category: {r.item.category}")
            lines.append("")
        
        # High confidence items
        high_conf = [r for r in results if r.confidence > 0.7]
        if high_conf:
            lines.extend([
                "### 🟢 High Confidence Items",
                "",
                "All agents strongly agree on these:",
                "",
            ])
            for r in high_conf[:5]:
                lines.append(f"- {r.item.title} (confidence: {r.confidence:.0%})")
        
        # Controversial items
        controversial = [r for r in results if r.controversial]
        if controversial:
            lines.extend([
                "",
                "### ⚡ Controversial Items",
                "",
                "Agents disagree on these - may need human judgment:",
                "",
            ])
            for r in controversial[:5]:
                lines.append(f"- {r.item.title} (strongest: {r.strongest_signal}, weakest: {r.weakest_signal})")
        
        # Quick wins
        quick_wins = [r for r in results if r.core_score >= 3.5 and r.confidence > 0.6]
        if quick_wins:
            lines.extend([
                "",
                "### ⚡ Quick Wins",
                "",
            ])
            for r in quick_wins[:5]:
                lines.append(f"- {r.item.title}")
        
        lines.extend([
            "",
            "---",
            "",
            "## 📊 Score Distribution",
            "",
            "```",
        ])
        
        # Histogram
        ranges = [(4.0, 5.0), (3.5, 4.0), (3.0, 3.5), (2.5, 3.0), (2.0, 2.5), (0, 2.0)]
        for low, high in ranges:
            count = sum(1 for r in results if low <= r.final_score < high)
            bar = "█" * count + "░" * (10 - count)
            lines.append(f"{low:.1f}-{high:.1f} | {bar} {count}")
        
        lines.extend([
            "```",
            "",
            "---",
            "",
            "## 🔍 Agent Consensus Analysis",
            "",
        ])
        
        # Which agents had the most influence?
        agent_influence = {}
        for r in results:
            for vote in r.votes:
                if vote.agent_name not in agent_influence:
                    agent_influence[vote.agent_name] = []
                agent_influence[vote.agent_name].append(vote.score * vote.weight)
        
        avg_influence = {
            name: sum(scores) / len(scores) 
            for name, scores in agent_influence.items()
        }
        
        sorted_influence = sorted(avg_influence.items(), key=lambda x: x[1], reverse=True)
        
        lines.extend([
            "### Most Influential Agents",
            "",
            "| Agent | Avg Weighted Score |",
            "|-------|-------------------|",
        ])
        
        for name, score in sorted_influence[:10]:
            lines.append(f"| {name} | {score:.2f} |")
        
        lines.extend([
            "",
            "---",
            "",
            f"*Generated by MegaOrchestrator with {len(self.all_agents)} agents*",
        ])
        
        return "\n".join(lines)


def main():
    """Run the mega orchestrator."""
    import sys
    
    script_dir = Path(__file__).parent
    roadmap_path = script_dir.parent.parent / "ROADMAP.md"
    
    if not roadmap_path.exists():
        print(f"Error: ROADMAP.md not found at {roadmap_path}")
        sys.exit(1)
    
    print(f"📋 Parsing {roadmap_path}...")
    items = parse_roadmap(roadmap_path)
    print(f"   Found {len(items)} pending items")
    
    orchestrator = MegaOrchestrator(max_workers=25)
    results = orchestrator.sort_backlog(items)
    
    print("\n📊 Generating mega report...")
    report = orchestrator.generate_mega_report(results)
    
    output_path = script_dir / "BACKLOG_MEGA_SORTED.md"
    output_path.write_text(report)
    print(f"   Written to {output_path}")
    
    # JSON output
    json_path = script_dir / "backlog_mega_sorted.json"
    json_data = []
    for r in results:
        json_data.append({
            "rank": r.rank,
            "title": r.item.title,
            "category": r.item.category,
            "final_score": r.final_score,
            "confidence": r.confidence,
            "core_score": r.core_score,
            "extended_score": r.extended_score,
            "specialized_score": r.specialized_score,
            "strongest_signal": r.strongest_signal,
            "weakest_signal": r.weakest_signal,
            "controversial": r.controversial,
            "votes": [
                {"agent": v.agent_name, "score": v.score, "weight": v.weight}
                for v in r.votes
            ]
        })
    json_path.write_text(json.dumps(json_data, indent=2))
    print(f"   JSON written to {json_path}")
    
    print("\n" + "=" * 70)
    print("🏆 TOP 5 PRIORITIES (25-Agent Mega Consensus)")
    print("=" * 70)
    for r in results[:5]:
        conf = "🟢" if r.confidence > 0.7 else "🟡" if r.confidence > 0.5 else "🔴"
        print(f"  {r.rank}. {r.item.title}")
        print(f"     Score: {r.final_score:.2f} | Confidence: {conf} {r.confidence:.0%}")
        print(f"     Strongest signal: {r.strongest_signal}")
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
