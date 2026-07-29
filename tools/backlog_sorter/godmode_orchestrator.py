#!/usr/bin/env python3
"""
🔥 GODMODE ORCHESTRATOR 🔥

60 agents running in parallel for ULTIMATE backlog analysis:
- 5 core agents
- 5 extended agents
- 15 specialized agents
- 15 persona agents
- 10 temporal agents
- 10 chaos agents

This is the final form. There is no higher level.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any
from collections import defaultdict
import json
import time
from pathlib import Path

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
    from backlog_sorter.temporal_agents import TEMPORAL_AGENTS
    from backlog_sorter.chaos_agents import CHAOS_AGENTS
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
    from temporal_agents import TEMPORAL_AGENTS
    from chaos_agents import CHAOS_AGENTS


@dataclass
class GodmodeVote:
    agent_name: str
    agent_category: str
    score: int
    weight: float


@dataclass
class GodmodeResult:
    item: BacklogItem
    votes: list[GodmodeVote]
    
    final_score: float = 0.0
    rank: int = 0
    
    # Category scores
    core_score: float = 0.0
    extended_score: float = 0.0
    specialized_score: float = 0.0
    persona_score: float = 0.0
    temporal_score: float = 0.0
    chaos_score: float = 0.0
    
    # Analysis
    confidence: float = 0.0
    consensus: str = ""
    volatility: float = 0.0  # How much chaos agents disagree
    
    # Top signals
    strongest_supporters: list[str] = field(default_factory=list)
    strongest_detractors: list[str] = field(default_factory=list)
    
    # Chaos analysis
    chaos_verdict: str = ""  # What the chaos agents think


class GodmodeOrchestrator:
    """The ultimate orchestrator. 60 agents. No mercy."""
    
    def __init__(self, max_workers: int = 60):
        # Core (5)
        self.core_agents = [
            PriorityAgent(),
            EffortAgent(),
            ImpactAgent(),
            DependencyAgent(),
            RiskAgent(),
        ]
        
        # Extended (5)
        self.extended_agents = [
            CompilerFocusAgent(),
            UserExperienceAgent(),
            PlatformCoverageAgent(),
            TechnicalDebtAgent(),
            MarketingValueAgent(),
        ]
        
        # Specialized (15)
        self.specialized_agents = [cls() for cls in SPECIALIZED_AGENTS]
        
        # Persona (15)
        self.persona_agents = [cls() for cls in PERSONA_AGENTS]
        
        # Temporal (10)
        self.temporal_agents = [cls() for cls in TEMPORAL_AGENTS]
        
        # Chaos (10)
        self.chaos_agents = [cls() for cls in CHAOS_AGENTS]
        
        # ALL AGENTS
        self.all_agents = (
            self.core_agents +
            self.extended_agents +
            self.specialized_agents +
            self.persona_agents +
            self.temporal_agents +
            self.chaos_agents
        )
        
        self.max_workers = max_workers
        
        self._print_banner()
    
    def _print_banner(self):
        print()
        print("=" * 70)
        print("🔥🔥🔥 GODMODE ORCHESTRATOR ACTIVATED 🔥🔥🔥")
        print("=" * 70)
        print(f"""
    ██████╗  ██████╗ ██████╗ ███╗   ███╗ ██████╗ ██████╗ ███████╗
   ██╔════╝ ██╔═══██╗██╔══██╗████╗ ████║██╔═══██╗██╔══██╗██╔════╝
   ██║  ███╗██║   ██║██║  ██║██╔████╔██║██║   ██║██║  ██║█████╗  
   ██║   ██║██║   ██║██║  ██║██║╚██╔╝██║██║   ██║██║  ██║██╔══╝  
   ╚██████╔╝╚██████╔╝██████╔╝██║ ╚═╝ ██║╚██████╔╝██████╔╝███████╗
    ╚═════╝  ╚═════╝ ╚═════╝ ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝
        """)
        print(f"   Total Agents: {len(self.all_agents)}")
        print(f"   ├── Core:        {len(self.core_agents)}")
        print(f"   ├── Extended:    {len(self.extended_agents)}")
        print(f"   ├── Specialized: {len(self.specialized_agents)}")
        print(f"   ├── Persona:     {len(self.persona_agents)}")
        print(f"   ├── Temporal:    {len(self.temporal_agents)}")
        print(f"   └── Chaos:       {len(self.chaos_agents)}")
        print("=" * 70)
    
    def _get_agent_category(self, agent: Agent) -> str:
        if agent in self.core_agents:
            return "core"
        elif agent in self.extended_agents:
            return "extended"
        elif agent in self.specialized_agents:
            return "specialized"
        elif agent in self.persona_agents:
            return "persona"
        elif agent in self.temporal_agents:
            return "temporal"
        else:
            return "chaos"
    
    def _evaluate_single(self, agent: Agent, item: BacklogItem) -> GodmodeVote:
        score = agent.evaluate(item)
        return GodmodeVote(
            agent_name=agent.name,
            agent_category=self._get_agent_category(agent),
            score=score,
            weight=agent.weight,
        )
    
    def evaluate_item(self, item: BacklogItem) -> GodmodeResult:
        votes = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._evaluate_single, agent, item): agent
                for agent in self.all_agents
            }
            
            for future in as_completed(futures):
                vote = future.result()
                votes.append(vote)
        
        # Calculate category scores
        def weighted_avg(vote_list):
            if not vote_list:
                return 0.0
            total_weight = sum(v.weight for v in vote_list)
            if total_weight == 0:
                return 0.0
            return sum(v.score * v.weight for v in vote_list) / total_weight
        
        core_votes = [v for v in votes if v.agent_category == "core"]
        extended_votes = [v for v in votes if v.agent_category == "extended"]
        specialized_votes = [v for v in votes if v.agent_category == "specialized"]
        persona_votes = [v for v in votes if v.agent_category == "persona"]
        temporal_votes = [v for v in votes if v.agent_category == "temporal"]
        chaos_votes = [v for v in votes if v.agent_category == "chaos"]
        
        core_score = weighted_avg(core_votes)
        extended_score = weighted_avg(extended_votes)
        specialized_score = weighted_avg(specialized_votes)
        persona_score = weighted_avg(persona_votes)
        temporal_score = weighted_avg(temporal_votes)
        chaos_score = weighted_avg(chaos_votes)
        
        # Final score: weighted combination
        # Core: 25%, Extended: 15%, Specialized: 20%, Persona: 20%, Temporal: 15%, Chaos: 5%
        final_score = (
            core_score * 0.25 +
            extended_score * 0.15 +
            specialized_score * 0.20 +
            persona_score * 0.20 +
            temporal_score * 0.15 +
            chaos_score * 0.05
        )
        
        # Confidence calculation
        all_scores = [v.score for v in votes]
        mean = sum(all_scores) / len(all_scores)
        variance = sum((s - mean) ** 2 for s in all_scores) / len(all_scores)
        std_dev = variance ** 0.5
        confidence = max(0, 1 - (std_dev / 2))
        
        # Consensus level
        if std_dev < 0.8:
            consensus = "unanimous"
        elif std_dev < 1.0:
            consensus = "strong"
        elif std_dev < 1.3:
            consensus = "moderate"
        elif std_dev < 1.6:
            consensus = "weak"
        else:
            consensus = "chaotic"
        
        # Chaos volatility
        chaos_scores = [v.score for v in chaos_votes]
        if chaos_scores:
            chaos_mean = sum(chaos_scores) / len(chaos_scores)
            chaos_var = sum((s - chaos_mean) ** 2 for s in chaos_scores) / len(chaos_scores)
            volatility = chaos_var ** 0.5
        else:
            volatility = 0
        
        # Top supporters/detractors
        sorted_votes = sorted(votes, key=lambda v: v.score * v.weight, reverse=True)
        strongest_supporters = [v.agent_name for v in sorted_votes[:5]]
        strongest_detractors = [v.agent_name for v in sorted_votes[-5:]]
        
        # Chaos verdict
        if chaos_score >= 4:
            chaos_verdict = "🔥 CHAOS APPROVES"
        elif chaos_score >= 3:
            chaos_verdict = "🎲 Chaos is neutral"
        elif chaos_score >= 2:
            chaos_verdict = "😈 Chaos is skeptical"
        else:
            chaos_verdict = "💀 CHAOS REJECTS"
        
        return GodmodeResult(
            item=item,
            votes=votes,
            final_score=final_score,
            core_score=core_score,
            extended_score=extended_score,
            specialized_score=specialized_score,
            persona_score=persona_score,
            temporal_score=temporal_score,
            chaos_score=chaos_score,
            confidence=confidence,
            consensus=consensus,
            volatility=volatility,
            strongest_supporters=strongest_supporters,
            strongest_detractors=strongest_detractors,
            chaos_verdict=chaos_verdict,
        )
    
    def sort_backlog(self, items: list[BacklogItem]) -> list[GodmodeResult]:
        total_evals = len(self.all_agents) * len(items)
        print(f"\n⚡ UNLEASHING {len(self.all_agents)} AGENTS ON {len(items)} ITEMS...")
        print(f"   Total evaluations: {total_evals}")
        
        start_time = time.time()
        
        results = []
        for i, item in enumerate(items, 1):
            result = self.evaluate_item(item)
            results.append(result)
            
            pct = (i / len(items)) * 100
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            print(f"\r   [{bar}] {pct:.0f}% ({i}/{len(items)})", end="", flush=True)
        
        print()
        
        elapsed = time.time() - start_time
        evals_per_sec = total_evals / elapsed if elapsed > 0 else 0
        print(f"   ⚡ Completed in {elapsed:.2f}s ({evals_per_sec:.0f} evals/sec)")
        
        sorted_results = sorted(results, key=lambda r: r.final_score, reverse=True)
        for i, result in enumerate(sorted_results, 1):
            result.rank = i
        
        return sorted_results
    
    def generate_godmode_report(self, results: list[GodmodeResult]) -> str:
        lines = [
            "# 🔥 GODMODE Backlog Priority Report 🔥",
            "",
            f"> **{len(self.all_agents)} agents** analyzed **{len(results)} items**",
            f"> Total evaluations: **{len(self.all_agents) * len(results)}**",
            "",
            "## 🤖 Agent Army",
            "",
            "| Category | Count | Weight | Purpose |",
            "|----------|-------|--------|---------|",
            f"| Core | {len(self.core_agents)} | 25% | Fundamental prioritization |",
            f"| Extended | {len(self.extended_agents)} | 15% | Technical analysis |",
            f"| Specialized | {len(self.specialized_agents)} | 20% | Domain expertise |",
            f"| Persona | {len(self.persona_agents)} | 20% | Stakeholder perspectives |",
            f"| Temporal | {len(self.temporal_agents)} | 15% | Time-based factors |",
            f"| Chaos | {len(self.chaos_agents)} | 5% | Controlled randomness |",
            "",
            "---",
            "",
            "## 🏆 FINAL RANKINGS",
            "",
        ]
        
        consensus_emoji = {
            "unanimous": "🟢",
            "strong": "🟢",
            "moderate": "🟡",
            "weak": "🟠",
            "chaotic": "🔴",
        }
        
        lines.extend([
            "| Rank | Task | Score | Consensus | Core | Spec | Persona | Temporal | Chaos |",
            "|------|------|-------|-----------|------|------|---------|----------|-------|",
        ])
        
        for r in results:
            emoji = consensus_emoji.get(r.consensus, "⚪")
            lines.append(
                f"| {r.rank} | {r.item.title} | **{r.final_score:.2f}** | "
                f"{emoji} {r.consensus} | {r.core_score:.1f} | {r.specialized_score:.1f} | "
                f"{r.persona_score:.1f} | {r.temporal_score:.1f} | {r.chaos_verdict} |"
            )
        
        lines.extend([
            "",
            "---",
            "",
            "## 🎯 GODMODE RECOMMENDATIONS",
            "",
            "### 🥇 Top 5 Priorities",
            "",
        ])
        
        for r in results[:5]:
            emoji = consensus_emoji.get(r.consensus, "⚪")
            lines.append(f"#### {r.rank}. {r.item.title}")
            lines.append("")
            lines.append(f"- **Final Score:** {r.final_score:.2f}")
            lines.append(f"- **Consensus:** {emoji} {r.consensus} ({r.confidence:.0%} confidence)")
            lines.append(f"- **Chaos Verdict:** {r.chaos_verdict}")
            lines.append(f"- **Top Supporters:** {', '.join(r.strongest_supporters[:3])}")
            lines.append(f"- **Category:** {r.item.category}")
            lines.append("")
        
        # Unanimous items
        unanimous = [r for r in results if r.consensus in ["unanimous", "strong"]]
        if unanimous:
            lines.extend([
                "### 🟢 Unanimous Priorities",
                "",
                "All 60 agents agree on these:",
                "",
            ])
            for r in unanimous[:5]:
                lines.append(f"- {r.item.title} (score: {r.final_score:.2f})")
        
        # Chaotic items
        chaotic = [r for r in results if r.consensus == "chaotic"]
        if chaotic:
            lines.extend([
                "",
                "### 🔴 Chaotic Items (High Disagreement)",
                "",
                "Agents are fighting over these:",
                "",
            ])
            for r in chaotic:
                lines.append(f"- **{r.item.title}**")
                lines.append(f"  - Supporters: {', '.join(r.strongest_supporters[:3])}")
                lines.append(f"  - Detractors: {', '.join(r.strongest_detractors[:3])}")
        
        # Chaos-approved
        chaos_approved = [r for r in results if "APPROVES" in r.chaos_verdict]
        if chaos_approved:
            lines.extend([
                "",
                "### 🔥 Chaos-Approved Items",
                "",
                "The chaos agents love these:",
                "",
            ])
            for r in chaos_approved[:5]:
                lines.append(f"- {r.item.title} (chaos score: {r.chaos_score:.1f})")
        
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
            bar_len = int((count / max(max_count, 1)) * 30)
            bar = "█" * bar_len + "░" * (30 - bar_len)
            lines.append(f"{low:.1f}-{high:.1f} | {bar} {count}")
        
        lines.extend([
            "```",
            "",
            "---",
            "",
            "## 🔍 Agent Influence Analysis",
            "",
        ])
        
        # Calculate influence
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
            "### Chaos Agent Breakdown",
            "",
            "| Agent | Avg Score | Personality |",
            "|-------|-----------|-------------|",
        ])
        
        chaos_personalities = {
            "RandomAgent": "Pure chaos",
            "ContrarianAgent": "Deliberately contrarian",
            "YOLOAgent": "Go big or go home",
            "MinimalistAgent": "Less is more",
            "PerfectionistAgent": "Nothing ships until perfect",
            "PragmatistAgent": "Ship it!",
            "CuriousAgent": "Follows interesting challenges",
            "LazyAgent": "Minimum effort",
            "ParanoidAgent": "What could go wrong?",
            "OptimistAgent": "Everything will work out!",
        }
        
        for agent in self.chaos_agents:
            if agent.name in avg_influence:
                personality = chaos_personalities.get(agent.name, "Unknown")
                lines.append(f"| {agent.name} | {avg_influence[agent.name]:.2f} | {personality} |")
        
        lines.extend([
            "",
            "---",
            "",
            f"*Generated by GODMODE Orchestrator with {len(self.all_agents)} agents*",
            "",
            "```",
            "   ██████╗  ██████╗ ██████╗ ███╗   ███╗ ██████╗ ██████╗ ███████╗",
            "  ██╔════╝ ██╔═══██╗██╔══██╗████╗ ████║██╔═══██╗██╔══██╗██╔════╝",
            "  ██║  ███╗██║   ██║██║  ██║██╔████╔██║██║   ██║██║  ██║█████╗  ",
            "  ██║   ██║██║   ██║██║  ██║██║╚██╔╝██║██║   ██║██║  ██║██╔══╝  ",
            "  ╚██████╔╝╚██████╔╝██████╔╝██║ ╚═╝ ██║╚██████╔╝██████╔╝███████╗",
            "   ╚═════╝  ╚═════╝ ╚═════╝ ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝",
            "```",
        ])
        
        return "\n".join(lines)


def main():
    import sys
    
    script_dir = Path(__file__).parent
    roadmap_path = script_dir.parent.parent / "ROADMAP.md"
    
    if not roadmap_path.exists():
        print(f"Error: ROADMAP.md not found at {roadmap_path}")
        sys.exit(1)
    
    print(f"📋 Parsing {roadmap_path}...")
    items = parse_roadmap(roadmap_path)
    print(f"   Found {len(items)} pending items")
    
    orchestrator = GodmodeOrchestrator(max_workers=60)
    results = orchestrator.sort_backlog(items)
    
    print("\n📊 Generating GODMODE report...")
    report = orchestrator.generate_godmode_report(results)
    
    output_path = script_dir / "BACKLOG_GODMODE.md"
    output_path.write_text(report)
    print(f"   Written to {output_path}")
    
    # JSON
    json_path = script_dir / "backlog_godmode.json"
    json_data = []
    for r in results:
        json_data.append({
            "rank": r.rank,
            "title": r.item.title,
            "category": r.item.category,
            "final_score": r.final_score,
            "confidence": r.confidence,
            "consensus": r.consensus,
            "chaos_verdict": r.chaos_verdict,
            "scores": {
                "core": r.core_score,
                "extended": r.extended_score,
                "specialized": r.specialized_score,
                "persona": r.persona_score,
                "temporal": r.temporal_score,
                "chaos": r.chaos_score,
            },
            "supporters": r.strongest_supporters,
            "detractors": r.strongest_detractors,
        })
    json_path.write_text(json.dumps(json_data, indent=2))
    print(f"   JSON written to {json_path}")
    
    # Print results
    consensus_emoji = {
        "unanimous": "🟢",
        "strong": "🟢",
        "moderate": "🟡",
        "weak": "🟠",
        "chaotic": "🔴",
    }
    
    print("\n" + "=" * 70)
    print("🔥 TOP 5 PRIORITIES (60-Agent GODMODE Consensus) 🔥")
    print("=" * 70)
    
    for r in results[:5]:
        emoji = consensus_emoji.get(r.consensus, "⚪")
        print(f"\n  {r.rank}. {r.item.title}")
        print(f"     Score: {r.final_score:.2f} | Consensus: {emoji} {r.consensus}")
        print(f"     {r.chaos_verdict}")
    
    print("\n" + "=" * 70)
    print("🔥 GODMODE COMPLETE 🔥")
    print("=" * 70)


if __name__ == "__main__":
    main()
