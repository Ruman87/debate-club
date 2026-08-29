"""
Judge Scoreboard & Alliance Component for Debate-Club.
Renders Supreme Judge Dredd's rulings, round score breakdowns, active coalitions,
and the live debate leaderboard.
"""

import streamlit as st
from typing import Optional
from models.debate_state import DebateState, JudgeRoundEvaluation, ActiveAlliance
from views.asset_loader import get_character_avatar_uri


def render_judge_scoreboard(state: DebateState):
    """
    Renders Supreme Judge Dredd's rulings, cumulative leaderboard, and alliance alerts.
    """
    if not state.round_evaluations and not state.active_alliances:
        return

    st.markdown("---")
    st.markdown("### ⚖️ Supreme Judge Dredd's Chamber & Leaderboard")

    # 1. Active Alliance Alert (Outsmart dynamic)
    active_alliance = state.get_active_alliance()
    if active_alliance and active_alliance.is_active:
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, rgba(239,68,68,0.2) 0%, rgba(168,85,247,0.2) 100%); border: 2px solid #EF4444; border-radius: 12px; padding: 12px 18px; margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <span style="font-size: 1.2rem;">🤝</span>
                    <strong style="color: #FCA5A5; font-size: 1rem; margin-left: 6px;">STRATEGIC COALITION IN EFFECT (Round {active_alliance.round_num}):</strong>
                    <div style="color: #F8FAFC; font-size: 0.92rem; margin-top: 2px;">
                        <strong>{active_alliance.debater_a}</strong> and <strong>{active_alliance.debater_b}</strong> have allied on shared premises against <strong>{active_alliance.target_debater}</strong>!
                    </div>
                </div>
                <div style="background: rgba(239,68,68,0.3); color: #FECACA; padding: 4px 10px; border-radius: 8px; font-weight: 700; font-size: 0.8rem;">
                    Non-Polar Coalition
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 2. Cumulative Standings Leaderboard
    cols = st.columns(len(state.debaters))
    sorted_scores = sorted(state.cumulative_scores.items(), key=lambda x: x[1], reverse=True)
    leader_name = sorted_scores[0][0] if sorted_scores else None

    for col, debater in zip(cols, state.debaters):
        char_name = debater.name
        total_pts = state.cumulative_scores.get(char_name, 0)
        is_leader = (char_name == leader_name and total_pts > 0)
        char_color = getattr(debater, "color", "#3B82F6")

        badge = "👑 LEADER" if is_leader else "DEBATER"
        border_glow = f"0 0 16px {char_color}55" if is_leader else "none"

        with col:
            st.markdown(
                f"""
                <div style="background: rgba(30, 41, 59, 0.8); border: 2px solid {char_color}; border-radius: 12px; padding: 12px; text-align: center; box-shadow: {border_glow};">
                    <div style="font-size: 0.75rem; font-weight: 800; color: {'#34D399' if is_leader else '#94A3B8'}; letter-spacing: 0.05em;">
                        {badge}
                    </div>
                    <div style="font-size: 1.25rem; font-weight: 800; color: {char_color}; margin: 2px 0;">
                        {char_name}
                    </div>
                    <div style="font-size: 1.75rem; font-weight: 800; font-family: 'JetBrains Mono', monospace; color: #F8FAFC;">
                        {total_pts} <span style="font-size: 0.85rem; color: #94A3B8; font-weight: 500;">pts</span>
                    </div>
                    <div style="font-size: 0.74rem; color: #94A3B8; margin-top: 4px;">
                        Position: <strong>{debater.stance_type.upper()}</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # 3. Round-by-Round Judge Dredd Evaluations
    dredd_avatar = get_character_avatar_uri("judge_dredd") or ""
    st.markdown("#### 📜 Supreme Judge Dredd's Decrees")
    
    for r_eval in reversed(state.round_evaluations):
        with st.expander(f"⚖️ Round {r_eval.round_num} Decree • Winner: {r_eval.round_winner} 🏆", expanded=(r_eval.round_num == len(state.round_evaluations))):
            avatar_tag = f'<img src="{dredd_avatar}" style="width: 52px; height: 52px; border-radius: 50%; border: 2px solid #F59E0B;" alt="Judge Dredd">' if dredd_avatar else '<div style="font-size: 2rem;">⚖️</div>'
            
            clash_banner = ""
            if getattr(r_eval, "key_clash_issue", None):
                clash_banner = f'<div style="margin-bottom: 8px; font-size: 0.82rem; color: #94A3B8;">🏛️ <strong>Decisive Clash Point:</strong> <em>{html.escape(r_eval.key_clash_issue)}</em></div>'

            st.markdown(
                f"""
                <div style="display: flex; gap: 14px; align-items: center; background: rgba(245, 158, 11, 0.08); border: 2px solid #F59E0B; border-radius: 10px; padding: 12px; margin-bottom: 12px;">
                    {avatar_tag}
                    <div>
                        <div style="font-weight: 800; color: #F59E0B; font-size: 0.9rem;">⚖️ SUPREME JUDGE DREDD:</div>
                        <div style="font-style: italic; color: #F8FAFC; font-size: 0.95rem; margin-top: 2px;">
                            "{r_eval.dredd_quote or r_eval.judge_commentary}"
                        </div>
                    </div>
                </div>
                {clash_banner}
                """,
                unsafe_allow_html=True,
            )
            
            # Scores Table (WUDC Standard)
            score_cols = st.columns(len(r_eval.scores))
            for sc_col, sc in zip(score_cols, r_eval.scores):
                clash_tag = f'<div style="font-size: 0.75rem; color: #34D399; margin-top: 3px;">🎯 <strong>Clash Won:</strong> {html.escape(sc.clash_won)}</div>' if getattr(sc, "clash_won", None) else ""
                
                with sc_col:
                    st.markdown(
                        f"""
                        <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 10px; font-size: 0.85rem;">
                            <strong style="font-size: 1rem; color: #60A5FA;">{sc.debater_name}</strong>
                            <div style="margin: 6px 0;">
                                <div>🧠 Mechanistic Warrants: <strong>{sc.logic_score}/10</strong></div>
                                <div>💥 Clash & Rebuttals: <strong>{sc.rebuttal_score}/10</strong></div>
                                <div>⚖️ Comparative Weighing: <strong>{sc.rhetoric_score}/10</strong></div>
                            </div>
                            <div style="border-top: 1px solid rgba(255,255,255,0.1); padding-top: 4px; font-weight: 700; color: #34D399;">
                                Total: {sc.total_points} pts
                            </div>
                            {clash_tag}
                            <div style="font-style: italic; color: #94A3B8; font-size: 0.78rem; margin-top: 4px;">
                                "{sc.feedback}"
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            if r_eval.strongest_argument:
                st.markdown(f"🌟 **Decisive Argument:** {r_eval.strongest_argument}")
            if r_eval.weakest_point:
                st.markdown(f"⚠️ **Vulnerability / Missing Warrant:** {r_eval.weakest_point}")
