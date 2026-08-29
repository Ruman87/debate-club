from prompting.debater_prompts import (
    get_debater_system_prompt,
    get_debater_user_prompt,
    DEBATE_PERSONA_GUIDELINES,
)
from prompting.moderator_prompts import get_moderator_synthesis_prompt

__all__ = [
    "get_debater_system_prompt",
    "get_debater_user_prompt",
    "DEBATE_PERSONA_GUIDELINES",
    "get_moderator_synthesis_prompt",
]
