import logging
import re
from typing import List, Optional, Any
from interfaces.llms import LLM, extract_json_from_text
from models.debate_state import DebaterConfig, TurnRecord
from models.turn_response import DebaterResponse
from interfaces.search import search_web_grounding, format_grounding_context
from prompting.debater_prompts import (
    get_debater_system_prompt,
    get_debater_user_prompt,
)
from prompting.plan_prompts import (
    get_plan_debater_system_prompt,
    get_plan_debater_user_prompt,
)

logger = logging.getLogger(__name__)


class Debater:
    """
    Represents an active debating or planning agent backed by a specific LLM and role.
    """

    def __init__(self, config: DebaterConfig):
        self.config = config
        self.llm = LLM.for_model_name(config.model_name)
        self._cached_grounding = None

    @property
    def id(self) -> str:
        return self.config.id

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def model_name(self) -> str:
        return self.config.model_name

    def make_turn(
        self,
        question: str,
        opponent_names: List[str],
        round_num: int,
        turn_index: int,
        past_turns: List[TurnRecord],
        mode: str = "Dialectic Truth-Seeking",
        active_alliance: Optional[Any] = None,
        app_mode: str = "debate",
        user_interventions: Optional[List[Any]] = None,
        grounding_enabled: bool = True,
        round_evaluations: Optional[List[Any]] = None,
    ) -> TurnRecord:
        """
        Executes a turn for either Debate Mode or Plan Mode by prompting the LLM and parsing structured response.
        """
        grounding_context = ""
        if grounding_enabled:
            if not self._cached_grounding:
                search_results = search_web_grounding(question, max_results=3)
                self._cached_grounding = format_grounding_context(search_results)
            grounding_context = self._cached_grounding

        if app_mode == "plan":
            system_prompt = get_plan_debater_system_prompt(
                debater_name=self.name,
                role_title=self.config.persona,
                partner_names=opponent_names,
                objective=question,
            )
            user_prompt = get_plan_debater_user_prompt(
                objective=question,
                debater_name=self.name,
                round_num=round_num,
                turn_index=turn_index,
                past_turns=past_turns,
            )
        else:
            system_prompt = get_debater_system_prompt(
                debater_name=self.name,
                opponent_names=opponent_names,
                persona=self.config.persona,
                mode=mode,
                assigned_stance=getattr(self.config, "assigned_stance", ""),
                stance_type=getattr(self.config, "stance_type", "for"),
            )
            user_prompt = get_debater_user_prompt(
                question=question,
                debater_name=self.name,
                round_num=round_num,
                turn_index=turn_index,
                past_turns=past_turns,
                active_alliance=active_alliance,
                user_interventions=user_interventions,
                grounding_context=grounding_context,
                round_evaluations=round_evaluations,
            )

        logger.info(f"Debater {self.name} ({self.model_name}) thinking for {'Iteration' if app_mode == 'plan' else 'Round'} {round_num} [{app_mode.upper()} MODE]...")
        raw_response = self.llm.send(system_prompt, user_prompt)

        try:
            parsed_dict = extract_json_from_text(raw_response)
            response_obj = DebaterResponse(**parsed_dict)
        except Exception as e:
            logger.warning(f"Failed to parse JSON from {self.name}: {e}. Generating clean fallback response.")
            
            # Cleanly extract human speech text without JSON artifacts or codeblocks
            cleaned_text = raw_response or ""
            cleaned_text = re.sub(r"<think>.*?</think>", "", cleaned_text, flags=re.DOTALL | re.IGNORECASE).strip()
            cleaned_text = re.sub(r"```(?:json)?", "", cleaned_text).strip()
            
            for key in ["speech_bubble_summary", "current_best_answer", "inner_reasoning", "critique_or_rebuttal", "blueprint_section"]:
                match = re.search(rf'"{key}"\s*:\s*"([^"]+)"', cleaned_text, flags=re.DOTALL)
                if match:
                    cleaned_text = match.group(1).replace('\\"', '"').replace('\\n', ' ').strip()
                    break
            else:
                cleaned_text = re.sub(r'[{}\[\]"]', '', cleaned_text).strip()

            response_obj = DebaterResponse(
                inner_reasoning="Model returned unformatted output; synthesized direct contribution.",
                critique_or_rebuttal="Identified key structural enhancements." if turn_index > 1 else "",
                points_of_agreement=[],
                current_best_answer=cleaned_text if cleaned_text else "Advancing core solution blueprint.",
                speech_bubble_summary=cleaned_text[:240] if cleaned_text else "Co-designing high-value architecture.",
                agreement_score=80 if app_mode == "plan" else 50,
                is_consensus_reached=False,
            )

        return TurnRecord(
            turn_id=turn_index,
            round_num=round_num,
            debater_id=self.id,
            debater_name=self.name,
            model_name=self.model_name,
            response=response_obj,
        )
