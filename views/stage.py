"""
Graphic Novel Arena Stage Component for Streamlit in Debate-Club.
Renders the stage image with animated speech balloons over podiums for both
Debate Mode (Competitive Arena with Judge Dredd) and Plan Mode (Collaborative Mastermind).
"""

import streamlit as st
import html
import re
from typing import Optional
from models.debate_state import DebateState, TurnRecord
from views.asset_loader import get_image_base64_data_uri


def _render_html(html_str: str):
    st.markdown(html_str, unsafe_allow_html=True)


def _clean_speech_text(text: str) -> str:
    if not text:
        return ""
    cleaned = text
    cleaned = re.sub(r"<think>.*?</think>", "", cleaned, flags=re.DOTALL | re.IGNORECASE).strip()
    cleaned = re.sub(r"```(?:json)?", "", cleaned).strip()

    if "{" in cleaned and "}" in cleaned:
        for key in ["speech_bubble_summary", "current_best_answer", "inner_reasoning", "critique_or_rebuttal", "blueprint_section"]:
            match = re.search(rf'"{key}"\s*:\s*"([^"]+)"', cleaned, flags=re.DOTALL)
            if match:
                cleaned = match.group(1).replace('\\"', '"').replace('\\n', ' ').strip()
                break
        else:
            cleaned = re.sub(r'[{}\[\]"]', '', cleaned)
    return cleaned.strip()


def _get_bubble_summary(turn: TurnRecord) -> str:
    resp = turn.response
    raw = resp.speech_bubble_summary or resp.current_best_answer or ""
    clean = _clean_speech_text(raw)
    if len(clean) > 340:
        clean = clean[:337] + "..."
    return clean


def render_arena_stage(
    state: DebateState,
    active_debater_idx: Optional[int] = None,
    upcoming_debater_idx: Optional[int] = None,
    is_thinking: bool = False,
    show_judge_verdict: bool = False,
):
    """
    Renders the main debate arena photo with the completed speech balloon of the previous speaker,
    Judge Dredd's round evaluation, or the Final Master Blueprint completion banner.
    """
    if not state.debaters:
        return

    is_plan_mode = state.app_mode == "plan"
    target_upcoming = upcoming_debater_idx if upcoming_debater_idx is not None else active_debater_idx

    stage_uri = get_image_base64_data_uri("assets/arena_stage.jpg")
    if not stage_uri:
        return

    latest_turn = state.turns[-1] if state.turns else None
    latest_eval = state.round_evaluations[-1] if state.round_evaluations else None
    is_finished = state.is_finished()

    # === 1. FINISHED STATE ===
    if is_finished:
        speaker_slot = "dredd"
        if is_plan_mode:
            header_title = "📋 AI MASTERMIND • MASTER BLUEPRINT FINALIZED"
            badge_text = "🚀 MASTER BLUEPRINT 100% READY"
            quote_text = (
                "The collaborative mastermind has successfully bulletproofed the blueprint! "
                "Architectural foundations established, critical failure modes mitigated, and the phased execution roadmap is ready."
            )
            balloon_inner = (
                f'<div class="stage-balloon-header">'
                f'<div class="stage-speaker-tag" style="color: #10B981;">'
                f'✨ AI MASTERMIND BLUEPRINT <span class="stage-model-pill">Co-Designed</span>'
                f'</div>'
                f'<div class="stage-round-badge" style="background: rgba(16,185,129,0.25); color: #059669; font-weight: 800;">'
                f'{header_title}'
                f'</div>'
                f'</div>'
                f'<div class="stage-balloon-body" style="font-weight: 600; color: #1E293B;">"{quote_text}"</div>'
                f'<div class="stage-balloon-chips">'
                f'<span style="background: rgba(16,185,129,0.25); color: #065F46; font-size: 0.82rem; font-weight: 800; padding: 3px 10px; border-radius: 6px; border: 1px solid #10B981;">{badge_text}</span>'
                f'</div>'
            )
        else:
            # Debate Mode Final Crown
            grand_winner = state.grand_winner
            if not grand_winner and state.cumulative_scores:
                grand_winner = max(state.cumulative_scores.items(), key=lambda x: x[1])[0]
            grand_winner = grand_winner or "Alex"
            top_pts = state.cumulative_scores.get(grand_winner, 0)
            
            header_title = "⚖️ SUPREME JUDGE DREDD • FINAL JUDGMENT"
            badge_text = f"👑 GRAND CHAMPION: {grand_winner.upper()} ({top_pts} PTS)"

            if state.final_verdict and state.final_verdict.summary_verdict:
                sv = state.final_verdict.summary_verdict.strip()
                if not sv.startswith("I AM THE LAW") and not sv.startswith("FINAL JUDGMENT"):
                    quote_text = f"FINAL VERDICT OF THE LAW! {grand_winner} is decreed the Grand Champion! {sv}"
                else:
                    quote_text = sv
            elif latest_eval and latest_eval.dredd_quote:
                quote_text = f"FINAL JUDGMENT OF THE LAW! By decree of the court, {grand_winner} wins the debate with {top_pts} points! {latest_eval.dredd_quote}"
            else:
                quote_text = f"I AM THE LAW! The deliberation is adjourned. By decree of Supreme Judge Dredd, {grand_winner} is declared the undisputed Grand Champion with {top_pts} total points!"

            balloon_inner = (
                f'<div class="stage-balloon-header">'
                f'<div class="stage-speaker-tag" style="color: #F59E0B;">'
                f'⚖️ SUPREME JUDGE DREDD <span class="stage-model-pill">{state.judge_model}</span>'
                f'</div>'
                f'<div class="stage-round-badge" style="background: rgba(245,158,11,0.25); color: #D97706; font-weight: 800;">'
                f'{header_title}'
                f'</div>'
                f'</div>'
                f'<div class="stage-balloon-body" style="font-weight: 600; color: #1E293B;">"{html.escape(quote_text)}"</div>'
                f'<div class="stage-balloon-chips">'
                f'<span style="background: rgba(245,158,11,0.25); color: #B45309; font-size: 0.82rem; font-weight: 800; padding: 3px 10px; border-radius: 6px; border: 1px solid #F59E0B;">{badge_text}</span>'
                f'</div>'
            )

    # === 2. SUPREME JUDGE DREDD: INTERMEDIATE ROUND RULING (Debate Mode Only) ===
    elif show_judge_verdict and latest_eval and not is_plan_mode:
        speaker_slot = "dredd"
        winner = latest_eval.round_winner
        quote = html.escape(latest_eval.dredd_quote or latest_eval.judge_commentary)
        header_title = f"⚖️ SUPREME JUDGE DREDD • ROUND {latest_eval.round_num} RULING"
        badge_text = f"🏆 Round {latest_eval.round_num} Winner: {winner}"

        balloon_inner = (
            f'<div class="stage-balloon-header">'
            f'<div class="stage-speaker-tag" style="color: #F59E0B;">'
            f'⚖️ SUPREME JUDGE DREDD <span class="stage-model-pill">{state.judge_model}</span>'
            f'</div>'
            f'<div class="stage-round-badge" style="background: rgba(245,158,11,0.2); color: #D97706; font-weight: 800;">'
            f'{header_title}'
            f'</div>'
            f'</div>'
            f'<div class="stage-balloon-body" style="font-weight: 600; color: #1E293B;">"{quote}"</div>'
            f'<div class="stage-balloon-chips">'
            f'<span style="background: rgba(245,158,11,0.2); color: #B45309; font-size: 0.78rem; font-weight: 800; padding: 2px 8px; border-radius: 6px;">{badge_text}</span>'
            f'</div>'
        )

    # === 3. DEBATER / MASTERMIND TURN BALLOON ===
    elif latest_turn:
        speaker_name = latest_turn.debater_name.lower()
        speaker_id = latest_turn.debater_id.lower()
        if "alex" in speaker_name or "debater_1" in speaker_id:
            speaker_slot = "alex"
        elif "charlie" in speaker_name or "debater_2" in speaker_id:
            speaker_slot = "charlie"
        else:
            speaker_slot = "shahar"

        debater_obj = next((d for d in state.debaters if d.id == latest_turn.debater_id), None)
        debater_color = getattr(debater_obj, "color", "#3B82F6") if debater_obj else "#3B82F6"
        summary_text = html.escape(_get_bubble_summary(latest_turn))
        speaker_display = latest_turn.debater_name
        model_display = latest_turn.model_name
        round_info = f"{'Iteration' if is_plan_mode else 'Round'} {latest_turn.round_num}"

        if is_plan_mode:
            role_title = getattr(debater_obj, "persona", "Architect")
            vulns = getattr(latest_turn.response, "vulnerabilities_identified", [])
            enhs = getattr(latest_turn.response, "proposed_enhancements", [])

            chips_list = []
            if vulns:
                chips_list.append(f'<span style="background: rgba(239,68,68,0.2); color: #F87171; font-size: 0.72rem; font-weight: 700; padding: 1px 6px; border-radius: 4px;">🔍 {len(vulns)} Risks Probed</span>')
            if enhs:
                chips_list.append(f'<span style="background: rgba(16,185,129,0.2); color: #34D399; font-size: 0.72rem; font-weight: 700; padding: 1px 6px; border-radius: 4px;">🚀 {len(enhs)} Solutions Added</span>')
            
            chips_html = f'<div class="stage-balloon-chips">{"".join(chips_list)}</div>' if chips_list else ""

            balloon_inner = (
                f'<div class="stage-balloon-header">'
                f'<div class="stage-speaker-tag" style="color: {debater_color};">'
                f'🛠️ {speaker_display} <span class="stage-model-pill">{model_display}</span>'
                f'</div>'
                f'<div class="stage-round-badge" style="background: {debater_color}22; color: {debater_color};">[{role_title}] • {round_info}</div>'
                f'</div>'
                f'<div class="stage-balloon-body">"{summary_text}"</div>'
                f'{chips_html}'
            )
        else:
            # Debate Mode Badges
            stance_label = getattr(debater_obj, "stance_type", "for").upper() if debater_obj else "FOR"
            tech = getattr(latest_turn.response, "rebuttal_technique", None)
            tech_badge = ""
            if tech and latest_turn.turn_id > 1:
                if "Link Turn" in tech:
                    tech_badge = '<span style="background: rgba(16,185,129,0.2); color: #34D399; font-size: 0.72rem; font-weight: 700; padding: 1px 6px; border-radius: 4px;">🔄 Link Turn</span>'
                elif "Even-If" in tech:
                    tech_badge = '<span style="background: rgba(245,158,11,0.2); color: #FBBF24; font-size: 0.72rem; font-weight: 700; padding: 1px 6px; border-radius: 4px;">⚖️ Even-If Analysis</span>'
                elif "Mechanism" in tech:
                    tech_badge = '<span style="background: rgba(239,68,68,0.2); color: #F87171; font-size: 0.72rem; font-weight: 700; padding: 1px 6px; border-radius: 4px;">💥 Mechanism Breakdown</span>'
                elif "Mitigation" in tech:
                    tech_badge = '<span style="background: rgba(59,130,246,0.2); color: #60A5FA; font-size: 0.72rem; font-weight: 700; padding: 1px 6px; border-radius: 4px;">🛡️ Impact Mitigation</span>'
                else:
                    tech_badge = '<span class="stage-chip-critique">💥 Rebuttal Delivered</span>'

            weighing = getattr(latest_turn.response, "weighing_metric", None)
            weighing_badge = ""
            if weighing:
                weighing_badge = f'<span style="background: rgba(99,102,241,0.2); color: #A5B4FC; font-size: 0.72rem; font-weight: 700; padding: 1px 6px; border-radius: 4px;">📊 Weighs {html.escape(weighing)}</span>'

            consensus_badge = ""
            if latest_turn.response.is_consensus_reached:
                consensus_badge = '<span class="stage-chip-consensus">✨ Consensus Proposed</span>'
                
            alliance_badge = ""
            if getattr(latest_turn.response, "alliance_target", None):
                t = latest_turn.response.alliance_target
                alliance_badge = f'<span style="background: rgba(168,85,247,0.2); color: #C084FC; font-size: 0.72rem; font-weight: 700; padding: 1px 6px; border-radius: 4px;">🤝 Targets {t} for Coalition</span>'

            chips_html = f'<div class="stage-balloon-chips">{tech_badge}{weighing_badge}{consensus_badge}{alliance_badge}</div>' if (tech_badge or weighing_badge or consensus_badge or alliance_badge) else ""

            balloon_inner = (
                f'<div class="stage-balloon-header">'
                f'<div class="stage-speaker-tag" style="color: {debater_color};">'
                f'🎙️ {speaker_display} <span class="stage-model-pill">{model_display}</span>'
                f'</div>'
                f'<div class="stage-round-badge" style="background: {debater_color}22; color: {debater_color};">[{stance_label}] • {round_info}</div>'
                f'</div>'
                f'<div class="stage-balloon-body">"{summary_text}"</div>'
                f'{chips_html}'
            )

    # === 4. OPENING TURN STATE ===
    else:
        speaker_slot = "alex"
        debater_obj = state.debaters[0]
        debater_color = getattr(debater_obj, "color", "#3B82F6")
        role_label = getattr(debater_obj, "persona", "Lead Architect" if is_plan_mode else "Affirmative")
        
        balloon_inner = (
            f'<div class="stage-balloon-header">'
            f'<div class="stage-speaker-tag" style="color: {debater_color};">'
            f'{"🛠️" if is_plan_mode else "🎙️"} Alex <span class="stage-model-pill">{debater_obj.model_name}</span>'
            f'</div>'
            f'<div class="stage-round-badge" style="background: {debater_color}22; color: {debater_color};">[{role_label}] • Iteration 1</div>'
            f'</div>'
            f'<div class="stage-balloon-body">"Alex is preparing to deliver the foundational blueprint architecture..."</div>'
        )

    # Live Ticker Indicator when an upcoming debater is thinking
    ticker_html = ""
    if not is_finished and is_thinking and target_upcoming is not None and target_upcoming < len(state.debaters):
        upcoming = state.debaters[target_upcoming]
        up_color = getattr(upcoming, "color", "#3B82F6")
        up_role = getattr(upcoming, "persona", "Architect" if is_plan_mode else "Debater")
        ticker_html = (
            f'<div class="stage-live-ticker" style="border-left-color: {up_color};">'
            f'<span class="live-dot" style="background-color: {up_color};"></span>'
            f'<span><strong>LIVE MASTERMIND:</strong> <span style="color: {up_color}; font-weight: 700;">{upcoming.name}</span> ({upcoming.model_name}) is co-designing as [{up_role}]...</span>'
            f'</div>'
        ) if is_plan_mode else (
            f'<div class="stage-live-ticker" style="border-left-color: {up_color};">'
            f'<span class="live-dot" style="background-color: {up_color};"></span>'
            f'<span><strong>LIVE:</strong> <span style="color: {up_color}; font-weight: 700;">{upcoming.name}</span> ({upcoming.model_name}) is formulating counter-argument defending [{getattr(upcoming, "stance_type", "for").upper()}]...</span>'
            f'</div>'
        )

    # Balloon container classes
    balloon_class = f"balloon-{speaker_slot}"
    tail_outer_class = f"stage-tail-{speaker_slot}"
    tail_inner_class = f"stage-tail-{speaker_slot}-inner"

    stage_html = (
        f'<div class="stage-photo-wrapper">'
        f'<img src="{stage_uri}" class="stage-photo-img" alt="Debate Arena Stage">'
        f'<div class="stage-overlay-balloon {balloon_class}">'
        f'{balloon_inner}'
        f'<div class="{tail_outer_class}"></div>'
        f'<div class="{tail_inner_class}"></div>'
        f'</div>'
        f'{ticker_html}'
        f'</div>'
    )

    _render_html(stage_html)

    # Roster Status Bar below photo
    roster_cols = st.columns(len(state.debaters))
    grand_winner_name = state.grand_winner or (max(state.cumulative_scores.items(), key=lambda x: x[1])[0] if is_finished and state.cumulative_scores else None)

    for idx, (col, debater) in enumerate(zip(roster_cols, state.debaters)):
        char_color = getattr(debater, "color", "#3B82F6")
        stance_str = getattr(debater, "stance_type", "for").upper()
        pts = state.cumulative_scores.get(debater.name, 0)
        
        if is_plan_mode:
            role_pill = (
                '<span style="background: rgba(59,130,246,0.2); color: #60A5FA; font-size: 0.72rem; padding: 2px 6px; border-radius: 4px; font-weight: 700;">🏗️ LEAD ARCHITECT</span>'
                if "architect" in debater.stance_type
                else '<span style="background: rgba(168,85,247,0.2); color: #C084FC; font-size: 0.72rem; padding: 2px 6px; border-radius: 4px; font-weight: 700;">🔍 STRESS-TESTER</span>'
                if "stress" in debater.stance_type
                else '<span style="background: rgba(239,68,68,0.2); color: #F87171; font-size: 0.72rem; padding: 2px 6px; border-radius: 4px; font-weight: 700;">⚡ SYNTHESIZER</span>'
            )
        else:
            role_pill = (
                '<span style="background: rgba(34,197,94,0.2); color: #4ADE80; font-size: 0.72rem; padding: 2px 6px; border-radius: 4px; font-weight: 700;">🟢 FOR</span>'
                if stance_str == "FOR"
                else '<span style="background: rgba(239,68,68,0.2); color: #F87171; font-size: 0.72rem; padding: 2px 6px; border-radius: 4px; font-weight: 700;">🔴 AGAINST</span>'
                if stance_str == "AGAINST"
                else '<span style="background: rgba(245,158,11,0.2); color: #FBBF24; font-size: 0.72rem; padding: 2px 6px; border-radius: 4px; font-weight: 700;">⚖️ MIDDLE GROUND</span>'
            )

        if is_finished:
            if is_plan_mode:
                status_label = "✅ Blueprint Contributor"
                status_color = "#34D399"
                border_style = f"2px solid #34D399"
                glow = "0 0 12px rgba(52, 211, 153, 0.4)"
            elif debater.name == grand_winner_name:
                status_label = f"👑 GRAND CHAMPION"
                status_color = "#F59E0B"
                border_style = f"2px solid #F59E0B"
                glow = "0 0 16px rgba(245, 158, 11, 0.7)"
            else:
                status_label = f"🏁 Finalist"
                status_color = "#94A3B8"
                border_style = "1px solid rgba(255,255,255,0.15)"
                glow = "none"
        elif is_thinking and target_upcoming == idx:
            status_label = "⚡ Co-Designing..." if is_plan_mode else "⚡ Formulating Rebuttal..."
            status_color = char_color
            border_style = f"2px solid {char_color}"
            glow = f"0 0 14px {char_color}66"
        elif latest_turn and latest_turn.debater_id == debater.id and not show_judge_verdict:
            status_label = "🛠️ Blueprint on Stage" if is_plan_mode else "💬 Point on Stage"
            status_color = "#34D399"
            border_style = f"2px solid {char_color}"
            glow = "none"
        else:
            status_label = "⏳ Standing By"
            status_color = "#94A3B8"
            border_style = "1px solid rgba(255,255,255,0.1)"
            glow = "none"

        with col:
            score_line = f'<div class="roster-meta" style="color: #F59E0B; font-weight: 700; font-size: 0.82rem; margin-top: 4px;">🏆 Score: {pts} pts</div>' if not is_plan_mode else f'<div class="roster-meta" style="color: #34D399; font-weight: 700; font-size: 0.82rem; margin-top: 4px;">🎯 Readiness: {state.plan_readiness_score}%</div>'
            st.markdown(
                f"""
                <div class="roster-card" style="border: {border_style}; box-shadow: {glow};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <span class="roster-name" style="color: {char_color};">{debater.name}</span>
                        {role_pill}
                    </div>
                    <div class="roster-model">{debater.model_name}</div>
                    <div style="font-size: 0.75rem; color: {status_color}; font-weight: 600; margin-top: 4px;">
                        {status_label}
                    </div>
                    {score_line}
                </div>
                """,
                unsafe_allow_html=True,
            )
