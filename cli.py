"""
Command Line Interface (CLI) runner for Debate-Club.
Supports both Debate Mode (Competitive Arena with Supreme Judge Dredd)
and Plan Mode (Collaborative Multi-Engine Mastermind & Master Blueprint Synthesis).

Usage:
    # Debate Mode
    python cli.py --question "Is P=NP?" --debater1 gpt-4o --debater2 claude-3-5-sonnet-latest --judge gpt-4o-mini

    # Plan Mode (Brainstorming)
    python cli.py --app_mode plan --question "Design a viral B2B AI agent launch" --num_engines 3 --rounds 3
"""

import argparse
import sys
import os
import json
from dotenv import load_dotenv
from debate.engine import DebateEngine

load_dotenv(override=True)

# ANSI Color Codes
CYAN = "\033[96m"
BLUE = "\033[94m"
PURPLE = "\033[95m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"


def main():
    parser = argparse.ArgumentParser(description="Debate-Club CLI: Multi-LLM Arena & Mastermind")
    parser.add_argument(
        "--app_mode", "-a",
        type=str,
        choices=["debate", "plan"],
        default="debate",
        help="Operational mode: 'debate' (Competitive Arena) or 'plan' (Collaborative Mastermind)",
    )
    parser.add_argument(
        "--question", "-q",
        type=str,
        required=True,
        help="The motion for debate or objective for brainstorming",
    )
    parser.add_argument(
        "--debater1", "-d1",
        type=str,
        default="gpt-4o",
        help="Model name for Engine 1 (Alex - Lead Architect / PRO)",
    )
    parser.add_argument(
        "--debater2", "-d2",
        type=str,
        default="gemini-2.5-flash",
        help="Model name for Engine 2 (Charlie - Stress-Tester / CON)",
    )
    parser.add_argument(
        "--debater3", "-d3",
        type=str,
        default="ollama/qwen2.5:latest",
        help="Model name for Engine 3 (Shahar - Synthesizer)",
    )
    parser.add_argument(
        "--num_engines", "-n",
        type=int,
        choices=[2, 3],
        default=3,
        help="Number of engines in session (2 or 3)",
    )
    parser.add_argument(
        "--judge", "-j",
        type=str,
        default="gpt-4o-mini",
        help="Model for Supreme Judge Dredd (Debate Mode only)",
    )
    parser.add_argument(
        "--philosophy", "-p",
        type=str,
        default="Competitive Dialectic",
        help="Debate philosophy",
    )
    parser.add_argument(
        "--rounds", "-r",
        type=int,
        default=3,
        help="Max number of rounds / iterations",
    )
    parser.add_argument(
        "--export", "-o",
        type=str,
        default=None,
        help="Optional output filepath to save final transcript/blueprint (.json or .md)",
    )

    args = parser.parse_args()
    is_plan = args.app_mode == "plan"

    print(f"\n{BOLD}{CYAN}========================================================{RESET}")
    if is_plan:
        print(f"{BOLD}{GREEN}📋 DEBATE-CLUB: COLLABORATIVE MASTERMIND (PLAN MODE){RESET}")
    else:
        print(f"{BOLD}{YELLOW}⚖️  DEBATE-CLUB: COMPETITIVE DIALECTIC ARENA{RESET}")
    print(f"{BOLD}{CYAN}========================================================{RESET}")
    print(f"{BOLD}🎯 Objective / Topic:{RESET} {args.question}")
    print(f"{BLUE}🔷 Engine 1 (Alex):{RESET}    {args.debater1}")
    print(f"{PURPLE}🟣 Engine 2 (Charlie):{RESET} {args.debater2}")
    if args.num_engines >= 3:
        print(f"{RED}🔥 Engine 3 (Shahar):{RESET}  {args.debater3}")
    if not is_plan:
        print(f"{YELLOW}⚖️  Supreme Judge:{RESET}      {args.judge}")
    print(f"⏱️  Max Rounds:{RESET}        {args.rounds}\n")

    # Initialize Engine
    if is_plan:
        engine = DebateEngine.create_plan_mode(
            objective=args.question,
            engine1_model=args.debater1,
            engine2_model=args.debater2,
            engine3_model=args.debater3 if args.num_engines >= 3 else None,
            num_engines=args.num_engines,
            max_rounds=args.rounds,
        )
    else:
        engine = DebateEngine.create_default(
            question=args.question,
            debater1_model=args.debater1,
            debater2_model=args.debater2,
            debater3_model=args.debater3 if args.num_engines >= 3 else None,
            num_debaters=args.num_engines,
            judge_model=args.judge,
            mode=args.philosophy,
            max_rounds=args.rounds,
        )

    # Stance and role summary
    print(f"{BOLD}👥 Assigned Roles & Mandates:{RESET}")
    for d in engine.state.debaters:
        color = BLUE if "alex" in d.name.lower() else PURPLE if "charlie" in d.name.lower() else RED
        print(f"  {color}• {d.name} ({d.model_name}){RESET}: [{d.stance_type.upper()}] {d.assigned_stance}")
    print()

    def progress(p, text):
        print(f"{CYAN}[{int(p*100):>3}%]{RESET} {text}")

    # Run deliberation
    final_state = engine.run_all(progress)

    print(f"\n{BOLD}{CYAN}--------------------------------------------------------{RESET}")
    print(f"{BOLD}📜 DELIBERATION TRANSCRIPT & TURNS{RESET}")
    print(f"{BOLD}{CYAN}--------------------------------------------------------{RESET}")

    for turn in final_state.turns:
        resp = turn.response
        color = BLUE if "alex" in turn.debater_name.lower() else PURPLE if "charlie" in turn.debater_name.lower() else RED
        
        print(f"\n{color}[{'Iteration' if is_plan else 'Round'} {turn.round_num}] {turn.debater_name} ({turn.model_name}):{RESET}")
        
        if is_plan:
            vulns = getattr(resp, "vulnerabilities_identified", [])
            enhs = getattr(resp, "proposed_enhancements", [])
            if vulns:
                print(f"  {RED}🔍 Risks Probed:{RESET} {'; '.join(vulns)}")
            if enhs:
                print(f"  {GREEN}🚀 Enhancements:{RESET} {'; '.join(enhs)}")
            print(f"  💬 Speech Summary: {resp.speech_bubble_summary}")
            print(f"  📊 Readiness: {resp.agreement_score}%")
        else:
            if resp.critique_or_rebuttal:
                tech = getattr(resp, "rebuttal_technique", "Refutation")
                print(f"  {PURPLE}💥 Rebuttal [{tech}]:{RESET} {resp.critique_or_rebuttal}")
            warrant = getattr(resp, "core_warrant", None)
            if warrant:
                print(f"  {BLUE}🧠 Causal Warrant:{RESET} {warrant}")
            if resp.points_of_agreement:
                print(f"  {GREEN}🤝 Strategic Concessions:{RESET} {', '.join(resp.points_of_agreement)}")
            print(f"  💬 Speech: {resp.speech_bubble_summary or resp.current_best_answer[:160]}...")
            print(f"  📊 Agreement Alignment: {resp.agreement_score}%")

    # Round Judge Evaluations (Debate Mode)
    if not is_plan and final_state.round_evaluations:
        print(f"\n{BOLD}{YELLOW}========================================================{RESET}")
        print(f"{BOLD}{YELLOW}⚖️  SUPREME JUDGE DREDD ADJUDICATION & SCORES{RESET}")
        print(f"{BOLD}{YELLOW}========================================================{RESET}")
        for r_eval in final_state.round_evaluations:
            print(f"\n{BOLD}⚖️ Round {r_eval.round_num} Decree • Winner: {r_eval.round_winner} 🏆{RESET}")
            print(f"  🏛️ Clash Point: {r_eval.key_clash_issue}")
            print(f"  \"{r_eval.dredd_quote}\"")
            for sc in r_eval.scores:
                print(f"    * {sc.debater_name}: Warrants={sc.logic_score}/10, Rebuttal={sc.rebuttal_score}/10, Weighing={sc.rhetoric_score}/10 -> Total: {sc.total_points} pts (Clash Won: {sc.clash_won})")

    # Final Output / Synthesis
    if is_plan and final_state.master_plan:
        print(f"\n{BOLD}{GREEN}========================================================{RESET}")
        print(f"{BOLD}{GREEN}📋 FINAL SYNTHESIZED MASTER BLUEPRINT{RESET}")
        print(f"{BOLD}{GREEN}========================================================{RESET}\n")
        print(final_state.master_plan)

        if args.export:
            out_file = args.export
            with open(out_file, "w") as f:
                f.write(final_state.master_plan)
            print(f"\n{GREEN}✅ Master Blueprint exported to: {out_file}{RESET}")

    elif not is_plan:
        print(f"\n{BOLD}{YELLOW}========================================================{RESET}")
        print(f"{BOLD}{YELLOW}👑 GRAND CHAMPION & FINAL VERDICT{RESET}")
        print(f"{BOLD}{YELLOW}========================================================{RESET}")
        if final_state.grand_winner:
            print(f"{BOLD}🏆 GRAND CHAMPION:{RESET} {final_state.grand_winner.upper()} ({final_state.cumulative_scores.get(final_state.grand_winner, 0)} pts)\n")
        if final_state.final_verdict:
            print(final_state.final_verdict.summary_verdict)

        if args.export:
            out_file = args.export
            with open(out_file, "w") as f:
                json.dump(final_state.model_dump(), f, default=str, indent=2)
            print(f"\n{GREEN}✅ Full transcript exported to: {out_file}{RESET}")


if __name__ == "__main__":
    main()
