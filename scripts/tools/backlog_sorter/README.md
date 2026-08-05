# 🤖 Backlog Sorter

A multi-agent priority ranking system for Flow's ROADMAP.md backlog.

## Overview

This tool uses **up to 60 AI agents** running in parallel to analyze and prioritize backlog items from multiple perspectives. Each agent evaluates items based on different criteria, and their weighted votes are combined to produce a final ranking.

## Quick Start

```bash
# From the flow/tools directory
python3 -m backlog_sorter              # Basic 5-agent sort
python3 -m backlog_sorter --full       # 10 agents
python3 -m backlog_sorter --mega       # 25 agents
python3 -m backlog_sorter --ultra      # 40 agents
python3 -m backlog_sorter --godmode    # 🔥 60 agents
```

## Agent Levels

| Level | Agents | Description |
|-------|--------|-------------|
| `--basic` | 5 | Core prioritization (Priority, Effort, Impact, Dependency, Risk) |
| `--full` | 10 | + Technical analysis (Compiler, UX, Platform, TechDebt, Marketing) |
| `--mega` | 25 | + Domain expertise (15 specialized agents) |
| `--ultra` | 40 | + Stakeholder perspectives (15 persona agents) |
| `--godmode` | 60 | + Time factors & chaos (10 temporal + 10 chaos agents) |

## Agent Categories

### Core Agents (5)
- **PriorityAgent** — Urgency and strategic importance
- **EffortAgent** — Implementation complexity (inverted: easy = high score)
- **ImpactAgent** — User value and ecosystem benefit
- **DependencyAgent** — Blockers and prerequisites
- **RiskAgent** — Technical risk (inverted: low risk = high score)

### Extended Agents (5)
- **CompilerFocusAgent** — Language/compiler maturity
- **UserExperienceAgent** — Developer experience
- **PlatformCoverageAgent** — Cross-platform support
- **TechnicalDebtAgent** — Code health and cleanup
- **MarketingValueAgent** — Positioning and showcasing

### Specialized Agents (15)
- **LanguageDesignAgent** — Language semantics
- **EcosystemReadinessAgent** — Production readiness
- **DifferentiatorAgent** — Unique Flow features
- **CommunityGrowthAgent** — Community building
- **PerformanceAgent** — Performance improvements
- **SafetyAgent** — Memory safety and correctness
- **InteropAgent** — FFI and interoperability
- **AudioDSPAgent** — Audio/DSP features (Flow's domain)
- **DocumentationAgent** — Docs and learning resources
- **TestingAgent** — Testing and QA
- **MomentumAgent** — Quick wins and visible progress
- **StrategicAlignmentAgent** — Vision alignment
- **BlockerDetectionAgent** — Dependency chain analysis
- **FreshEyesAgent** — Newcomer perspective
- **LongTermValueAgent** — Foundational vs short-term

### Persona Agents (15)
- **NewcomerDeveloperAgent** — First-time Flow user
- **SystemsProgrammerAgent** — Experienced systems dev
- **AudioEngineerAgent** — Audio/DSP professional
- **MLResearcherAgent** — ML researcher (vs Mojo/Julia)
- **GameDeveloperAgent** — Game developer
- **LanguageDesignerAgent** — PL enthusiast
- **OpenSourceMaintainerAgent** — Project health focus
- **VCInvestorAgent** — Market potential (tongue in cheek)
- **SkepticalEngineerAgent** — Prove it works
- **ProductManagerAgent** — User needs vs effort
- **CompilerEngineerAgent** — Correctness and performance
- **TechWriterAgent** — Documentation quality
- **SecurityEngineerAgent** — Safety and security
- **DevOpsEngineerAgent** — CI/CD and deployment
- **EmbeddedDeveloperAgent** — Resource constraints

### Temporal Agents (10)
- **MomentumWindowAgent** — Is now the right time?
- **TechnicalDebtAccrualAgent** — Debt from delaying
- **CompetitivePressureAgent** — Mojo/Julia/Rust pressure
- **CommunityMomentumAgent** — Community excitement
- **SeasonalRelevanceAgent** — Calendar timing
- **DependencyChainAgent** — Unblocking other work
- **VersionMilestoneAgent** — Version alignment
- **BurndownVelocityAgent** — Sprint velocity
- **TeamMoraleAgent** — Motivation impact
- **LearningCurveAgent** — Skill development

### Chaos Agents (10)
- **RandomAgent** — Pure randomness for tie-breaking
- **ContrarianAgent** — Questions conventional wisdom
- **YOLOAgent** — Favors ambitious projects
- **MinimalistAgent** — Less is more
- **PerfectionistAgent** — Nothing ships until perfect
- **PragmatistAgent** — Ship it!
- **CuriousAgent** — Interesting challenges
- **LazyAgent** — Minimum effort
- **ParanoidAgent** — What could go wrong?
- **OptimistAgent** — Everything will work out!

## CLI Options

```
python3 -m backlog_sorter [OPTIONS]

Options:
  --basic      Use 5 core agents (default)
  --full       Use 10 agents with parallel execution
  --mega       Use 25 agents (core + extended + specialized)
  --ultra      Use 40 agents including persona-based stakeholders
  --godmode    🔥 GODMODE: 60 agents including temporal and chaos

  --watch      Watch ROADMAP.md and re-sort on changes
  --json       Output JSON to stdout
  --quiet      Minimal output
  --roadmap    Path to ROADMAP.md (default: auto-detect)
```

## Output Files

Reports are written to the `scripts/tools/backlog_sorter/` directory:

| Level | Markdown | JSON |
|-------|----------|------|
| basic | `BACKLOG_SORTED.md` | `backlog_sorted.json` |
| full | `BACKLOG_SORTED_DETAILED.md` | `backlog_sorted_detailed.json` |
| mega | `BACKLOG_MEGA_SORTED.md` | `backlog_mega_sorted.json` |
| ultra | `BACKLOG_ULTRA_SORTED.md` | `backlog_ultra_sorted.json` |
| godmode | `BACKLOG_GODMODE.md` | `backlog_godmode.json` |

## How It Works

1. **Parse** — Extract pending items (🔲) from ROADMAP.md
2. **Evaluate** — Each agent scores each item (1-5)
3. **Weight** — Scores are weighted by agent importance
4. **Aggregate** — Category scores combined into final score
5. **Analyze** — Confidence, consensus, and insights calculated
6. **Report** — Markdown and JSON reports generated

## Weight Distribution (GODMODE)

| Category | Weight | Purpose |
|----------|--------|---------|
| Core | 25% | Fundamental prioritization |
| Extended | 15% | Technical analysis |
| Specialized | 20% | Domain expertise |
| Persona | 20% | Stakeholder perspectives |
| Temporal | 15% | Time-based factors |
| Chaos | 5% | Controlled randomness |

## Consensus Levels

| Level | Std Dev | Meaning |
|-------|---------|---------|
| 🟢 Unanimous | < 0.8 | All agents strongly agree |
| 🟢 Strong | 0.8-1.0 | Most agents agree |
| 🟡 Moderate | 1.0-1.3 | General agreement |
| 🟠 Weak | 1.3-1.6 | Some disagreement |
| 🔴 Chaotic | > 1.6 | Agents are fighting |

## Example Output

```
======================================================================
🔥 TOP 5 PRIORITIES (60-Agent GODMODE Consensus) 🔥
======================================================================

  1. Record Tetris demo GIF
     Score: 3.45 | Consensus: 🟡 moderate
     🎲 Chaos is neutral

  2. Benchmark vs C comparison
     Score: 3.31 | Consensus: 🟡 moderate
     🎲 Chaos is neutral

  3. Cross-platform graphics (Linux)
     Score: 3.26 | Consensus: 🟡 moderate
     😈 Chaos is skeptical
```

## Architecture

```
backlog_sorter/
├── __init__.py           # Package init
├── __main__.py           # CLI entry point
├── agents.py             # Core agents + base classes
├── parallel_agents.py    # Extended agents + ParallelOrchestrator
├── specialized_agents.py # 15 domain-specific agents
├── persona_agents.py     # 15 stakeholder persona agents
├── temporal_agents.py    # 10 time-based agents
├── chaos_agents.py       # 10 chaos/randomness agents
├── mega_orchestrator.py  # 25-agent orchestrator
├── ultra_orchestrator.py # 40-agent orchestrator
├── godmode_orchestrator.py # 60-agent orchestrator
└── README.md             # This file
```

## Performance

All agents run in parallel using `ThreadPoolExecutor`. Typical performance:

- **60 agents × 18 items = 1,080 evaluations**
- **Completed in ~0.02 seconds**
- **~50,000 evaluations/second**

## Extending

To add a new agent:

1. Create a class inheriting from `Agent`
2. Set `name` and `weight` class attributes
3. Implement `evaluate(self, item: BacklogItem) -> int` (return 1-5)
4. Add to the appropriate agent list

```python
class MyAgent(Agent):
    name = "MyAgent"
    weight = 1.0
    
    def evaluate(self, item: BacklogItem) -> int:
        if "important" in item.title.lower():
            return 5
        return 3
```

---

*Built for the Flow programming language project*
