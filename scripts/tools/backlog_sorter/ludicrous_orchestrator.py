#!/usr/bin/env python3
"""
🚀 LUDICROUS MODE ORCHESTRATOR 🚀

90 agents running in parallel for MAXIMUM backlog analysis:
- 5 core agents
- 5 extended agents
- 15 specialized agents
- 15 persona agents
- 10 temporal agents
- 10 chaos agents
- 19 meta agents
- 11 philosophical agents

This goes beyond GODMODE. This is LUDICROUS.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
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
    from backlog_sorter.meta_agents import META_AGENTS
    from backlog_sorter.philosophical_agents import PHILOSOPHICAL_AGENTS
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
    from meta_agents import META_AGENTS
    from philosophical_agents import PHILOSOPHICAL_AGENTS


@dataclass
class LudicrousResult:
    item: BacklogItem
    votes: list
    final_score: float = 0.0
    rank: int = 0
    confidence: float = 0.0
    consensus: str = ""
    category_scores: dict = field(default_factory=dict)
    top_supporters: list = field(default_factory=list)
    verdict: str = ""


class LudicrousOrchestrator:
    """90 agents. LUDICROUS MODE."""
    
    def __init__(self, max_workers: int = 90):
        self.core = [PriorityAgent(), EffortAgent(), ImpactAgent(), DependencyAgent(), RiskAgent()]
        self.extended = [CompilerFocusAgent(), UserExperienceAgent(), PlatformCoverageAgent(), TechnicalDebtAgent(), MarketingValueAgent()]
        self.specialized = [cls() for cls in SPECIALIZED_AGENTS]
        self.persona = [cls() for cls in PERSONA_AGENTS]
        self.temporal = [cls() for cls in TEMPORAL_AGENTS]
        self.chaos = [cls() for cls in CHAOS_AGENTS]
        self.meta = [cls() for cls in META_AGENTS]
        self.philosophical = [cls() for cls in PHILOSOPHICAL_AGENTS]
        
        self.all_agents = self.core + self.extended + self.specialized + self.persona + self.temporal + self.chaos + self.meta + self.philosophical
        self.max_workers = max_workers
        
        self._print_banner()
    
    def _print_banner(self):
        print("\n" + "=" * 70)
        print("🚀🚀🚀 LUDICROUS MODE ACTIVATED 🚀🚀🚀")
        print("=" * 70)
        print("""
   ██╗     ██╗   ██╗██████╗ ██╗ ██████╗██████╗  ██████╗ ██╗   ██╗███████╗
   ██║     ██║   ██║██╔══██╗██║██╔════╝██╔══██╗██╔═══██╗██║   ██║██╔════╝
   ██║     ██║   ██║██║  ██║██║██║     ██████╔╝██║   ██║██║   ██║███████╗
   ██║     ██║   ██║██║  ██║██║██║     ██╔══██╗██║   ██║██║   ██║╚════██║
   ███████╗╚██████╔╝██████╔╝██║╚██████╗██║  ██║╚██████╔╝╚██████╔╝███████║
   ╚══════╝ ╚═════╝ ╚═════╝ ╚═╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚══════╝
        """)
        print(f"   Total Agents: {len(self.all_agents)}")
        print(f"   ├── Core:         {len(self.core)}")
        print(f"   ├── Extended:     {len(self.extended)}")
        print(f"   ├── Specialized:  {len(self.specialized)}")
        print(f"   ├── Persona:      {len(self.persona)}")
        print(f"   ├── Temporal:     {len(self.temporal)}")
        print(f"   ├── Chaos:        {len(self.chaos)}")
        print(f"   ├── Meta:         {len(self.meta)}")
        print(f"   └── Philosophical:{len(self.philosophical)}")
        print("=" * 70)
    
    def _get_category(self, agent):
        if agent in self.core: return "core"
        if agent in self.extended: return "extended"
        if agent in self.specialized: return "specialized"
        if agent in self.persona: return "persona"
        if agent in self.temporal: return "temporal"
        if agent in self.chaos: return "chaos"
        if agent in self.meta: return "meta"
        return "philosophical"
    
    def evaluate_item(self, item: BacklogItem) -> LudicrousResult:
        votes = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as ex:
            futures = {ex.submit(lambda a, i: (a.name, self._get_category(a), a.evaluate(i), a.weight), agent, item): agent for agent in self.all_agents}
            for f in as_completed(futures):
                votes.append(f.result())
        
        # Calculate scores
        cat_scores = defaultdict(list)
        for name, cat, score, weight in votes:
            cat_scores[cat].append((score, weight))
        
        def wavg(lst):
            if not lst: return 0
            tw = sum(w for s, w in lst)
            return sum(s * w for s, w in lst) / tw if tw else 0
        
        scores = {k: wavg(v) for k, v in cat_scores.items()}
        
        # Weights: core 20%, extended 10%, specialized 15%, persona 15%, temporal 15%, chaos 5%, meta 10%, philosophical 10%
        final = (scores.get("core", 0) * 0.20 + scores.get("extended", 0) * 0.10 + 
                 scores.get("specialized", 0) * 0.15 + scores.get("persona", 0) * 0.15 +
                 scores.get("temporal", 0) * 0.15 + scores.get("chaos", 0) * 0.05 +
                 scores.get("meta", 0) * 0.10 + scores.get("philosophical", 0) * 0.10)
        
        all_scores = [s for _, _, s, _ in votes]
        mean = sum(all_scores) / len(all_scores)
        std = (sum((s - mean) ** 2 for s in all_scores) / len(all_scores)) ** 0.5
        confidence = max(0, 1 - std / 2)
        
        consensus = "unanimous" if std < 0.8 else "strong" if std < 1.0 else "moderate" if std < 1.3 else "weak" if std < 1.6 else "chaotic"
        
        sorted_votes = sorted(votes, key=lambda x: x[2] * x[3], reverse=True)
        top = [v[0] for v in sorted_votes[:5]]
        
        if final >= 3.5: verdict = "🚀 SHIP IT"
        elif final >= 3.0: verdict = "👍 Good to go"
        elif final >= 2.5: verdict = "🤔 Consider it"
        else: verdict = "⏸️ Backlog it"
        
        return LudicrousResult(item=item, votes=votes, final_score=final, confidence=confidence, 
                               consensus=consensus, category_scores=scores, top_supporters=top, verdict=verdict)
    
    def sort_backlog(self, items):
        total = len(self.all_agents) * len(items)
        print(f"\n🚀 UNLEASHING {len(self.all_agents)} AGENTS...")
        print(f"   Total evaluations: {total}")
        
        start = time.time()
        results = []
        for i, item in enumerate(items, 1):
            results.append(self.evaluate_item(item))
            pct = i / len(items) * 100
            print(f"\r   [{'█' * int(pct/5)}{'░' * (20-int(pct/5))}] {pct:.0f}%", end="", flush=True)
        print()
        
        elapsed = time.time() - start
        print(f"   ⚡ {elapsed:.2f}s ({total/elapsed:.0f} evals/sec)")
        
        sorted_results = sorted(results, key=lambda r: r.final_score, reverse=True)
        for i, r in enumerate(sorted_results, 1):
            r.rank = i
        return sorted_results
    
    def generate_ludicrous_report(self, results):
        lines = ["# 🚀 LUDICROUS MODE Report", "", f"> **{len(self.all_agents)} agents** analyzed **{len(results)} items**", ""]
        lines.extend(["## Rankings", "", "| Rank | Task | Score | Consensus | Verdict |", "|------|------|-------|-----------|---------|"])
        
        emoji = {"unanimous": "🟢", "strong": "🟢", "moderate": "🟡", "weak": "🟠", "chaotic": "🔴"}
        for r in results:
            lines.append(f"| {r.rank} | {r.item.title} | **{r.final_score:.2f}** | {emoji.get(r.consensus, '⚪')} {r.consensus} | {r.verdict} |")
        
        lines.extend(["", "## Top 5", ""])
        for r in results[:5]:
            lines.append(f"### {r.rank}. {r.item.title}")
            lines.append(f"- Score: {r.final_score:.2f} | {r.verdict}")
            lines.append(f"- Supporters: {', '.join(r.top_supporters[:3])}")
            lines.append("")
        
        return "\n".join(lines)


def main():
    import sys
    script_dir = Path(__file__).parent
    roadmap = script_dir.parent.parent.parent / "docs/project/ROADMAP.md"
    
    if not roadmap.exists():
        print(f"Error: {roadmap} not found")
        sys.exit(1)
    
    print(f"📋 Parsing {roadmap}...")
    items = parse_roadmap(roadmap)
    print(f"   Found {len(items)} items")
    
    orch = LudicrousOrchestrator()
    results = orch.sort_backlog(items)
    
    report = orch.generate_ludicrous_report(results)
    out = script_dir / "BACKLOG_LUDICROUS.md"
    out.write_text(report)
    print(f"\n📊 Written to {out}")
    
    print("\n" + "=" * 70)
    print("🚀 TOP 5 (90-Agent LUDICROUS Consensus)")
    print("=" * 70)
    for r in results[:5]:
        print(f"\n  {r.rank}. {r.item.title}")
        print(f"     Score: {r.final_score:.2f} | {r.verdict}")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
