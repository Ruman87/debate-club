import logging
import re
from typing import List, Optional, Any
from interfaces.llms import LLM, extract_json_from_text
from models.debate_state import DebaterConfig, TurnRecord
from models.turn_response import DebaterResponse
from prompting.debater_prompts import (
    get_debater_system_prompt,
    get_debater_user_prompt,
)

logger = logging.getLogger(__name__)


class Debater:
    """
    Represents an active debating agent backed by a specific LLM and persona.
    """

    def __init__(self, config: DebaterConfig):
        self.config = config
        self.llm = LLM.for_model_name(config.model_name, config.temperature)

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def id(self) -> str:
        return self.config.id

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
    ) -> TurnRecord:
        """
        Executes a debate turn by prompting the LLM and parsing the structured response.
        """
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
        )

        logger.info(f"Debater {self.name} ({self.model_name}) thinking for Round {round_num}...")
        raw_response = self.llm.send(system_prompt, user_prompt)

        try:
            parsed_dict = extract_json_from_text(raw_response)
            response_obj = DebaterResponse(**parsed_dict)
        except Exception as e:
            logger.warning(f"Failed to parse JSON from {self.name}: {e}. Generating clean fallback response.")
            
            # Cleanly extract human speech text without JSON artifacts or codeblocks
            cleaned_text = raw_response or ""
            # Strip <think> tags
            cleaned_text = re.sub(r"<think>.*?</think>", "", cleaned_text, flags=re.DOTALL | re.IGNORECASE).strip()
            # Strip ```json fences
            cleaned_text = re.sub(r"```(?:json)?", "", cleaned_text).strip()
            
            # Extract key text if embedded in raw json string
            for key in ["speech_bubble_summary", "current_best_answer", "inner_reasoning", "critique_or_rebuttal"]:
                match = re.search(rf'"{key}"\s*:\s*"([^"]+)"', cleaned_text, flags=re.DOTALL)
                if match:
                    cleaned_text = match.group(1).replace('\\"', '"').replace('\\n', ' ').strip()
                    break
            else:
                cleaned_text = re.sub(r'[{}\[\]"]', '', cleaned_text).strip()

            response_obj = DebaterResponse(
                inner_reasoning="Model returned unformatted output; synthesized direct argument.",
                critique_or_rebuttal="Delivered direct counter-argument." if turn_index > 1 else "",
                points_of_agreement=[],
                current_best_answer=cleaned_text if cleaned_text else "Advocating for assigned debate mandate.",
                speech_bubble_summary=cleaned_text[:240] if cleaned_text else "Defending core proposition with conviction.",
                agreement_score=50,
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
