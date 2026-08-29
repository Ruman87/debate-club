import logging
from typing import List, Tuple
from interfaces.llms import LLM, extract_json_from_text
from models.debate_state import FinalVerdict, TurnRecord, DebateState
from prompting.moderator_prompts import get_moderator_synthesis_prompt

logger = logging.getLogger(__name__)


class Moderator:
    """
    Evaluates consensus conditions, detects stalemates, and synthesizes final verdicts.
    """

    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.3):
        self.model_name = model_name
        self.llm = LLM.for_model_name(model_name, temperature)

    def check_termination(
        self,
        state: DebateState,
    ) -> Tuple[bool, str]:
        """
        Evaluates whether debate should terminate based on success criteria:
        1. All debaters declare consensus (is_consensus_reached is True)
        2. High agreement threshold (average score >= 90% in current round)
        3. Max rounds reached
        4. Stalemate detected (flat agreement score for multiple rounds)
        """
        if not state.turns:
            return False, "Debate not started"

        # Check latest completed round
        current_round_turns = state.get_turns_for_round(state.current_round)
        
        # Condition 1 & 2: If everyone in current round has had a turn
        if len(current_round_turns) == len(state.debaters) and len(current_round_turns) > 0:
            all_agree = all(t.response.is_consensus_reached for t in current_round_turns)
            avg_score = sum(t.response.agreement_score for t in current_round_turns) / len(current_round_turns)

            if all_agree or avg_score >= 90:
                return True, f"Consensus achieved with {avg_score:.1f}% agreement"

            # Check stalemate (if 3+ rounds and no improvement)
            if state.current_round >= 3:
                history = state.get_agreement_history()
                if len(history) >= 2:
                    score_diff = abs(history[-1]["average_agreement"] - history[-2]["average_agreement"])
                    if score_diff < 3 and avg_score < 70:
                        return True, "Stalemate detected: perspectives remain divergent"

        # Condition 3: Max rounds limit reached
        if state.current_round > state.max_rounds or (
            state.current_round == state.max_rounds
            and len(current_round_turns) == len(state.debaters)
        ):
            return True, f"Maximum rounds ({state.max_rounds}) reached"

        return False, "In progress"

    def synthesize_verdict(
        self,
        state: DebateState,
        termination_reason: str,
    ) -> FinalVerdict:
        """
        Prompts the moderator model to construct the synthesized final conclusion.
        """
        prompt = get_moderator_synthesis_prompt(
            question=state.question,
            turns=state.turns,
            termination_reason=termination_reason,
        )

        try:
            raw_response = self.llm.send(
                system_prompt="You are an expert impartial debate moderator.",
                user_prompt=prompt,
                max_tokens=1500,
            )
            parsed = extract_json_from_text(raw_response)
            return FinalVerdict(**parsed)
        except Exception as e:
            logger.error(f"Moderator synthesis failed: {e}. Fallback to latest best answer.")
            latest = state.get_latest_turn()
            fallback_answer = latest.response.current_best_answer if latest else "No resolution reached."
            return FinalVerdict(
                summary_verdict=fallback_answer,
                agreed_points=["Debate concluded according to round limits"],
                remaining_nuances=[],
                final_consensus_score=latest.response.agreement_score if latest else 50,
                conclusion_reason=termination_reason,
            )
