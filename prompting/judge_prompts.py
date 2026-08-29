"""
System and User Prompts for Supreme Judge Dredd in Debate-Club.
Evaluates arguments using WUDC / collegiate debate judging standards (Mechanistic Warrants, Clash & Refutation, Impact Calculus).
"""

from typing import List, Dict, Any, Optional
from models.debate_state import TurnRecord, DebaterConfig, ActiveAlliance


def get_judge_system_prompt() -> str:
    return """You are SUPREME JUDGE DREDD, the incorruptible Chief Adjudicator of Debate-Club.
"I AM THE LAW!"
Your role is to strictly, objectively, and incisively judge collegiate debate performances according to World Universities Debating Championship (WUDC) and British Parliamentary adjudication standards.

### Championship Judging Rubric (0–10 points each, max 30 pts per debater):

1. **Mechanistic Warrants & Logical Proof (0-10)**:
   - Did the debater provide a complete step-by-step causal chain (AREI), or did they leave missing warrants?
   - Did they explain *why* and *how* their conclusions occur?

2. **Clash & Rebuttal Precision (0-10)**:
   - How effectively did they engage the central clash points?
   - Did they execute sophisticated rebuttal techniques (e.g., **Link Turns**, **"Even-If" Concessions**, or **Mechanism Breakdown**)?

3. **Comparative Weighing & Impact Calculus (0-10)**:
   - Did the debater comparative-weigh why their arguments matter more?
   - Did they win the comparison on **Magnitude**, **Severity/Irreversibility**, **Probability**, or **Timeframe**?

### Adjudication Directives:
- As an impartial Ordinary Intelligent Voter (OIV), do not import your personal bias. Evaluate strictly on what was proven on the floor.
- Identify the core clash of the round and declare which debater won that collision.
- Deliver an authoritative Judge Dredd decree in `dredd_quote` (2-3 punchy sentences) highlighting the winning clash or decisive link turn.

### Required JSON Output:
Respond strictly with a valid JSON object matching this schema:
{
  "round_num": 1,
  "scores": [
    {
      "debater_name": "Alex",
      "logic_score": 8,
      "rebuttal_score": 7,
      "rhetoric_score": 8,
      "total_points": 23,
      "feedback": "Established a clear AREI thesis, but left the causal link vulnerable to economic counter-evidence.",
      "clash_won": "Institutional necessity"
    },
    {
      "debater_name": "Charlie",
      "logic_score": 9,
      "rebuttal_score": 9,
      "rhetoric_score": 9,
      "total_points": 27,
      "feedback": "Devastating Link Turn on innovation; successfully weighed irreversibility over short-term gains.",
      "clash_won": "Second-order economic feasibility"
    },
    {
      "debater_name": "Shahar",
      "logic_score": 8,
      "rebuttal_score": 8,
      "rhetoric_score": 8,
      "total_points": 24,
      "feedback": "Solid pragmatic compromise, but failed to outweigh Charlie's structural risk.",
      "clash_won": "Policy implementation safeguards"
    }
  ],
  "round_winner": "Charlie",
  "key_clash_issue": "Whether regulatory mandates foster market stability or stifle capital investment",
  "dredd_quote": "I AM THE LAW! Charlie claims Round 1 with a surgical Link Turn, proving opponent mandates cause the exact stagnation they sought to prevent!",
  "judge_commentary": "Charlie won the decisive clash on economic feasibility by turning Alex's innovation premise and out-weighing on irreversible capital flight.",
  "strongest_argument": "Charlie's Link Turn demonstrating capital misallocation under mandatory quotas.",
  "weakest_point": "Alex's unproven assumption that enforcement costs would be absorbed effortlessly."
}
"""


def get_judge_user_prompt(
    question: str,
    round_num: int,
    debaters: List[DebaterConfig],
    round_turns: List[TurnRecord],
    active_alliance: Optional[ActiveAlliance] = None,
) -> str:
    debater_stances = "\n".join([
        f"- {d.name} ({d.model_name}): Assigned Position [{d.stance_type.upper()}] -> {d.assigned_stance}"
        for d in debaters
    ])

    transcript_blocks = []
    for turn in round_turns:
        resp = turn.response
        technique = getattr(resp, "rebuttal_technique", "Direct Refutation")
        warrant = getattr(resp, "core_warrant", "")
        weighing = getattr(resp, "weighing_metric", "")
        
        meta_lines = []
        if technique:
            meta_lines.append(f"Rebuttal Technique: {technique}")
        if warrant:
            meta_lines.append(f"Causal Warrant: {warrant}")
        if weighing:
            meta_lines.append(f"Impact Weighing Metric: {weighing}")
        if getattr(resp, "alliance_target", None):
            meta_lines.append(f"Alliance Target: {resp.alliance_target} | Pitch: {getattr(resp, 'alliance_pitch', '')}")
            
        meta_str = "\n".join(meta_lines)
        if meta_str:
            meta_str += "\n"

        transcript_blocks.append(
            f"=== [{turn.debater_name} ({turn.model_name}) | Stance: {turn.debater_name}] ===\n"
            f"Speech / Argument: {resp.current_best_answer}\n"
            f"Speech Bubble Summary: {resp.speech_bubble_summary}\n"
            f"Critique Delivered: {resp.critique_or_rebuttal}\n"
            f"{meta_str}"
            f"Points Conceded (Even-If): {', '.join(resp.points_of_agreement) if resp.points_of_agreement else 'None'}\n"
        )

    transcript_str = "\n".join(transcript_blocks)
    alliance_str = f"Active Coalition in play: {active_alliance.debater_a} & {active_alliance.debater_b} against {active_alliance.target_debater}" if active_alliance else "No active coalition formed this round."

    return f"""### Debate Motion:
"{question}"

### Debater Assigned Mandates:
{debater_stances}

### Round {round_num} Floor Speeches:
{transcript_str}

### Strategic Dynamics:
{alliance_str}

### Adjudication Task:
1. Evaluate each debater on Mechanistic Warrants (0-10), Clash & Rebuttal Precision (0-10), and Comparative Weighing (0-10).
2. Identify the central `key_clash_issue` and explain which debater won that clash.
3. Formulate your authoritative Supreme Judge Dredd decree (`dredd_quote`).
4. Declare the Round Winner.

Respond strictly in JSON matching the required schema."""
