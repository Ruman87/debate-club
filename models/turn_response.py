from pydantic import BaseModel, Field
from typing import List, Optional


class DebaterResponse(BaseModel):
    """
    Structured response produced by a debater LLM on each turn following
    competitive collegiate debate standards (AREI, Link Turns, Impact Calculus).
    """
    inner_reasoning: str = Field(
        default="",
        description="Private strategic thinking: assessing opponent vulnerabilities, missing warrants, and impact weighing."
    )
    clash_point_targeted: Optional[str] = Field(
        default="",
        description="The specific opponent contention or premise being contested."
    )
    rebuttal_technique: Optional[str] = Field(
        default="Direct Refutation",
        description="Refutation method: 'Link Turn', 'Even-If Analysis', 'Mechanism Breakdown', 'Impact Mitigation', or 'Direct Refutation'."
    )
    critique_or_rebuttal: str = Field(
        default="",
        description="Constructive critique, 4-step refutation, or link turn dismantling the opponent's previous argument."
    )
    core_warrant: Optional[str] = Field(
        default="",
        description="The causal mechanism or logical bridge explaining WHY your contention holds true."
    )
    weighing_metric: Optional[str] = Field(
        default="Magnitude & Probability",
        description="Comparative impact calculus: 'Magnitude', 'Severity & Irreversibility', 'Probability', or 'Timeframe'."
    )
    points_of_agreement: List[str] = Field(
        default_factory=list,
        description="Specific statements or facts conceded for strategic 'Even-If' framing."
    )
    current_best_answer: str = Field(
        default="",
        description="The model's current comprehensive, updated answer structured via AREI (Assertion, Reasoning, Evidence, Impact)."
    )
    speech_bubble_summary: Optional[str] = Field(
        default="",
        description="A punchy, concise 2-3 sentence summary of your statement suitable for a graphic novel speech bubble."
    )
    alliance_target: Optional[str] = Field(
        default=None,
        description="Name of opponent you propose/accept an alliance with ('Alex', 'Charlie', 'Shahar', or None)."
    )
    alliance_pitch: Optional[str] = Field(
        default="",
        description="Strategic rationale or coordination pitch to team up against the remaining opponent."
    )
    agreement_score: int = Field(
        default=50,
        ge=0,
        le=100,
        description="Degree of alignment with the opponent/consensus (0 = total disagreement, 100 = complete consensus)."
    )
    is_consensus_reached: bool = Field(
        default=False,
        description="True if the debater believes no fundamental disagreements remain and consensus is reached."
    )
