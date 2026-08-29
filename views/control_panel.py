"""
Sidebar Control Panel for Debate-Club supporting both Debate Mode (Arena)
and Plan Mode (Collaborative Mastermind Brainstorming).
"""

import streamlit as st
from typing import Dict, Any, List, Optional
from interfaces.model_registry import (
    get_all_models_with_status,
    get_providers_status_summary,
    ModelInfo,
    ModelCategory,
)

PRESET_QUESTIONS = [
    "Should society implement a mandatory 4-day work week?",
    "Is next-token prediction sufficient to achieve Artificial General Intelligence (AGI)?",
    "Should AI-generated code be allowed in safety-critical infrastructure without human review?",
    "Should open-weights frontier AI models be restricted by international treaties?",
    "Will autonomous AI agents create more net economic value than SaaS platforms by 2030?",
    "Is nuclear fission energy indispensable for powering future global AI compute clusters?",
]

PRESET_BRAINSTORM_OBJECTIVES = [
    "Design a viral, zero-budget launch strategy for a B2B AI agent platform",
    "Architect an ultra-low latency, edge-deployed real-time voice AI assistant",
    "Create a 6-month go-to-market plan for an open-source developer tool",
    "Design an autonomous pair-programming agent with proactive linting and AST refactoring",
    "Develop a sustainable monetization model for an open-source AI community",
]


def format_model_dropdown_label(model_id: str, model_info_map: Dict[str, ModelInfo]) -> str:
    info = model_info_map.get(model_id)
    if not info:
        return model_id
    status_icon = "🟢" if info.is_available else "⚪" if info.category == ModelCategory.LOCAL_MACHINE else "🔴"
    return f"{status_icon} {info.name} ({info.provider})"


def _render_model_status_badge(model_id: str, model_info_map: Dict[str, ModelInfo]):
    info = model_info_map.get(model_id)
    if not info:
        return

    if info.category == ModelCategory.CLOUD_API:
        if info.is_available:
            st.markdown(
                f"""
                <div class="model-status-card status-configured">
                    <span>🟢</span>
                    <div><strong>API Ready:</strong> <code>{info.env_var}</code> detected.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="model-status-card status-missing-key">
                    <span>⚠️</span>
                    <div><strong>Missing Key:</strong> Set <code>{info.env_var}</code> in your <code>.env</code> file.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    elif info.category == ModelCategory.LOCAL_MACHINE:
        if info.is_available:
            st.markdown(
                f"""
                <div class="model-status-card status-configured">
                    <span>🟢</span>
                    <div><strong>Local Ollama Ready:</strong> Running natively on your Mac.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif "Offline" in info.status_text:
            st.markdown(
                f"""
                <div class="model-status-card status-missing-key">
                    <span>🔴</span>
                    <div><strong>Ollama Offline:</strong> Start Ollama on your Mac (<code>ollama serve</code>).</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            clean_name = model_id.replace("ollama/", "")
            st.markdown(
                f"""
                <div class="model-status-card status-missing-key">
                    <span>⚪</span>
                    <div><strong>Model Not Downloaded:</strong> Run <code>ollama pull {clean_name}</code> in terminal, or select an installed model.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    elif info.category == ModelCategory.SIMULATION:
        st.markdown(
            f"""
            <div class="model-status-card status-simulation">
                <span>🧪</span>
                <div><strong>Built-in Simulator:</strong> Offline mock debater (Zero setup, 100% free, instant test responses).</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_control_panel() -> Dict[str, Any]:
    """
    Renders setup parameters for either Debate Mode (Arena) or Plan Mode (Collaborative Brainstorming).
    """
    model_infos = get_all_models_with_status()
    model_info_map = {m.id: m for m in model_infos}
    all_models = [m.id for m in model_infos]

    # Calculate recommended defaults
    default_d1_idx = 0
    default_d2_idx = min(1, len(all_models) - 1)
    default_d3_idx = min(2, len(all_models) - 1)

    for idx, m in enumerate(all_models):
        info = model_info_map.get(m)
        if info and info.is_available:
            default_d1_idx = idx
            break

    for idx in range(default_d1_idx + 1, len(all_models)):
        info = model_info_map.get(all_models[idx])
        if info and info.is_available:
            default_d2_idx = idx
            break

    for idx in range(default_d2_idx + 1, len(all_models)):
        info = model_info_map.get(all_models[idx])
        if info and info.is_available:
            default_d3_idx = idx
            break

    with st.sidebar:
        st.markdown("### ⚙️ Workspace Configuration")

        # 1. Operational Mode Switch
        mode_selection = st.radio(
            "🎯 Operational Mode:",
            ["⚔️ Debate Mode (Competitive Arena)", "📋 Plan Mode (Brainstorming Mastermind)"],
            index=0,
            help="Debate Mode features adversarial stances and Judge Dredd. Plan Mode collaborates to co-design a high-value Master Blueprint without a judge.",
        )
        is_plan_mode = "Plan" in mode_selection
        app_mode = "plan" if is_plan_mode else "debate"

        # 2. Provider & Key Status Overview Expander
        with st.expander("📊 Provider & API Status", expanded=False):
            summaries = get_providers_status_summary()
            for s in summaries:
                icon = "🟢" if s["is_active"] else "⚠️" if s["type"] == "Cloud API" else "⚪"
                status_class = "active" if s["is_active"] else "inactive"
                st.markdown(
                    f"<div class='provider-pill {status_class}'>"
                    f"<span>{icon}</span><strong>{s['provider']}</strong>: {s['detail']}"
                    f"</div>",
                    unsafe_allow_html=True,
                )
            st.caption("💡 **Tip:** To use Cloud APIs, add keys to `.env`. Local Ollama models run free on your Mac.")

        st.markdown("---")

        # === PLAN MODE CONFIGURATION ===
        if is_plan_mode:
            st.markdown("#### 📋 Collaborative Mastermind Setup")
            
            preset_choice = st.selectbox(
                "💡 Choose a Brainstorming Idea (or write custom objective below):",
                ["Custom Objective..."] + PRESET_BRAINSTORM_OBJECTIVES,
                index=0,
            )
            default_obj = "" if preset_choice == "Custom Objective..." else preset_choice
            question = st.text_area(
                "🎯 Brainstorm Objective / Idea to Architect:",
                value=default_obj,
                height=90,
                placeholder="e.g. Design a viral zero-budget launch strategy for a B2B AI agent...",
            )

            num_engines = st.radio(
                "👥 Number of Brainstorming Engines:",
                options=[2, 3],
                index=1,
                horizontal=True,
                help="Select 2 engines (Lead Architect + Stress-Tester) or 3 engines (+ Systems Synthesizer).",
            )

            st.markdown("##### 🤖 Brainstorming Mastermind Roles")
            st.caption("Engines collaborate iteratively to stress-test and co-design a finalized Master Blueprint.")

            # Engine 1 (Lead Architect)
            with st.expander("🔷 Engine 1: Alex [Lead Architect]", expanded=True):
                model1 = st.selectbox(
                    "Model:",
                    all_models,
                    index=default_d1_idx,
                    format_func=lambda m: format_model_dropdown_label(m, model_info_map),
                    key="plan_m1",
                )
                _render_model_status_badge(model1, model_info_map)

            # Engine 2 (Chief Risk & Stress-Tester)
            with st.expander("🟣 Engine 2: Charlie [Chief Risk & Stress-Tester]", expanded=True):
                model2 = st.selectbox(
                    "Model:",
                    all_models,
                    index=default_d2_idx,
                    format_func=lambda m: format_model_dropdown_label(m, model_info_map),
                    key="plan_m2",
                )
                _render_model_status_badge(model2, model_info_map)

            # Engine 3 (Systems Synthesizer)
            model3 = None
            if num_engines >= 3:
                with st.expander("🔥 Engine 3: Shahar [Systems Synthesizer]", expanded=True):
                    model3 = st.selectbox(
                        "Model:",
                        all_models,
                        index=default_d3_idx,
                        format_func=lambda m: format_model_dropdown_label(m, model_info_map),
                        key="plan_m3",
                    )
                    _render_model_status_badge(model3, model_info_map)

            max_rounds = st.slider("🔄 Brainstorming Iterations:", min_value=2, max_value=5, value=3)
            judge_model = None
            mode = "Collaborative Mastermind"

        # === DEBATE MODE CONFIGURATION ===
        else:
            st.markdown("#### ⚔️ Competitive Debate Arena Setup")

            preset_choice = st.selectbox(
                "📚 Choose a Preset Motion (or write custom topic below):",
                ["Custom Motion..."] + PRESET_QUESTIONS,
                index=0,
            )
            default_question = "" if preset_choice == "Custom Motion..." else preset_choice
            question = st.text_area(
                "💬 Question / Motion for Debate:",
                value=default_question,
                height=90,
                placeholder="e.g. Is next-token prediction sufficient to achieve general intelligence?",
            )

            st.markdown("##### 🤖 Debaters Roster")
            st.caption("⚖️ Supreme Judge Dredd automatically assigns stances and assesses if 2 or 3 debaters are optimal.")

            with st.expander("🔷 Debater 1: Alex", expanded=True):
                model1 = st.selectbox(
                    "Model:",
                    all_models,
                    index=default_d1_idx,
                    format_func=lambda m: format_model_dropdown_label(m, model_info_map),
                    key="debate_m1",
                )
                _render_model_status_badge(model1, model_info_map)

            with st.expander("🟣 Debater 2: Charlie", expanded=True):
                model2 = st.selectbox(
                    "Model:",
                    all_models,
                    index=default_d2_idx,
                    format_func=lambda m: format_model_dropdown_label(m, model_info_map),
                    key="debate_m2",
                )
                _render_model_status_badge(model2, model_info_map)

            with st.expander("🔥 Debater 3: Shahar (Summoned for Complex Topics)", expanded=True):
                model3 = st.selectbox(
                    "Model:",
                    all_models,
                    index=default_d3_idx,
                    format_func=lambda m: format_model_dropdown_label(m, model_info_map),
                    key="debate_m3",
                )
                _render_model_status_badge(model3, model_info_map)

            st.markdown("---")
            with st.expander("⚖️ Supreme Judge Dredd (Chief Adjudicator)", expanded=True):
                judge_idx = 0
                for idx, m in enumerate(all_models):
                    if m in ["gpt-4o-mini", "gemini-3.6-flash", "gemini-flash-latest"]:
                        info = model_info_map.get(m)
                        if info and info.is_available:
                            judge_idx = idx
                            break

                judge_model = st.selectbox(
                    "Judge Model:",
                    all_models,
                    index=judge_idx,
                    format_func=lambda m: format_model_dropdown_label(m, model_info_map),
                    key="judge_model",
                )
                _render_model_status_badge(judge_model, model_info_map)

            mode = st.selectbox(
                "🎭 Debate Philosophy:",
                [
                    "Competitive Dialectic",
                    "Dialectic Truth-Seeking",
                    "Pragmatic Engineering & Trade-offs",
                    "Proponent vs Skeptic",
                    "Socratic Inquiry",
                ],
                index=0,
            )
            max_rounds = st.slider("⏱️ Max Rounds Limit:", min_value=2, max_value=6, value=3)
            num_engines = None

        # Check for unready warnings
        selected_models = [model1, model2] + ([model3] if model3 else []) + ([judge_model] if judge_model else [])
        unready_warnings = []
        for sm in selected_models:
            info = model_info_map.get(sm)
            if info and not info.is_available:
                if info.category == ModelCategory.CLOUD_API:
                    unready_warnings.append(f"• **{sm}**: Missing API key (`{info.env_var}`).")
                elif info.category == ModelCategory.LOCAL_MACHINE:
                    if "Offline" in info.status_text:
                        unready_warnings.append(f"• **{sm}**: Local Ollama server is offline.")
                    else:
                        clean_name = sm.replace("ollama/", "")
                        unready_warnings.append(f"• **{sm}**: Model not downloaded on Mac (run `ollama pull {clean_name}`).")

        return {
            "app_mode": app_mode,
            "question": question.strip(),
            "model1": model1,
            "model2": model2,
            "model3": model3,
            "judge_model": judge_model,
            "num_engines": num_engines,
            "mode": mode,
            "max_rounds": max_rounds,
            "unready_warnings": unready_warnings,
            "is_valid": len(unready_warnings) == 0,
        }
