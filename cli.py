"""
Command Line Interface (CLI) runner for Debate-Club.

Usage:
    python cli.py --question "Is P=NP?" --debater1 gpt-4o --debater2 claude-3-5-sonnet-latest
"""

import argparse
import sys
import os
from dotenv import load_dotenv
from debate.engine import DebateEngine

load_dotenv(override=True)


def main():
    parser = argparse.ArgumentParser(description="Debate-Club CLI: Multi-LLM Dialectic Deliberation")
    parser.add_argument(
        "--question", "-q",
        type=str,
        required=True,
        help="The question or topic for debate",
    )
    parser.add_argument(
        "--debater1", "-d1",
        type=str,
        default="gpt-4o",
        help="Model name for Debater 1 (Alpha)",
    )
    parser.add_argument(
        "--debater2", "-d2",
        type=str,
        default="claude-3-5-sonnet-latest",
        help="Model name for Debater 2 (Beta)",
    )
    parser.add_argument(
        "--debater3", "-d3",
        type=str,
        default="gemini-2.5-flash",
        help="Model name for Debater 3 (Gamma)",
    )
    parser.add_argument(
        "--num_debaters", "-n",
        type=int,
        choices=[2, 3],
        default=3,
        help="Number of debaters (2 or 3)",
    )
    parser.add_argument(
        "--devils_advocate",
        type=int,
        default=2,
        help="Index of debater to act as Devil's Advocate (0, 1, or 2). Set to -1 for none.",
    )
    parser.add_argument(
        "--mode", "-m",
        type=str,
        default="Dialectic Truth-Seeking",
        help="Debate philosophy/mode",
    )
    parser.add_argument(
        "--rounds", "-r",
        type=int,
        default=4,
        help="Max number of rounds",
    )

    args = parser.parse_args()

    print(f"\n========================================================")
    print(f"⚖️  DEBATE-CLUB: DIALECTIC DELIBERATION")
    print(f"========================================================")
    print(f"❓ Question: {args.question}")
    print(f"🔷 Debater 1: {args.debater1}")
    print(f"🟣 Debater 2: {args.debater2}")
    if args.num_debaters >= 3:
        print(f"🔥 Debater 3: {args.debater3} {'(Devil\'s Advocate)' if args.devils_advocate == 2 else ''}")
    print(f"🎭 Mode:      {args.mode}")
    print(f"⏱️ Max Rounds: {args.rounds}\n")

    da_idx = args.devils_advocate if args.devils_advocate in [0, 1, 2] else None

    engine = DebateEngine.create_default(
        question=args.question,
        debater1_model=args.debater1,
        debater2_model=args.debater2,
        debater3_model=args.debater3,
        num_debaters=args.num_debaters,
        devils_advocate_idx=da_idx,
        mode=args.mode,
        max_rounds=args.rounds,
    )

    def progress(p, text):
        print(f"[{int(p*100):>3}%] {text}")

    final_state = engine.run_all(progress)

    print("\n--------------------------------------------------------")
    print("📜 DEBATE TRANSCRIPT RECAP")
    print("--------------------------------------------------------")
    for turn in final_state.turns:
        print(f"\n[Round {turn.round_num}] {turn.debater_name} ({turn.model_name}):")
        if turn.response.critique_or_rebuttal:
            print(f"  • Critique: {turn.response.critique_or_rebuttal}")
        if turn.response.points_of_agreement:
            print(f"  • Agreed Points: {', '.join(turn.response.points_of_agreement)}")
        print(f"  • Proposed Answer: {turn.response.current_best_answer}")
        print(f"  • Agreement Score: {turn.response.agreement_score}% | Consensus: {turn.response.is_consensus_reached}")

    if final_state.final_verdict:
        print("\n========================================================")
        print("🏆 FINAL SYNTHESIZED VERDICT")
        print("========================================================")
        print(f"Status: {final_state.final_verdict.conclusion_reason}")
        print(f"Consensus Score: {final_state.final_verdict.final_consensus_score}%\n")
        print(final_state.final_verdict.summary_verdict)
        if final_state.final_verdict.agreed_points:
            print("\nAgreed Principles:")
            for pt in final_state.final_verdict.agreed_points:
                print(f"  ✓ {pt}")


if __name__ == "__main__":
    main()
