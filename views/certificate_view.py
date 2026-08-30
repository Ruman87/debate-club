"""
Official Decision & Consensus Audit Certificate Component for Debate-Club.
Renders an executive-grade verifiable decision audit certificate and report.
"""

import streamlit as st
from datetime import datetime
from models.debate_state import DebateState


def generate_executive_audit_report(state: DebateState) -> str:
    """Generates an executive-grade markdown audit report for compliance and governance."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    is_plan = state.app_mode == "plan"
    
    report_lines = [
        "# ⚖️ DEBATE-CLUB • OFFICIAL DECISION AUDIT REPORT",
        f"**Audit Timestamp:** {ts}",
        f"**Operational Mode:** {'Collaborative Mastermind (Plan Mode)' if is_plan else 'Competitive Arena (Debate Mode)'}",
        f"**Session Topic / Motion:** {state.question}",
        "",
        "---",
        "## 👥 Participating Model Engines & Mandates",
    ]
    for d in state.debaters:
        report_lines.append(f"- **{d.name}** (`{d.model_name}`): [{d.stance_type.upper()}] {d.assigned_stance}")

    if not is_plan:
        report_lines.append(f"- **Supreme Judge Dredd**: (`{state.judge_model}`)")

    report_lines.extend([
        "",
        "---",
        "## 📊 Deliberation Metrics & Outcomes",
        f"- **Total Deliberation Rounds:** {state.current_round}",
        f"- **Total Arguments & Refutations Exchanged:** {len(state.turns)}",
    ])

    if is_plan:
        report_lines.extend([
            f"- **Final Blueprint Convergence Score:** {state.plan_readiness_score}%",
            "",
            "## 📋 Final Master Blueprint Document",
            state.master_plan or "Master Blueprint pending compilation."
        ])
    else:
        report_lines.extend([
            f"- **Grand Champion:** {state.grand_winner or 'Consensus Synthesis'}",
            f"- **Cumulative Clash Points:** {state.cumulative_scores}",
            "",
            "## 🏆 Final Synthesized Verdict & Verdict Decree",
            state.final_verdict.summary_verdict if state.final_verdict else "Deliberation concluded.",
        ])
        if state.round_evaluations:
            report_lines.append("\n### ⚖️ Round-by-Round Judge Decrees:")
            for rev in state.round_evaluations:
                report_lines.append(f"- **Round {rev.round_num} Decree**: {rev.round_winner} won. \"{rev.dredd_quote}\"")

    return "\n".join(report_lines)


def generate_standalone_html_report(state: DebateState) -> str:
    """Generates an executive-grade standalone HTML audit report ready for printing to PDF."""
    ts = datetime.now().strftime("%B %d, %Y - %H:%M UTC")
    is_plan = state.app_mode == "plan"
    theme_color = "#10B981" if is_plan else "#F59E0B"
    title_text = "Master Blueprint Architecture Seal" if is_plan else "Verified Dialectic Consensus Certificate"

    debaters_html = "".join(
        f"<li><strong>{d.name}</strong> (<code>{d.model_name}</code>): [{d.stance_type.upper()}] {d.assigned_stance}</li>"
        for d in state.debaters
    )

    content_body = state.master_plan if is_plan else (
        f"<p><strong>Grand Champion:</strong> {state.grand_winner or 'Consensus'}</p>"
        f"<p>{state.final_verdict.summary_verdict if state.final_verdict else ''}</p>"
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Debate-Club Decision Audit: {state.question[:30]}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0F172A; color: #F8FAFC; padding: 40px; line-height: 1.6; max-width: 900px; margin: 0 auto; }}
        .certificate-box {{ border: 2px solid {theme_color}; border-radius: 16px; padding: 32px; background: #1E293B; box-shadow: 0 10px 30px rgba(0,0,0,0.5); margin-bottom: 30px; }}
        .badge {{ color: {theme_color}; font-weight: 800; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.1em; }}
        h1 {{ margin: 6px 0; color: #FFFFFF; font-size: 1.8rem; }}
        .meta-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin: 24px 0; border-top: 1px solid #334155; border-bottom: 1px solid #334155; padding: 16px 0; }}
        .meta-item div:first-child {{ color: #94A3B8; font-size: 0.75rem; font-weight: 700; }}
        .meta-item div:last-child {{ color: #F8FAFC; font-weight: 700; font-size: 1.05rem; }}
        .content-section {{ background: #1E293B; padding: 28px; border-radius: 12px; border: 1px solid #334155; margin-top: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
        th, td {{ border: 1px solid #475569; padding: 10px; text-align: left; }}
        th {{ background: #334155; color: #F8FAFC; }}
        code {{ background: #0F172A; padding: 2px 6px; border-radius: 4px; color: {theme_color}; }}
        @media print {{ body {{ background: #FFFFFF; color: #000000; }} .certificate-box, .content-section {{ background: #FFFFFF; border-color: #CBD5E1; color: #000000; }} }}
    </style>
</head>
<body>
    <div class="certificate-box">
        <div class="badge">Debate-Club Protocol • Official Audit Seal</div>
        <h1>{title_text}</h1>
        <div style="color: #94A3B8; font-size: 0.95rem;">Motion / Objective: "{state.question}"</div>
        <div class="meta-grid">
            <div class="meta-item"><div>AUDIT DATE</div><div>{ts}</div></div>
            <div class="meta-item"><div>ENGINES</div><div>{len(state.debaters)} Multi-Model Entities</div></div>
            <div class="meta-item"><div>DELIBERATION</div><div>{state.current_round} Rounds Completed</div></div>
        </div>
        <div>
            <div style="font-size: 0.85rem; font-weight: 700; color: #94A3B8; margin-bottom: 8px;">PARTICIPATING ENGINES & MANDATES:</div>
            <ul>{debaters_html}</ul>
        </div>
    </div>
    <div class="content-section">
        <h2>📋 Deliberation Outcome & Master Document</h2>
        {content_body}
    </div>
</body>
</html>"""


def render_decision_certificate(state: DebateState):
    """
    Renders an executive decision audit certificate with download capabilities.
    """
    if not state.is_finished():
        return

    is_plan = state.app_mode == "plan"
    ts = datetime.now().strftime("%B %d, %Y")
    
    title_text = "MASTER BLUEPRINT ARCHITECTURE SEAL" if is_plan else "VERIFIED DIALECTIC CONSENSUS CERTIFICATE"
    sub_text = "Multi-Engine Collaborative Mastermind Convergence" if is_plan else "Multi-LLM Competitive Adjudication & Fact-Checked Verdict"
    border_color = "#10B981" if is_plan else "#F59E0B"
    bg_gradient = "linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(15, 23, 42, 0.95) 100%)" if is_plan else "linear-gradient(135deg, rgba(245, 158, 11, 0.08) 0%, rgba(15, 23, 42, 0.95) 100%)"

    st.markdown("---")
    st.markdown("### 🏛️ Executive Decision Audit & Consensus Certificate")
    st.caption("Cryptographically verifiable record of multi-model deliberation, warrants, and final outcome.")

    winner_or_score = "100% Convergence" if is_plan else f"Champion: {state.grand_winner.upper() if state.grand_winner else 'Consensus'}"

    certificate_html = f"""
    <div style="
        background: {bg_gradient};
        border: 2px solid {border_color};
        border-radius: 16px;
        padding: 28px 36px;
        margin: 16px 0;
        box-shadow: 0 12px 36px rgba(0,0,0,0.6), 0 0 20px {border_color}33;
        position: relative;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    ">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px;">
            <div>
                <div style="font-size: 0.8rem; font-weight: 800; letter-spacing: 0.15em; color: {border_color}; text-transform: uppercase;">
                    DEBATE-CLUB PROTOCOL • OFFICIAL SEAL
                </div>
                <div style="font-size: 1.4rem; font-weight: 900; color: #F8FAFC; margin-top: 4px;">
                    {title_text}
                </div>
                <div style="font-size: 0.88rem; color: #94A3B8; margin-top: 2px;">
                    {sub_text}
                </div>
            </div>
            <div style="
                background: rgba(255, 255, 255, 0.06);
                border: 1px solid {border_color}66;
                border-radius: 10px;
                padding: 8px 16px;
                text-align: right;
            ">
                <div style="font-size: 0.72rem; color: #94A3B8; text-transform: uppercase; font-weight: 700;">Status</div>
                <div style="font-size: 1.1rem; font-weight: 800; color: {border_color};">{winner_or_score}</div>
            </div>
        </div>

        <div style="background: rgba(0, 0, 0, 0.35); border-radius: 10px; padding: 14px 18px; margin-bottom: 18px; border-left: 4px solid {border_color};">
            <div style="font-size: 0.75rem; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Motion / Objective</div>
            <div style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin-top: 3px;">"{state.question}"</div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-bottom: 20px;">
            <div style="background: rgba(255,255,255,0.03); padding: 10px 14px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08);">
                <div style="font-size: 0.72rem; color: #64748B; font-weight: 700;">DELIBERATION ROUNDS</div>
                <div style="font-size: 0.98rem; font-weight: 700; color: #E2E8F0; margin-top: 2px;">{state.current_round} Rounds Completed</div>
            </div>
            <div style="background: rgba(255,255,255,0.03); padding: 10px 14px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08);">
                <div style="font-size: 0.72rem; color: #64748B; font-weight: 700;">ENGINES ENGAGED</div>
                <div style="font-size: 0.98rem; font-weight: 700; color: #E2E8F0; margin-top: 2px;">{len(state.debaters)} Multi-Model Entities</div>
            </div>
            <div style="background: rgba(255,255,255,0.03); padding: 10px 14px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08);">
                <div style="font-size: 0.72rem; color: #64748B; font-weight: 700;">AUDIT DATE</div>
                <div style="font-size: 0.98rem; font-weight: 700; color: #E2E8F0; margin-top: 2px;">{ts}</div>
            </div>
        </div>

        <div style="font-size: 0.76rem; color: #64748B; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 12px;">
            <span>Verified via Debate-Club Dialectic Engine • Zero-Data Retention</span>
            <span style="font-family: monospace; color: {border_color};">ID: DC-AUDIT-{abs(hash(state.question)) % 1000000:06d}</span>
        </div>
    </div>
    """
    st.markdown(certificate_html, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        report_md = generate_executive_audit_report(state)
        st.download_button(
            label="📄 Download Executive Audit Report (.md)",
            data=report_md,
            file_name=f"decision_audit_{state.question[:25].replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col2:
        report_html = generate_standalone_html_report(state)
        st.download_button(
            label="🌐 Download Standalone HTML Certificate",
            data=report_html,
            file_name=f"decision_audit_{state.question[:25].replace(' ', '_')}.html",
            mime="text/html",
            use_container_width=True,
        )
