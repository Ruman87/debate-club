"""
Master Blueprint Viewer Component for Plan Mode in Debate-Club.
Renders the synthesized, executive-grade Master Blueprint Document with structured tabs,
interactive Mermaid diagrams, and one-click export tools.
"""

import json
import streamlit as st
from models.debate_state import DebateState


def render_master_blueprint(state: DebateState):
    """
    Renders the finalized Master Blueprint document with interactive metrics,
    structured tabs, risk mitigation tables, and one-click download tools.
    """
    if not state.master_plan:
        return

    st.markdown("---")
    st.markdown("### 📋 Final Master Blueprint & Co-Designed Architecture")
    st.caption("Co-designed, stress-tested, and synthesized by the multi-engine AI Mastermind.")

    # Status Banner & Download Controls
    col1, col2, col3 = st.columns([2.5, 1, 1])
    with col1:
        st.markdown(
            f"""
            <div style="background: rgba(16, 185, 129, 0.12); border: 2px solid #10B981; border-radius: 10px; padding: 12px 16px; margin-bottom: 14px;">
                <div style="font-weight: 800; color: #10B981; font-size: 1.05rem; display: flex; align-items: center; gap: 8px;">
                    <span>✨</span> MASTER BLUEPRINT READY • 100% CONVERGENCE
                </div>
                <div style="color: #E2E8F0; font-size: 0.88rem; margin-top: 2px;">
                    Integrates verified system architecture, stress-tested risk mitigations, and phased execution milestones.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.download_button(
            label="📥 Download (.md)",
            data=state.master_plan,
            file_name=f"master_blueprint_{state.question[:25].replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col3:
        transcript_json = json.dumps(state.model_dump(), default=str, indent=2)
        st.download_button(
            label="📦 Export JSON",
            data=transcript_json,
            file_name=f"mastermind_session_{state.question[:25].replace(' ', '_')}.json",
            mime="application/json",
            use_container_width=True,
        )

    tab1, tab2, tab3 = st.tabs(["📖 Complete Blueprint", "🔍 Probed Risks & Mitigations", "📜 Mastermind Design Log"])

    with tab1:
        st.markdown(state.master_plan)

    with tab2:
        st.markdown("#### 🛡️ Stress-Testing Findings & Red-Team Mitigations")
        vuln_count = 0
        for t in state.turns:
            vulns = getattr(t.response, "vulnerabilities_identified", [])
            enhs = getattr(t.response, "proposed_enhancements", [])
            if vulns or enhs:
                vuln_count += 1
                with st.expander(f"Step #{t.turn_id}: {t.debater_name} ({t.model_name}) Contributions", expanded=True):
                    if vulns:
                        st.markdown(f"**🔍 Vulnerabilities Identified:**")
                        for v in vulns:
                            st.markdown(f"- ⚠️ {v}")
                    if enhs:
                        st.markdown(f"**🚀 Actionable Enhancements Injected:**")
                        for e in enhs:
                            st.markdown(f"- ✅ {e}")
        if vuln_count == 0:
            st.info("No isolated risk items logged outside the main document body.")

    with tab3:
        st.markdown("#### 💬 Collaborative Turn Summary")
        for t in state.turns:
            st.markdown(f"**Iteration {t.round_num} • {t.debater_name} ({t.model_name})**: {t.response.speech_bubble_summary or t.response.current_best_answer[:180]}")

    st.markdown("---")
