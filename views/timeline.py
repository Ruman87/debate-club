import html
import streamlit as st
from typing import List, Optional
from models.debate_state import TurnRecord, DebateState
from views.asset_loader import get_character_avatar_uri


def _render_html(html_str: str):
    """Renders raw HTML cleanly using st.html or st.markdown without markdown code formatting."""
    if hasattr(st, "html"):
        st.html(html_str)
    else:
        st.markdown(html_str, unsafe_allow_html=True)


def render_comic_speech_balloon(
    turn: TurnRecord,
    debater_color: str,
    debater_avatar_emoji: str,
    debater_image_path: Optional[str] = None,
    debater_persona: str = "",
    stance_type: str = "for",
    is_devils_advocate: bool = False,
    is_left_aligned: bool = True,
):
    """
    Renders a single debate turn as a graphic-novel style speech balloon
    pointing directly to the character's avatar.
    """
    resp = turn.response
    agreement_color = (
        "#34D399" if resp.agreement_score >= 80 else "#FBBF24" if resp.agreement_score >= 50 else "#F87171"
    )

    avatar_uri = get_character_avatar_uri(turn.debater_name, debater_image_path)
    
    # Alignment classes
    row_class = "row-left" if is_left_aligned else "row-right"
    tail_class = "comic-tail-left" if is_left_aligned else "comic-tail-right"

    stance_tag = (
        '<span style="background: rgba(34,197,94,0.2); color: #4ADE80; font-size: 0.72rem; padding: 1px 6px; border-radius: 4px; font-weight: 700; margin-left: 6px;">[FOR]</span>'
        if stance_type == "for"
        else '<span style="background: rgba(239,68,68,0.2); color: #F87171; font-size: 0.72rem; padding: 1px 6px; border-radius: 4px; font-weight: 700; margin-left: 6px;">[AGAINST]</span>'
        if stance_type == "against"
        else '<span style="background: rgba(245,158,11,0.2); color: #FBBF24; font-size: 0.72rem; padding: 1px 6px; border-radius: 4px; font-weight: 700; margin-left: 6px;">[MIDDLE GROUND]</span>'
    )

    # Avatar image tag
    avatar_html = (
        f'<img src="{avatar_uri}" alt="{turn.debater_name}">'
        if avatar_uri
        else f'<div style="font-size: 2.2rem; line-height: 78px;">{debater_avatar_emoji}</div>'
    )

    # Rebuttal block HTML
    critique_html = ""
    if resp.critique_or_rebuttal and turn.turn_id > 1:
        tech_label = getattr(resp, "rebuttal_technique", "Refutation")
        critique_escaped = html.escape(resp.critique_or_rebuttal)
        critique_html = f'<div class="comic-critique-block"><div class="comic-critique-header">💥 Rebuttal [{html.escape(tech_label)}]:</div><div>{critique_escaped}</div></div>'

    # Core Warrant & Weighing HTML
    warrant_html = ""
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
    if getattr(resp, "alliance_target", None) and resp.alliance_target:
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
        thought_html = f'<div class="comic-thought-bubble"><div style="font-weight: 700; color: #94A3B8; margin-bottom: 2px;">💭 {turn.debater_name}\'s Strategic Intent:</div><div>"{thought_escaped}"</div></div>'

    def _clean_text(raw: str) -> str:
        import re
        if not raw:
            return ""
        cleaned = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL | re.IGNORECASE).strip()
        if "<think>" in cleaned.lower():
            cleaned = re.sub(r"<think>.*", "", cleaned, flags=re.DOTALL | re.IGNORECASE).strip()
        cleaned = re.sub(r"```(?:json)?", "", cleaned).strip()
        if "{" in cleaned or '"' in cleaned:
            for key in ["speech_bubble_summary", "current_best_answer", "inner_reasoning", "critique_or_rebuttal"]:
                match = re.search(rf'"{key}"\s*:\s*"([^"]+)"', cleaned, flags=re.DOTALL)
                if match:
                    cleaned = match.group(1).replace('\\"', '"').replace('\\n', ' ').strip()
                    break
            else:
                cleaned = re.sub(r'[{}\[\]"]', '', cleaned)
        return cleaned.strip()

    answer_escaped = html.escape(_clean_text(resp.current_best_answer))
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
        f'<span class="balloon-turn-pill">Round {turn.round_num} • Turn #{turn.turn_id}</span>'
        f'</div>'
        f'<div class="balloon-agreement-badge" style="color: {agreement_color}; border-color: {agreement_color}44;">'
        f'Agreement: {resp.agreement_score}% {consensus_star}'
        f'</div>'
        f'</div>'
        f'<div class="balloon-speech-text">"{answer_escaped}"</div>'
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
    Renders the chronological graphic-novel speech balloon stream of all debate rounds.
    """
    if not state.turns:
        st.info("💡 No debate rounds yet. Click **Next Turn** or **Run Full Debate** to start!")
        return

    st.markdown("### 💬 Deliberation Stream & Dialogues")
    _render_html('<div class="comic-timeline">')

    # Debater metadata map
    debater_meta = {
        d.id: (
            d.name,
            getattr(d, "color", "#3B82F6"),
            getattr(d, "avatar", "🤖"),
            getattr(d, "image_path", None),
            getattr(d, "persona", ""),
            getattr(d, "stance_type", "for"),
            getattr(d, "is_devils_advocate", False),
        )
        for d in state.debaters
    }

    for idx, turn in enumerate(state.turns):
        name, color, avatar, img_path, persona, stance_type, is_da = debater_meta.get(
            turn.debater_id, ("Debater", "#3B82F6", "🤖", None, "", "for", False)
        )
        
        # Determine left vs right alignment (Alex on left, Charlie on right, Shahar alternating)
        if "alex" in name.lower():
            is_left = True
        elif "charlie" in name.lower():
            is_left = False
        elif "shahar" in name.lower() or "sam" in name.lower():
            is_left = (idx % 2 == 0)
        else:
            is_left = (idx % 2 == 0)

        render_comic_speech_balloon(
            turn=turn,
            debater_color=color,
            debater_avatar_emoji=avatar,
            debater_image_path=img_path,
            debater_persona=persona,
            stance_type=stance_type,
            is_devils_advocate=is_da,
            is_left_aligned=is_left,
        )

    _render_html('</div>')
