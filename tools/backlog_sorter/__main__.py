#!/usr/bin/env python3
"""
CLI entry point for backlog sorter.

Usage:
    python -m backlog_sorter [OPTIONS]

Options:
    --basic     Use 5 core agents (default)
    --full      Use 10 agents (parallel execution)
    --mega      Use 25 agents (core + extended + specialized)
    --ultra     Use 40 agents (ALL agents including personas)
    --watch     Watch ROADMAP.md and re-sort on changes
    --json      Output JSON to stdout instead of markdown
    --quiet     Minimal output
    --help      Show this help
"""

import argparse
import json
import sys
import time
from pathlib import Path


def find_roadmap() -> Path:
    """Find ROADMAP.md relative to this script."""
    script_dir = Path(__file__).parent
    roadmap = script_dir.parent.parent / "ROADMAP.md"
    if not roadmap.exists():
        # Try current directory
        roadmap = Path.cwd() / "ROADMAP.md"
    return roadmap


def run_basic_sort(roadmap_path: Path, quiet: bool = False) -> list:
    """Run basic 5-agent sort."""
    from backlog_sorter.agents import Orchestrator, parse_roadmap
    
    if not quiet:
        print(f"📋 Parsing {roadmap_path}...")
    
    items = parse_roadmap(roadmap_path)
    
    if not quiet:
        print(f"   Found {len(items)} pending items")
        print("\n🤖 Running 5-agent evaluation...")
    
    orchestrator = Orchestrator()
    sorted_items = orchestrator.sort_backlog(items)
    
    return sorted_items, orchestrator, "BACKLOG_SORTED.md"


def run_full_sort(roadmap_path: Path, quiet: bool = False) -> list:
    """Run full 10-agent parallel sort."""
    from backlog_sorter.parallel_agents import ParallelOrchestrator
    from backlog_sorter.agents import parse_roadmap
    
    if not quiet:
        print(f"📋 Parsing {roadmap_path}...")
    
    items = parse_roadmap(roadmap_path)
    
    if not quiet:
        print(f"   Found {len(items)} pending items")
        print("\n🤖 Running 10-agent parallel evaluation...")
    
    orchestrator = ParallelOrchestrator(max_workers=10)
    sorted_items = orchestrator.sort_backlog(items)
    
    return sorted_items, orchestrator, "BACKLOG_SORTED_DETAILED.md"


def run_mega_sort(roadmap_path: Path, quiet: bool = False) -> list:
    """Run 25-agent mega sort."""
    from backlog_sorter.mega_orchestrator import MegaOrchestrator
    from backlog_sorter.agents import parse_roadmap
    
    if not quiet:
        print(f"📋 Parsing {roadmap_path}...")
    
    items = parse_roadmap(roadmap_path)
    
    if not quiet:
        print(f"   Found {len(items)} pending items")
    
    orchestrator = MegaOrchestrator(max_workers=25)
    results = orchestrator.sort_backlog(items)
    
    return results, orchestrator, "BACKLOG_MEGA_SORTED.md"


def run_ultra_sort(roadmap_path: Path, quiet: bool = False) -> list:
    """Run 40-agent ultra sort."""
    from backlog_sorter.ultra_orchestrator import UltraOrchestrator
    from backlog_sorter.agents import parse_roadmap
    
    if not quiet:
        print(f"📋 Parsing {roadmap_path}...")
    
    items = parse_roadmap(roadmap_path)
    
    if not quiet:
        print(f"   Found {len(items)} pending items")
    
    orchestrator = UltraOrchestrator(max_workers=40)
    results = orchestrator.sort_backlog(items)
    
    return results, orchestrator, "BACKLOG_ULTRA_SORTED.md"


def run_godmode_sort(roadmap_path: Path, quiet: bool = False) -> list:
    """Run 60-agent GODMODE sort."""
    from backlog_sorter.godmode_orchestrator import GodmodeOrchestrator
    from backlog_sorter.agents import parse_roadmap
    
    if not quiet:
        print(f"📋 Parsing {roadmap_path}...")
    
    items = parse_roadmap(roadmap_path)
    
    if not quiet:
        print(f"   Found {len(items)} pending items")
    
    orchestrator = GodmodeOrchestrator(max_workers=60)
    results = orchestrator.sort_backlog(items)
    
    return results, orchestrator, "BACKLOG_GODMODE.md"


def run_ludicrous_sort(roadmap_path: Path, quiet: bool = False) -> list:
    """Run 90-agent LUDICROUS sort."""
    from backlog_sorter.ludicrous_orchestrator import LudicrousOrchestrator
    from backlog_sorter.agents import parse_roadmap
    
    if not quiet:
        print(f"📋 Parsing {roadmap_path}...")
    
    items = parse_roadmap(roadmap_path)
    
    if not quiet:
        print(f"   Found {len(items)} pending items")
    
    orchestrator = LudicrousOrchestrator(max_workers=90)
    results = orchestrator.sort_backlog(items)
    
    return results, orchestrator, "BACKLOG_LUDICROUS.md"


def watch_mode(roadmap_path: Path, full: bool = False):
    """Watch ROADMAP.md and re-sort on changes."""
    print(f"👀 Watching {roadmap_path} for changes...")
    print("   Press Ctrl+C to stop\n")
    
    last_mtime = 0
    
    try:
        while True:
            current_mtime = roadmap_path.stat().st_mtime
            
            if current_mtime != last_mtime:
                last_mtime = current_mtime
                print(f"\n🔄 Change detected at {time.strftime('%H:%M:%S')}")
                
                if full:
                    sorted_items, orchestrator = run_full_sort(roadmap_path)
                else:
                    sorted_items, orchestrator = run_basic_sort(roadmap_path)
                
                print("\n📊 Top 5 Priorities:")
                for item in sorted_items[:5]:
                    print(f"   {item.rank}. {item.title} ({item.final_score:.2f})")
                
                # Write report
                script_dir = Path(__file__).parent
                if full:
                    report = orchestrator.generate_detailed_report(sorted_items)
                    output_path = script_dir / "BACKLOG_SORTED_DETAILED.md"
                else:
                    report = orchestrator.generate_report(sorted_items)
                    output_path = script_dir / "BACKLOG_SORTED.md"
                
                output_path.write_text(report)
                print(f"   Updated {output_path.name}")
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\n👋 Stopped watching.")


def main():
    parser = argparse.ArgumentParser(
        description="Multi-agent backlog sorter for Flow ROADMAP.md",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Agent Levels:
  --basic   5 agents  (Priority, Effort, Impact, Dependency, Risk)
  --full    10 agents (+ Compiler, UX, Platform, TechDebt, Marketing)
  --mega    25 agents (+ 15 specialized domain agents)
  --ultra   40 agents (+ 15 persona-based stakeholder agents)
        """
    )
    
    level_group = parser.add_mutually_exclusive_group()
    level_group.add_argument(
        "--basic", action="store_true", default=True,
        help="Use 5 core agents (default)"
    )
    level_group.add_argument(
        "--full", action="store_true",
        help="Use 10 agents with parallel execution"
    )
    level_group.add_argument(
        "--mega", action="store_true",
        help="Use 25 agents (core + extended + specialized)"
    )
    level_group.add_argument(
        "--ultra", action="store_true",
        help="Use ALL 40 agents including persona-based stakeholders"
    )
    level_group.add_argument(
        "--godmode", action="store_true",
        help="🔥 GODMODE: 60 agents including temporal and chaos agents"
    )
    level_group.add_argument(
        "--ludicrous", action="store_true",
        help="🚀 LUDICROUS: 90 agents including meta and philosophical agents"
    )
    
    parser.add_argument(
        "--watch", action="store_true",
        help="Watch ROADMAP.md and re-sort on changes"
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output JSON to stdout"
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true",
        help="Minimal output"
    )
    parser.add_argument(
        "--roadmap", type=Path,
        help="Path to ROADMAP.md (default: auto-detect)"
    )
    
    args = parser.parse_args()
    
    roadmap_path = args.roadmap or find_roadmap()
    
    if not roadmap_path.exists():
        print(f"Error: ROADMAP.md not found at {roadmap_path}", file=sys.stderr)
        sys.exit(1)
    
    if args.watch:
        watch_mode(roadmap_path, full=args.full)
        return
    
    # Determine which sort to run
    if args.ludicrous:
        results, orchestrator, output_name = run_ludicrous_sort(roadmap_path, quiet=args.quiet)
        report_method = "generate_ludicrous_report"
    elif args.godmode:
        results, orchestrator, output_name = run_godmode_sort(roadmap_path, quiet=args.quiet)
        report_method = "generate_godmode_report"
    elif args.ultra:
        results, orchestrator, output_name = run_ultra_sort(roadmap_path, quiet=args.quiet)
        report_method = "generate_ultra_report"
    elif args.mega:
        results, orchestrator, output_name = run_mega_sort(roadmap_path, quiet=args.quiet)
        report_method = "generate_mega_report"
    elif args.full:
        results, orchestrator, output_name = run_full_sort(roadmap_path, quiet=args.quiet)
        report_method = "generate_detailed_report"
    else:
        results, orchestrator, output_name = run_basic_sort(roadmap_path, quiet=args.quiet)
        report_method = "generate_report"
    
    if args.json:
        # Output JSON to stdout
        if hasattr(results[0], 'to_dict'):
            json_data = [item.to_dict() for item in results]
        else:
            # For mega/ultra results
            json_data = [
                {
                    "rank": r.rank,
                    "title": r.item.title,
                    "score": r.final_score,
                    "confidence": getattr(r, 'confidence', 0),
                }
                for r in results
            ]
        print(json.dumps(json_data, indent=2))
    else:
        # Generate and save report
        script_dir = Path(__file__).parent
        report = getattr(orchestrator, report_method)(results)
        output_path = script_dir / output_name
        
        output_path.write_text(report)
        
        if not args.quiet:
            print(f"\n📊 Report written to {output_path}")
            print("\n" + "=" * 50)
            print("TOP 5 PRIORITIES")
            print("=" * 50)
            for r in results[:5]:
                # Handle both BacklogItem and ConsensusResult/UltraResult
                if hasattr(r, 'item'):
                    title = r.item.title
                    score = r.final_score
                    rank = r.rank
                else:
                    title = r.title
                    score = r.final_score
                    rank = r.rank
                print(f"  {rank}. {title} ({score:.2f})")
            print("\n✅ Done!")


if __name__ == "__main__":
    main()
