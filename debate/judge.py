"""
AI Judge Agent for Debate-Club.
Evaluates round deliberation, awards points for logic/rebuttals/rhetoric,
and announces round winners.
"""

import json
import logging
import re
from typing import List, Optional

from interfaces.llms import LLM
from models.debate_state import DebaterConfig, TurnRecord, JudgeRoundEvaluation, DebaterScore, ActiveAlliance
from prompting.judge_prompts import get_judge_system_prompt, get_judge_user_prompt

logger = logging.getLogger("debate_club.judge")


class Judge:
    """
    AI Judge that scores debaters round-by-round.
    """

    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.4):
        self.model_name = model_name
        self.temperature = temperature
        try:
            self.llm = LLM.for_model_name(model_name, temperature)
        except Exception as e:
            logger.warning(f"Could not load judge model {model_name}: {e}. Falling back to mock-debater-alpha.")
            self.llm = LLM.for_model_name("mock-debater-alpha", temperature)

    def evaluate_round(
        self,
        question: str,
        round_num: int,
        debaters: List[DebaterConfig],
        round_turns: List[TurnRecord],
        active_alliance: Optional[ActiveAlliance] = None,
    ) -> JudgeRoundEvaluation:
        """
        Evaluates all turns in a completed round and produces scores and commentary.
        """
        system_prompt = get_judge_system_prompt()
        user_prompt = get_judge_user_prompt(
            question=question,
            round_num=round_num,
            debaters=debaters,
            round_turns=round_turns,
            active_alliance=active_alliance,
        )

        try:
            raw_response = self.llm.send(system_prompt, user_prompt)
            return self._parse_evaluation(raw_response, round_num, debaters)
        except Exception as e:
            logger.error(f"Error during Judge round evaluation: {e}")
            return self._fallback_evaluation(round_num, debaters)

    def _parse_evaluation(
        self, raw_response: str, round_num: int, debaters: List[DebaterConfig]
    ) -> JudgeRoundEvaluation:
        try:
            cleaned = raw_response.strip()
            # Clean markdown code blocks if present
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            # Find json block
            match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
            if match:
                cleaned = match.group(1)

            data = json.loads(cleaned)

            scores = []
            for s in data.get("scores", []):
                debater_name = s.get("debater_name", "")
                logic = int(s.get("logic_score", 7))
                rebuttal = int(s.get("rebuttal_score", 7))
                rhetoric = int(s.get("rhetoric_score", 7))
                total = int(s.get("total_points", logic + rebuttal + rhetoric))
                feedback = s.get("feedback", "")
                clash = s.get("clash_won", "")
                scores.append(
                    DebaterScore(
                        debater_name=debater_name,
                        logic_score=logic,
                        rebuttal_score=rebuttal,
                        rhetoric_score=rhetoric,
                        total_points=total,
                        feedback=feedback,
                        clash_won=clash,
                    )
                )

            # Ensure all debaters have scores
            scored_names = {s.debater_name for s in scores}
            for d in debaters:
                if d.name not in scored_names:
                    scores.append(
                        DebaterScore(
                            debater_name=d.name,
                            logic_score=7,
                            rebuttal_score=7,
                            rhetoric_score=7,
                            total_points=21,
                            feedback="Solid defense of assigned stance.",
                            clash_won="Defended baseline premises",
                        )
                    )

            # Determine winner if not explicit
            winner = data.get("round_winner")
            if not winner or winner not in [d.name for d in debaters]:
                winner = max(scores, key=lambda x: x.total_points).debater_name

            dredd_q = data.get(
                "dredd_quote",
                f"I AM THE LAW! {winner} takes Round {round_num} with commanding legal and rhetorical force!",
            )

            return JudgeRoundEvaluation(
                round_num=round_num,
                scores=scores,
                round_winner=winner,
                dredd_quote=dredd_q,
                judge_commentary=data.get(
                    "judge_commentary",
                    f"{winner} led Round {round_num} with high rhetorical conviction and precise rebuttals.",
                ),
                strongest_argument=data.get(
                    "strongest_argument", "Key deductive argument defending assigned position."
                ),
                weakest_point=data.get("weakest_point", "Vulnerability in handling edge-case trade-offs."),
                key_clash_issue=data.get("key_clash_issue", "Core feasibility and systemic trade-offs"),
            )
        except Exception as e:
            logger.warning(f"Failed to parse Judge JSON output ({e}). Using robust fallback.")
            return self._fallback_evaluation(round_num, debaters)

    def _fallback_evaluation(
        self, round_num: int, debaters: List[DebaterConfig]
    ) -> JudgeRoundEvaluation:
        scores = []
        for i, d in enumerate(debaters):
            score_val = 8 if i == 0 else 7
            scores.append(
                DebaterScore(
                    debater_name=d.name,
                    logic_score=score_val,
                    rebuttal_score=score_val,
                    rhetoric_score=score_val,
                    total_points=score_val * 3,
                    feedback="Delivered a structured and rigorous argument.",
                )
            )

        winner = debaters[0].name if debaters else "Alex"
        return JudgeRoundEvaluation(
            round_num=round_num,
            scores=scores,
            round_winner=winner,
            dredd_quote=f"I AM THE LAW! {winner} takes Round {round_num} with decisive deductive power!",
            judge_commentary=f"Round {round_num} saw sharp clashes, with {winner} mounting a formidable case.",
            strongest_argument="Core thesis addressing the question with logical consistency.",
            weakest_point="Opportunities remain to explore deeper empirical nuances in the next round.",
        )
