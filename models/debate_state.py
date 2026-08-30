from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from models.turn_response import DebaterResponse


class DebaterConfig(BaseModel):
    """
    Configuration and metadata for an individual debater.
    """
    id: str
    name: str
    model_name: str
    temperature: float = 0.7
    persona: str = "Dialectic Truth-Seeking"
    color: str = "#3B82F6"  # Hex color for UI badges/accents
    avatar: str = "🤖"
    image_path: Optional[str] = None
    is_devils_advocate: bool = False
    assigned_stance: str = ""
    stance_type: Literal["for", "against", "middle_ground", "architect", "stress_tester", "synthesizer"] = "for"


class TurnRecord(BaseModel):
    """
    Record of a single turn by a debater.
    """
    turn_id: int
    round_num: int
    debater_id: str
    debater_name: str
    model_name: str
    response: DebaterResponse
    timestamp: datetime = Field(default_factory=datetime.now)


class DebaterScore(BaseModel):
    """
    Score breakdown for an individual debater in a single round (WUDC / BP competition standard).
    """
    debater_name: str
    logic_score: int = Field(default=7, ge=0, le=10, description="Mechanistic Warrants & Logic (0-10)")
    rebuttal_score: int = Field(default=7, ge=0, le=10, description="Clash, Link Turns & Rebuttal Precision (0-10)")
    rhetoric_score: int = Field(default=7, ge=0, le=10, description="Comparative Weighing & Impact Calculus (0-10)")
    total_points: int = 21
    feedback: str = ""
    clash_won: Optional[str] = ""


class JudgeRoundEvaluation(BaseModel):
    """
    Evaluation and point allocation produced by Supreme Judge Dredd for a completed round.
    """
    round_num: int
    scores: List[DebaterScore] = Field(default_factory=list)
    round_winner: str = ""
    dredd_quote: str = ""
    judge_commentary: str = ""
    strongest_argument: str = ""
    weakest_point: str = ""
    key_clash_issue: Optional[str] = ""


class ActiveAlliance(BaseModel):
    """
    Record of an established alliance between two debaters against a third.
    """
    round_num: int
    debater_a: str
    debater_b: str
    target_debater: str
    is_active: bool = True
    status_message: str = ""


class FinalVerdict(BaseModel):
    """
    Synthesized outcome of the entire debate produced by Supreme Judge Dredd.
    """
    summary_verdict: str
    agreed_points: List[str] = Field(default_factory=list)
    remaining_nuances: List[str] = Field(default_factory=list)
    final_consensus_score: int = 100
    conclusion_reason: str = "Consensus reached"
    grand_winner: Optional[str] = None
    dredd_final_decree: Optional[str] = None


class UserIntervention(BaseModel):
    """
    Cross-examination question or constraint injected by the audience / user mid-session.
    """
    round_num: int
    question: str
    target_debater: Optional[str] = "All"
    timestamp: datetime = Field(default_factory=datetime.now)


class DebateState(BaseModel):
    """
    Complete state of an ongoing or completed debate or planning brainstorm session.
    """
    question: str
    app_mode: str = "debate"  # 'debate' (Competitive Arena) or 'plan' (Collaborative Mastermind)
    mode: str = "Dialectic Truth-Seeking"
    max_rounds: int = 4
    current_round: int = 1
    current_turn_index: int = 0
    debaters: List[DebaterConfig] = Field(default_factory=list)
    turns: List[TurnRecord] = Field(default_factory=list)
    user_interventions: List[UserIntervention] = Field(default_factory=list)
    status: str = "idle"  # 'idle', 'in_progress', 'consensus_reached', 'max_rounds_reached', 'stalemate', 'plan_finalized'
    
    # Debate Mode: Judge & Competitive Mechanics
    judge_model: str = "gpt-4o-mini"
    round_evaluations: List[JudgeRoundEvaluation] = Field(default_factory=list)
    active_alliances: List[ActiveAlliance] = Field(default_factory=list)
    cumulative_scores: Dict[str, int] = Field(default_factory=dict)
    grand_winner: Optional[str] = None
    final_verdict: Optional[FinalVerdict] = None

    # Plan Mode: Collaborative Mastermind Mechanics
    master_plan: Optional[str] = None
    plan_readiness_score: int = 0

    def get_latest_turn(self) -> Optional[TurnRecord]:
        if self.turns:
            return self.turns[-1]
        return None

    def get_turns_for_round(self, round_num: int) -> List[TurnRecord]:
        return [t for t in self.turns if t.round_num == round_num]

    def get_active_alliance(self) -> Optional[ActiveAlliance]:
        for a in reversed(self.active_alliances):
            if a.is_active:
                return a
        return None

    def is_finished(self) -> bool:
        return self.status not in ["idle", "in_progress"]

    def get_agreement_history(self) -> List[Dict]:
        history = []
        for r in range(1, self.current_round + 1):
            r_turns = self.get_turns_for_round(r)
            if r_turns:
                avg = sum(t.response.agreement_score for t in r_turns) / len(r_turns)
                history.append({"round": r, "average_agreement": avg})
        return history
