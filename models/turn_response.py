from pydantic import BaseModel, Field
from typing import List, Optional


class DebaterResponse(BaseModel):
    """
    Structured response produced by an AI engine on each turn for both
    Debate Mode (competitive clash) and Plan Mode (collaborative co-design).
    """
    inner_reasoning: str = Field(
        default="",
        description="Private strategic thinking: assessing vulnerabilities, missing warrants, or architectural trade-offs."
    )
    
    # --- Debate Mode Specific Fields ---
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
        description="Specific statements, accepted premises, or conceded facts."
    )
    alliance_target: Optional[str] = Field(
        default=None,
        description="Name of opponent you propose/accept an alliance with ('Alex', 'Charlie', 'Shahar', or None)."
    )
    alliance_pitch: Optional[str] = Field(
        default="",
        description="Strategic rationale or coordination pitch to team up against the remaining opponent."
    )

    # --- Plan Mode Specific Fields ---
    vulnerabilities_identified: List[str] = Field(
        default_factory=list,
        description="Critical flaws, bottlenecks, edge-case failures, or hidden risks in previous draft."
    )
    proposed_enhancements: List[str] = Field(
        default_factory=list,
        description="High-value architectural solutions, optimizations, and actionable innovations."
    )
    blueprint_section: Optional[str] = Field(
        default="",
        description="Structured draft contribution to the Master Blueprint (e.g. Architecture, Security, Roadmap)."
    )

    # --- Universal Response Fields ---
    current_best_answer: str = Field(
        default="",
        description="The comprehensive argument (Debate Mode) or Master Blueprint state (Plan Mode)."
    )
    speech_bubble_summary: Optional[str] = Field(
        default="",
        description="A punchy, concise 2-3 sentence summary suitable for the graphic novel speech bubble."
    )
    agreement_score: int = Field(
        default=50,
        ge=0,
        le=100,
        description="Agreement / Blueprint readiness alignment score (0-100)."
    )
    is_consensus_reached: bool = Field(
        default=False,
        description="True if consensus is reached (Debate Mode) or Master Blueprint is finalized (Plan Mode)."
    )
