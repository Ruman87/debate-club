"""
Debate Engine for Debate-Club.
Orchestrates debater turns, dynamic assigned stances, Outsmart-style 2-vs-1 alliances,
and round-by-round AI Judge scoring.
"""

import logging
from typing import List, Optional, Callable, Dict
from models.debate_state import (
    DebateState,
    DebaterConfig,
    TurnRecord,
    JudgeRoundEvaluation,
    ActiveAlliance,
    FinalVerdict,
)
from debate.debater import Debater
from debate.moderator import Moderator
from debate.judge import Judge
from debate.history_manager import save_session
from prompting.stance_generator import generate_assigned_stances, assess_topic_complexity

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[float, str], None]


class DebateEngine:
    """
    Central coordinator managing the debate lifecycle, assigned positions,
    strategic alliances, and AI Judge scoring.
    """

    def __init__(
        self,
        state: DebateState,
        moderator_model: Optional[str] = None,
        judge_model: Optional[str] = None,
    ):
        self.state = state
        self.debaters = [Debater(cfg) for cfg in state.debaters]
        self.debater_map = {d.id: d for d in self.debaters}

        mod_model = moderator_model or (
            state.debaters[0].model_name if state.debaters else "gpt-4o-mini"
        )
        self.moderator = Moderator(model_name=mod_model)

        judge_m = judge_model or getattr(state, "judge_model", "gpt-4o-mini")
        self.judge = Judge(model_name=judge_m)

    @classmethod
    def create_default(
        cls,
        question: str,
        debater1_model: str = "gpt-4o",
        debater2_model: str = "gemini-3.6-flash",
        debater3_model: Optional[str] = "ollama/qwen2.5:latest",
        debater1_persona: str = "Dialectic Truth-Seeking",
        debater2_persona: str = "Dialectic Truth-Seeking",
        debater3_persona: str = "Middle Ground & Synthesis",
        num_debaters: Optional[int] = None,
        judge_model: str = "gpt-4o-mini",
        mode: str = "Competitive Dialectic",
        max_rounds: int = 3,
    ) -> "DebateEngine":
        """
        Factory method initializing debate with dynamically assigned stances for Alex, Charlie, and Shahar.
        The Judge Engine automatically determines whether 2 or 3 debaters are optimal based on topic complexity.
        """
        # Automatically assess complexity if not provided
        if num_debaters is None:
            num_debaters = assess_topic_complexity(question)

        # Fallback to 2 if debater 3 model is absent
        if num_debaters >= 3 and not debater3_model:
            num_debaters = 2

        # Generate bespoke assigned stances
        stances = generate_assigned_stances(question, num_debaters)
        debaters = []

        # Debater 1 (Alex - Blue - FOR)
        alex_stance = stances.get("Alex", {})
        debaters.append(
            DebaterConfig(
                id="debater_1",
                name="Alex",
                model_name=debater1_model,
                persona=debater1_persona,
                color="#3B82F6",  # Electric Blue
                avatar="🔷",
                image_path="assets/alex.jpg",
                assigned_stance=alex_stance.get("mandate", "Argue firmly in favor (PRO)."),
                stance_type=alex_stance.get("stance_type", "for"),
                is_devils_advocate=False,
            )
        )

        # Debater 2 (Charlie - Purple - AGAINST)
        charlie_stance = stances.get("Charlie", {})
        debaters.append(
            DebaterConfig(
                id="debater_2",
                name="Charlie",
                model_name=debater2_model,
                persona=debater2_persona,
                color="#A855F7",  # Amethyst Purple
                avatar="🟣",
                image_path="assets/charlie.jpg",
                assigned_stance=charlie_stance.get("mandate", "Argue firmly against (CON)."),
                stance_type=charlie_stance.get("stance_type", "against"),
                is_devils_advocate=False,
            )
        )

        # Debater 3 (Shahar - Red - MIDDLE GROUND) if 3 debaters selected
        if num_debaters >= 3 and debater3_model:
            shahar_stance = stances.get("Shahar", {})
            debaters.append(
                DebaterConfig(
                    id="debater_3",
                    name="Shahar",
                    model_name=debater3_model,
                    persona=debater3_persona,
                    color="#EF4444",  # Crimson Red
                    avatar="🔥",
                    image_path="assets/shahar.jpg",
                    assigned_stance=shahar_stance.get("mandate", "Argue for a structured middle ground/synthesis."),
                    stance_type=shahar_stance.get("stance_type", "middle_ground"),
                    is_devils_advocate=(debater3_persona == "Devil's Advocate"),
                )
            )

        # Initialize cumulative scores
        cum_scores = {d.name: 0 for d in debaters}

        state = DebateState(
            question=question,
            mode=mode,
            max_rounds=max_rounds,
            current_round=1,
            current_turn_index=0,
            debaters=debaters,
            status="in_progress",
            judge_model=judge_model,
            cumulative_scores=cum_scores,
        )
        return cls(state, judge_model=judge_model)

    def is_finished(self) -> bool:
        return self.state.status not in ["idle", "in_progress"]

    def _evaluate_alliances(self, round_turns: List[TurnRecord]):
        """
        Detects mutual non-polar alliance proposals among debaters.
        Note: Pure polar opposites (FOR vs AGAINST) cannot ally against the Middle Ground.
        """
        if len(self.debaters) < 3:
            return

        turn_proposals: Dict[str, str] = {}
        for turn in round_turns:
            target = getattr(turn.response, "alliance_target", None)
            if target and target.strip():
                turn_proposals[turn.debater_name] = target.strip()

        # Check for mutual non-polar match:
        # Shahar (MIDDLE_GROUND) + Alex (FOR) OR Shahar (MIDDLE_GROUND) + Charlie (AGAINST)
        found_alliance = False
        valid_non_polar_pairs = [("Charlie", "Shahar"), ("Alex", "Shahar")]
        for debater_a, debater_b in valid_non_polar_pairs:
            if (
                turn_proposals.get(debater_a) == debater_b
                and turn_proposals.get(debater_b) == debater_a
            ):
                all_names = {d.name for d in self.debaters}
                target_debater = list(all_names - {debater_a, debater_b})[0]
                
                alliance_record = ActiveAlliance(
                    round_num=self.state.current_round,
                    debater_a=debater_a,
                    debater_b=debater_b,
                    target_debater=target_debater,
                    is_active=True,
                    status_message=f"🤝 Strategic Coalition Formed: {debater_a} and {debater_b} have allied on common ground against {target_debater}!",
                )
                self.state.active_alliances.append(alliance_record)
                logger.info(f"Mutual non-polar alliance formed: {debater_a} + {debater_b} vs {target_debater}")
                found_alliance = True
                break

        if not found_alliance:
            # Mark previous alliances inactive if no mutual renewal
            for a in self.state.active_alliances:
                if a.round_num < self.state.current_round:
                    a.is_active = False

    @classmethod
    def create_plan_mode(
        cls,
        objective: str,
        engine1_model: str = "gpt-4o",
        engine2_model: str = "gemini-3.6-flash",
        engine3_model: Optional[str] = "ollama/qwen2.5:latest",
        num_engines: int = 3,
        max_rounds: int = 3,
    ) -> "DebateEngine":
        """
        Factory method initializing Plan Mode for collaborative mastermind brainstorming.
        User selects between 2 or 3 engines. No Judge is involved.
        """
        debaters = []

        # Engine 1 (Alex - Lead Architect)
        debaters.append(
            DebaterConfig(
                id="debater_1",
                name="Alex",
                model_name=engine1_model,
                persona="Lead Architect & Visionary",
                color="#3B82F6",
                avatar="🔷",
                image_path="assets/alex.jpg",
                assigned_stance="Lead Architect: Formulates foundational vision, core workflows, and architectural framework.",
                stance_type="architect",
            )
        )

        # Engine 2 (Charlie - Chief Risk & Stress-Tester)
        debaters.append(
            DebaterConfig(
                id="debater_2",
                name="Charlie",
                model_name=engine2_model,
                persona="Chief Risk & Stress-Tester (Red Team)",
                color="#A855F7",
                avatar="🟣",
                image_path="assets/charlie.jpg",
                assigned_stance="Chief Risk & Stress-Tester: Probes hidden bottlenecks, failure modes, costs, and provides concrete remedies.",
                stance_type="stress_tester",
            )
        )

        # Engine 3 (Shahar - Systems Synthesizer) if 3 engines chosen
        if num_engines >= 3 and engine3_model:
            debaters.append(
                DebaterConfig(
                    id="debater_3",
                    name="Shahar",
                    model_name=engine3_model,
                    persona="Systems Synthesizer & Execution Lead",
                    color="#EF4444",
                    avatar="🔥",
                    image_path="assets/shahar.jpg",
                    assigned_stance="Systems Synthesizer: Unifies trade-offs, operational milestones, and scaling optimizations.",
                    stance_type="synthesizer",
                )
            )

        state = DebateState(
            question=objective,
            app_mode="plan",
            mode="Collaborative Mastermind",
            max_rounds=max_rounds,
            current_round=1,
            current_turn_index=0,
            debaters=debaters,
            status="in_progress",
            plan_readiness_score=60,
        )
        return cls(state)

    def _synthesize_master_plan(self):
        """Compiles the finalized Master Blueprint document using the lead architect model."""
        from prompting.plan_prompts import get_master_plan_synthesis_prompt
        prompt = get_master_plan_synthesis_prompt(self.state.question, self.state.turns)
        lead_llm = self.debaters[0].llm
        try:
            raw_doc = lead_llm.send(
                system_prompt="You are an elite enterprise architect compiling a Master Blueprint.",
                user_prompt=prompt,
                max_tokens=2500,
            )
            self.state.master_plan = raw_doc.strip()
        except Exception as e:
            logger.error(f"Error compiling Master Blueprint: {e}")
            self.state.master_plan = self.state.turns[-1].response.current_best_answer if self.state.turns else "Master blueprint synthesized."

    def step_turn(self, progress: Optional[ProgressCallback] = None) -> Optional[TurnRecord]:
        """
        Executes exactly one turn by the next scheduled debater / mastermind engine.
        """
        if self.is_finished():
            return None

        debater_idx = self.state.current_turn_index % len(self.debaters)
        debater = self.debaters[debater_idx]
        opponent_names = [d.name for d in self.debaters if d.id != debater.id]

        role_label = debater.config.persona
        if progress:
            progress(
                0.2,
                f"Iteration {self.state.current_round}: {debater.name} ({debater.model_name}) is co-designing as [{role_label}]..."
                if self.state.app_mode == "plan"
                else f"Round {self.state.current_round}: {debater.name} ({debater.model_name}) presenting stance [{debater.config.stance_type.upper()}]...",
            )

        active_alliance = self.state.get_active_alliance() if self.state.app_mode == "debate" else None

        turn_record = debater.make_turn(
            question=self.state.question,
            opponent_names=opponent_names,
            round_num=self.state.current_round,
            turn_index=len(self.state.turns) + 1,
            past_turns=self.state.turns,
            mode=self.state.mode,
            active_alliance=active_alliance,
            app_mode=self.state.app_mode,
            user_interventions=self.state.user_interventions,
        )

        self.state.turns.append(turn_record)
        self.state.current_turn_index += 1

        # === PLAN MODE ITERATION HANDLING ===
        if self.state.app_mode == "plan":
            recent_scores = [t.response.agreement_score for t in self.state.turns[-len(self.debaters):]]
            if recent_scores:
                self.state.plan_readiness_score = int(sum(recent_scores) / len(recent_scores))

            if self.state.current_turn_index % len(self.debaters) == 0:
                if self.state.current_round >= self.state.max_rounds:
                    self.state.status = "plan_finalized"
                    if progress:
                        progress(0.85, "Compiling Master Blueprint Document...")
                    self._synthesize_master_plan()
                    save_session(self.state)
                else:
                    self.state.current_round += 1

            if progress:
                progress(1.0, "Iteration completed.")
            return turn_record

        # === DEBATE MODE ITERATION HANDLING (JUDGE & ALLIANCES) ===
        if self.state.current_turn_index % len(self.debaters) == 0:
            round_turns = self.state.get_turns_for_round(self.state.current_round)

            # 1. Evaluate Alliances (Outsmart mechanics)
            self._evaluate_alliances(round_turns)

            # 2. AI Judge Scoring Evaluation
            if progress:
                progress(0.75, f"⚖️ AI Judge is evaluating Round {self.state.current_round} arguments and allocating points...")

            eval_result = self.judge.evaluate_round(
                question=self.state.question,
                round_num=self.state.current_round,
                debaters=self.state.debaters,
                round_turns=round_turns,
                active_alliance=self.state.get_active_alliance(),
            )
            self.state.round_evaluations.append(eval_result)

            # Accumulate scores
            for s in eval_result.scores:
                self.state.cumulative_scores[s.debater_name] = (
                    self.state.cumulative_scores.get(s.debater_name, 0) + s.total_points
                )

            # 3. Check Stopping criteria
            should_terminate, reason = self.moderator.check_termination(self.state)
            if should_terminate or self.state.current_round >= self.state.max_rounds:
                self.state.status = (
                    "consensus_reached" if "Consensus" in reason else "max_rounds_reached"
                )
                if progress:
                    progress(0.9, f"Debate completed: {reason}. Crown winner...")

                # Crown grand winner
                if self.state.cumulative_scores:
                    self.state.grand_winner = max(
                        self.state.cumulative_scores.items(), key=lambda x: x[1]
                    )[0]

                self.state.final_verdict = self.moderator.synthesize_verdict(
                    self.state, reason
                )
                if self.state.final_verdict:
                    self.state.final_verdict.grand_winner = self.state.grand_winner
                save_session(self.state)
            else:
                self.state.current_round += 1

        if progress:
            progress(1.0, "Turn completed.")

        return turn_record

    def step_round(self, progress: Optional[ProgressCallback] = None) -> List[TurnRecord]:
        """
        Executes all turns in the current round.
        """
        records = []
        start_round = self.state.current_round
        while not self.is_finished() and self.state.current_round == start_round:
            rec = self.step_turn(progress)
            if rec:
                records.append(rec)
        return records

    def inject_user_intervention(self, question: str, target_debater: str = "All") -> None:
        """
        Injects a real-time audience cross-examination question or constraint into the active debate state.
        """
        from models.debate_state import UserIntervention
        inv = UserIntervention(
            round_num=self.state.current_round,
            question=question.strip(),
            target_debater=target_debater,
        )
        self.state.user_interventions.append(inv)
        logger.info(f"Injected user intervention for Round {self.state.current_round}: '{question[:60]}...'")

    def run_all(self, progress: Optional[ProgressCallback] = None) -> DebateState:
        """
        Runs the full debate until termination condition or max rounds.
        """
        while not self.is_finished():
            self.step_turn(progress)
        save_session(self.state)
        return self.state
