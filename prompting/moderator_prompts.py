from typing import List
from models.debate_state import TurnRecord


def get_moderator_synthesis_prompt(
    question: str,
    turns: List[TurnRecord],
    termination_reason: str,
) -> str:
    """
    Constructs the prompt for the Moderator LLM to synthesize the final verdict.
    """
    transcript_blocks = []
    for turn in turns:
        transcript_blocks.append(
            f"--- Round {turn.round_num}: {turn.debater_name} ({turn.model_name}) ---\n"
            f"Critique / Rebuttal: {turn.response.critique_or_rebuttal}\n"
            f"Points of Agreement: {', '.join(turn.response.points_of_agreement)}\n"
            f"Proposed Answer: {turn.response.current_best_answer}\n"
            f"Agreement Score: {turn.response.agreement_score}%\n"
        )
    transcript_str = "\n\n".join(transcript_blocks)

    return f"""You are the Chief Moderator and Arbiter of Debate-Club.
A multi-LLM debate has just concluded on the following question:

Question:
"{question}"

Reason for Debate Conclusion: {termination_reason}

Full Debate Transcript:
{transcript_str}

### Your Task:
Synthesize the definitive verdict of this deliberation into a structured, clear summary.

You MUST respond strictly with a valid JSON object matching this schema:
{{
  "summary_verdict": "The clear, authoritative, synthesized answer agreed upon by the debate (or the best synthesis of the dominant arguments if rounds ended).",
  "agreed_points": [
    "Key agreed takeaway or principle #1",
    "Key agreed takeaway or principle #2"
  ],
  "remaining_nuances": [
    "Any subtle trade-offs, edge cases, or perspectives that remained distinct"
  ],
  "final_consensus_score": 95,
  "conclusion_reason": "{termination_reason}"
}}

Respond strictly in JSON with no extra text."""
