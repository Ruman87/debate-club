"""
Master Blueprint Viewer Component for Plan Mode in Debate-Club.
Renders the synthesized, executive-grade Master Blueprint Document with download options.
"""

import streamlit as st
from models.debate_state import DebateState


def render_master_blueprint(state: DebateState):
    """
    Renders the finalized Master Blueprint document with interactive metrics,
    risk mitigation tables, and a one-click download button.
    """
    if not state.master_plan:
        return

    st.markdown("---")
    st.markdown("### 📋 Final Master Blueprint & Action Plan")
    st.caption("Co-designed, stress-tested, and synthesized by the multi-engine AI Mastermind.")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            f"""
            <div style="background: rgba(16, 185, 129, 0.1); border: 2px solid #10B981; border-radius: 10px; padding: 14px; margin-bottom: 16px;">
                <div style="font-weight: 800; color: #10B981; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
                    <span>✨</span> MASTER BLUEPRINT READY • 100% READINESS
                </div>
                <div style="color: #E2E8F0; font-size: 0.92rem; margin-top: 4px;">
                    This document integrates foundational architecture, stress-tested risk mitigations, and a phased execution roadmap.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.download_button(
            label="📥 Download Blueprint (.md)",
            data=state.master_plan,
            file_name=f"master_blueprint_{state.question[:30].replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    # Master plan body
    with st.container():
        st.markdown(state.master_plan)

    st.markdown("---")
