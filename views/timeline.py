"""
Chronological Timeline Component for Streamlit in Debate-Club.
Renders graphic-novel styled turn-by-turn dialogue stream for both
Debate Mode (Competitive Arena) and Plan Mode (Collaborative Mastermind).
"""

import streamlit as st
import html
import re
from typing import Optional
from models.debate_state import DebateState, TurnRecord
from views.asset_loader import get_character_avatar_uri


def _render_html(html_str: str):
    st.markdown(html_str, unsafe_allow_html=True)


def _get_agreement_color(score: int) -> str:
    if score >= 75:
        return "#10B981"  # Emerald Green
    elif score >= 50:
        return "#3B82F6"  # Blue
    elif score >= 25:
        return "#F59E0B"  # Amber
    else:
        return "#EF4444"  # Red


def render_comic_turn(
    turn: TurnRecord,
    debater_color: str,
    debater_avatar_emoji: str,
    avatar_uri: Optional[str] = None,
    is_left_aligned: bool = True,
    is_plan_mode: bool = False,
):
    """
    Renders a single graphic-novel turn card with speech bubbles and metadata.
    """
    resp = turn.response
    agreement_color = _get_agreement_color(resp.agreement_score)

    row_class = "left-aligned" if is_left_aligned else "right-aligned"
    tail_class = "comic-tail-left" if is_left_aligned else "comic-tail-right"

    if is_plan_mode:
        stance_tag = (
            '<span style="background: rgba(59,130,246,0.2); color: #60A5FA; font-size: 0.72rem; padding: 1px 6px; border-radius: 4px; font-weight: 700; margin-left: 6px;">[ARCHITECT]</span>'
            if "alex" in turn.debater_name.lower() or "debater_1" in turn.debater_id
            else '<span style="background: rgba(168,85,247,0.2); color: #C084FC; font-size: 0.72rem; padding: 1px 6px; border-radius: 4px; font-weight: 700; margin-left: 6px;">[STRESS-TESTER]</span>'
            if "charlie" in turn.debater_name.lower() or "debater_2" in turn.debater_id
            else '<span style="background: rgba(239,68,68,0.2); color: #F87171; font-size: 0.72rem; padding: 1px 6px; border-radius: 4px; font-weight: 700; margin-left: 6px;">[SYNTHESIZER]</span>'
        )
    else:
        stance_tag = (
            '<span style="background: rgba(34,197,94,0.2); color: #4ADE80; font-size: 0.72rem; padding: 1px 6px; border-radius: 4px; font-weight: 700; margin-left: 6px;">[FOR]</span>'
            if "alex" in turn.debater_name.lower() or "debater_1" in turn.debater_id
            else '<span style="background: rgba(239,68,68,0.2); color: #F87171; font-size: 0.72rem; padding: 1px 6px; border-radius: 4px; font-weight: 700; margin-left: 6px;">[AGAINST]</span>'
            if "charlie" in turn.debater_name.lower() or "debater_2" in turn.debater_id
            else '<span style="background: rgba(245,158,11,0.2); color: #FBBF24; font-size: 0.72rem; padding: 1px 6px; border-radius: 4px; font-weight: 700; margin-left: 6px;">[MIDDLE GROUND]</span>'
        )

    # Avatar image tag
    avatar_html = (
        f'<img src="{avatar_uri}" alt="{turn.debater_name}">'
        if avatar_uri
        else f'<div style="font-size: 2.2rem; line-height: 78px;">{debater_avatar_emoji}</div>'
    )

    # Plan Mode specific blocks
    plan_blocks_html = ""
    if is_plan_mode:
        vulns = getattr(resp, "vulnerabilities_identified", [])
        enhs = getattr(resp, "proposed_enhancements", [])
        
        if vulns:
            chips_v = "".join([f'<div style="margin-top: 2px;">⚠️ {html.escape(v)}</div>' for v in vulns])
            plan_blocks_html += f'<div style="background: rgba(239,68,68,0.1); border-left: 3px solid #EF4444; border-radius: 0 8px 8px 0; padding: 6px 10px; margin-bottom: 8px; font-size: 0.83rem; color: #FCA5A5;"><div style="font-weight: 700; color: #F87171; margin-bottom: 2px;">🔍 Vulnerabilities & Risks Probed:</div>{chips_v}</div>'
            
        if enhs:
            chips_e = "".join([f'<div style="margin-top: 2px;">🚀 {html.escape(e)}</div>' for e in enhs])
            plan_blocks_html += f'<div style="background: rgba(16,185,129,0.1); border-left: 3px solid #10B981; border-radius: 0 8px 8px 0; padding: 6px 10px; margin-bottom: 8px; font-size: 0.83rem; color: #6EE7B7;"><div style="font-weight: 700; color: #34D399; margin-bottom: 2px;">🛠️ High-Value Enhancements Added:</div>{chips_e}</div>'

    # Debate Mode Rebuttal block HTML
    critique_html = ""
    if not is_plan_mode and resp.critique_or_rebuttal and turn.turn_id > 1:
        tech_label = getattr(resp, "rebuttal_technique", "Refutation")
        critique_escaped = html.escape(resp.critique_or_rebuttal)
        critique_html = f'<div class="comic-critique-block"><div class="comic-critique-header">💥 Rebuttal [{html.escape(tech_label)}]:</div><div>{critique_escaped}</div></div>'

    # Core Warrant & Weighing HTML
    warrant_html = ""
    if not is_plan_mode:
        warrant_val = getattr(resp, "core_warrant", None)
        weighing_val = getattr(resp, "weighing_metric", None)
        if warrant_val or weighing_val:
            w_items = []
            if warrant_val:
                w_items.append(f"<strong>🧠 Causal Warrant:</strong> {html.escape(warrant_val)}")
            if weighing_val:
                w_items.append(f"<strong>📊 Impact Weighing:</strong> {html.escape(weighing_val)}")
            w_inner = " • ".join(w_items)
            warrant_html = f'<div style="background: rgba(59,130,246,0.1); border-left: 3px solid #3B82F6; border-radius: 0 8px 8px 0; padding: 6px 10px; margin-bottom: 8px; font-size: 0.83rem; color: #93C5FD;">{w_inner}</div>'

    # Agreed points HTML
    agreed_html = ""
    if resp.points_of_agreement:
        chips = "".join([f'<span class="comic-agreed-chip">✓ {html.escape(pt)}</span>' for pt in resp.points_of_agreement])
        agreed_html = f'<div class="comic-agreed-block"><div class="comic-agreed-header">🤝 Strategic Concession (Even-If):</div><div>{chips}</div></div>'

    # Alliance Pitch HTML
    alliance_html = ""
    if not is_plan_mode and getattr(resp, "alliance_target", None) and resp.alliance_target:
        pitch_escaped = html.escape(getattr(resp, "alliance_pitch", "") or "Proposed tactical coordination.")
        alliance_html = (
            f'<div style="background: rgba(168,85,247,0.12); border-left: 3px solid #A855F7; border-radius: 0 8px 8px 0; padding: 6px 10px; margin-bottom: 8px; font-size: 0.84rem; color: #D8B4FE;">'
            f'<strong>🤝 Alliance Pitch to {html.escape(resp.alliance_target)}:</strong> "{pitch_escaped}"'
            f'</div>'
        )

    # Thought Bubble HTML
    thought_html = ""
    if resp.inner_reasoning:
        thought_escaped = html.escape(resp.inner_reasoning)
        thought_html = f'<div class="comic-thought-bubble"><div style="font-weight: 700; color: #94A3B8; margin-bottom: 2px;">💭 {turn.debater_name}\'s Design Thinking:</div><div>"{thought_escaped}"</div></div>'

    def _clean_text(raw: str) -> str:
        if not raw:
            return ""
        cleaned = raw
        cleaned = re.sub(r"<think>.*?</think>", "", cleaned, flags=re.DOTALL | re.IGNORECASE).strip()
        cleaned = re.sub(r"```(?:json)?", "", cleaned).strip()

        if "{" in cleaned and "}" in cleaned:
            for key in ["current_best_answer", "speech_bubble_summary", "inner_reasoning", "critique_or_rebuttal", "blueprint_section"]:
                match = re.search(rf'"{key}"\s*:\s*"([^"]+)"', cleaned, flags=re.DOTALL)
                if match:
                    cleaned = match.group(1).replace('\\"', '"').replace('\\n', ' ').strip()
                    break
            else:
                cleaned = re.sub(r'[{}\[\]"]', '', cleaned)
        return cleaned.strip()

    answer_escaped = html.escape(_clean_text(resp.current_best_answer))
    badge_label = f"Readiness: {resp.agreement_score}%" if is_plan_mode else f"Agreement: {resp.agreement_score}%"
    consensus_star = "✨" if resp.is_consensus_reached else ""

    balloon_markup = (
        f'<div class="comic-turn-row {row_class}">'
        f'<div class="comic-avatar-col">'
        f'<div class="comic-avatar-frame" style="border: 3px solid {debater_color}; box-shadow: 0 0 16px {debater_color}55;">{avatar_html}</div>'
        f'<div class="comic-avatar-nameplate" style="color: {debater_color};">{turn.debater_name}</div>'
        f'<div class="comic-avatar-model" title="{turn.model_name}">{turn.model_name}</div>'
        f'</div>'
        f'<div class="comic-balloon" style="border: 2px solid {debater_color}; --balloon-border-color: {debater_color};">'
        f'<div class="{tail_class}"></div>'
        f'<div class="balloon-header">'
        f'<div class="balloon-speaker-title">'
        f'<span style="color: {debater_color}; font-weight: 800;">{turn.debater_name}</span>'
        f'{stance_tag}'
        f'<span class="balloon-turn-pill">{"Iteration" if is_plan_mode else "Round"} {turn.round_num} • Step #{turn.turn_id}</span>'
        f'</div>'
        f'<div class="balloon-agreement-badge" style="color: {agreement_color}; border-color: {agreement_color}44;">'
        f'{badge_label} {consensus_star}'
        f'</div>'
        f'</div>'
        f'<div class="balloon-speech-text">"{answer_escaped}"</div>'
        f'{plan_blocks_html}'
        f'{warrant_html}'
        f'{alliance_html}'
        f'{critique_html}'
        f'{agreed_html}'
        f'{thought_html}'
        f'</div>'
        f'</div>'
    )

    _render_html(balloon_markup)


def render_debate_timeline(state: DebateState):
    """
    Renders the chronological graphic-novel speech balloon stream of all debate or planning turns.
    """
    if not state.turns:
        st.info("💡 No dialogue yet. Click **Next Step** or **Run Full Session** to start!")
        return

    is_plan_mode = state.app_mode == "plan"
    title = "💬 Mastermind Co-Design Trajectory" if is_plan_mode else "💬 Deliberation Stream & Dialogues"
    st.markdown(f"### {title}")
    _render_html('<div class="comic-timeline">')

    debater_map = {d.id: d for d in state.debaters}

    for turn in state.turns:
        debater = debater_map.get(turn.debater_id)
        debater_color = getattr(debater, "color", "#3B82F6") if debater else "#3B82F6"
        debater_emoji = getattr(debater, "avatar", "🔷") if debater else "🔷"
        avatar_uri = get_character_avatar_uri(turn.debater_name)

        is_left = "debater_1" in turn.debater_id or "alex" in turn.debater_name.lower()

        render_comic_turn(
            turn=turn,
            debater_color=debater_color,
            debater_avatar_emoji=debater_emoji,
            avatar_uri=avatar_uri,
            is_left_aligned=is_left,
            is_plan_mode=is_plan_mode,
        )

    _render_html('</div>')
