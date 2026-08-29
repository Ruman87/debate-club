from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Any


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

    @field_validator(
        "inner_reasoning",
        "critique_or_rebuttal",
        "current_best_answer",
        "speech_bubble_summary",
        "core_warrant",
        "clash_point_targeted",
        mode="before"
    )
    @classmethod
    def coerce_str_fields(cls, v: Any) -> str:
        """Coerces dictionaries or nested objects returned by small local models into clean strings."""
        if v is None:
            return ""
        if isinstance(v, str):
            return v
        if isinstance(v, dict):
            # If model nested keys inside this field, extract the best matching subkey or join values
            for candidate in ["speech_bubble_summary", "current_best_answer", "summary", "content", "answer", "text"]:
                if candidate in v and isinstance(v[candidate], str):
                    return v[candidate]
            return " ".join(str(val) for val in v.values() if isinstance(val, (str, int, float)))
        if isinstance(v, (list, tuple)):
            return " ".join(str(item) for item in v)
        return str(v)

    @field_validator(
        "points_of_agreement",
        "vulnerabilities_identified",
        "proposed_enhancements",
        mode="before"
    )
    @classmethod
    def coerce_list_fields(cls, v: Any) -> List[str]:
        """Coerces strings or dictionaries into clean lists of strings."""
        if v is None:
            return []
        if isinstance(v, list):
            return [str(item) for item in v if item]
        if isinstance(v, str):
            if not v.strip():
                return []
            return [line.strip().lstrip("-•* ") for line in v.split("\n") if line.strip()]
        if isinstance(v, dict):
            return [f"{k}: {val}" for k, val in v.items() if val]
        return [str(v)]

    @field_validator("agreement_score", mode="before")
    @classmethod
    def coerce_score(cls, v: Any) -> int:
        """Clamps score integer within [0, 100]."""
        try:
            val = int(v)
            return max(0, min(100, val))
        except (ValueError, TypeError):
            return 50
