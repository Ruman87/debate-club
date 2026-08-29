import streamlit as st
import pandas as pd
from models.debate_state import DebateState


def render_consensus_meter(state: DebateState):
    """
    Renders top status indicators: Round counter, Agreement Score gauge, and debate status badge.
    """
    latest_turn = state.get_latest_turn()
    current_agreement = latest_turn.response.agreement_score if latest_turn else 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Round",
            value=f"{state.current_round} / {state.max_rounds}",
        )

    with col2:
        st.metric(
            label="Turns Elapsed",
            value=len(state.turns),
        )

    with col3:
        st.metric(
            label="Agreement Level",
            value=f"{current_agreement}%",
            delta=f"{current_agreement - 50}% vs initial" if len(state.turns) > 1 else None,
        )

    with col4:
        status_label = {
            "idle": "⚪ Ready",
            "in_progress": "🟡 Debating",
            "consensus_reached": "🟢 Consensus Reached",
            "max_rounds_reached": "🔵 Max Rounds Ended",
            "stalemate": "🔴 Stalemate",
        }.get(state.status, state.status)
        st.metric(label="Status", value=status_label)

    # Convergence progression line chart if we have > 1 turn
    if len(state.turns) > 1:
        scores_by_turn = [t.response.agreement_score for t in state.turns]
        chart_df = pd.DataFrame(
            {"Agreement (%)": scores_by_turn},
            index=[f"T{i+1}" for i in range(len(state.turns))],
        )
        st.line_chart(chart_df, height=140)


def render_final_verdict(state: DebateState):
    """
    Renders the celebratory Final Verdict & Synthesis card when the debate concludes.
    """
    if not state.final_verdict:
        return

    verdict = state.final_verdict

    st.markdown(
        f"""
        <div class="verdict-card">
            <div class="verdict-title">
                🏆 Final Synthesized Verdict
            </div>
            <p style="font-size: 0.9rem; color: #6EE7B7; margin-bottom: 1rem;">
                <b>Conclusion:</b> {verdict.conclusion_reason} (Consensus Rating: {verdict.final_consensus_score}%)
            </p>
            <div style="background: rgba(0,0,0,0.25); border-radius: 10px; padding: 1.2rem; margin-bottom: 1rem; color: #F1F5F9; font-size: 1.05rem; line-height: 1.6;">
                {verdict.summary_verdict}
            </div>
        """,
        unsafe_allow_html=True,
    )

    if verdict.agreed_points:
        st.markdown("**🤝 Key Principles Agreed by Both Debaters:**")
        for pt in verdict.agreed_points:
            st.markdown(f"- ✅ **{pt}**")

    if verdict.remaining_nuances:
        st.markdown("**⚖️ Remaining Nuances & Distinct Considerations:**")
        for nu in verdict.remaining_nuances:
            st.markdown(f"- 🔍 *{nu}*")

    st.markdown("</div>", unsafe_allow_html=True)
