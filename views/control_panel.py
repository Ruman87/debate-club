import streamlit as st
from typing import Dict, Any
from interfaces.llms import LLM
from interfaces.model_registry import (
    get_all_models_with_status,
    get_model_info_map,
    format_model_dropdown_label,
    get_recommended_default_indices,
    get_providers_status_summary,
    ModelCategory,
)

PRESET_QUESTIONS = [
    "Should AI developers prioritize open-weights models or closed API-only safety guardrails?",
    "Is artificial general intelligence (AGI) likely achievable via autoregressive next-token prediction alone?",
    "Should monolithic architectures or microservices be the default choice for early-stage software startups?",
    "Can free will exist in a deterministic universe?",
    "What is the most effective approach to mitigate algorithmic bias in automated hiring systems?",
]

PERSONA_OPTIONS = [
    "Dialectic Truth-Seeking",
    "Devil's Advocate",
    "Pragmatic Engineering & Trade-offs",
    "Proponent vs Skeptic",
    "Socratic Inquiry",
]


def _render_model_status_badge(model_id: str, model_info_map: Dict[str, Any]):
    """Renders a dynamic visual card below a model selector showing API / Local status."""
    info = model_info_map.get(model_id)
    if not info:
        return

    if info.category == ModelCategory.CLOUD_API:
        if info.is_available:
            st.markdown(
                f"""
                <div class="model-status-card status-active-api">
                    <span>🟢</span>
                    <div><strong>Cloud API:</strong> Connected via <code>{info.env_var}</code></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="model-status-card status-missing-key">
                    <span>⚠️</span>
                    <div><strong>Cloud API (Unconfigured):</strong> Missing <code>{info.env_var}</code> in <code>.env</code>. Add your key or choose a Local/Simulator model.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    elif info.category == ModelCategory.LOCAL_MACHINE:
        clean_name = model_id.replace("ollama/", "")
        if info.is_available:
            st.markdown(
                f"""
                <div class="model-status-card status-local-running">
                    <span>💻</span>
                    <div><strong>Local Machine:</strong> Running locally on your Mac via Ollama (Free, private, no API bill).</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif "Offline" in info.status_text:
            st.markdown(
                f"""
                <div class="model-status-card status-local-offline">
                    <span>⚪</span>
                    <div><strong>Local Machine (Offline):</strong> Ollama is not running. Run <code>ollama serve</code> in terminal to activate local execution.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="model-status-card status-missing-key">
                    <span>⚪</span>
                    <div><strong>Model Not Downloaded:</strong> Run <code>ollama pull {clean_name}</code> in terminal, or select an installed model (e.g. <code>deepseek-r1:1.5b</code>, <code>llama3.2:latest</code>).</div>
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
    Renders debate setup parameters, question input, model selection with status badges, and action triggers.
    """
    model_infos = get_all_models_with_status()
    model_info_map = {m.id: m for m in model_infos}
    all_models = [m.id for m in model_infos]

    # Calculate recommended defaults (favoring available models)
    default_d1_idx, default_d2_idx, default_d3_idx = get_recommended_default_indices(
        all_models, model_info_map
    )

    with st.sidebar:
        st.markdown("### ⚙️ Debate Configuration")

        # Provider & Key Status Overview Expander
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

        # Preset Question selection
        preset_choice = st.selectbox(
            "📚 Choose a Preset Question (or write your own below):",
            ["Custom Question..."] + PRESET_QUESTIONS,
            index=0,
        )

        default_question = (
            "" if preset_choice == "Custom Question..." else preset_choice
        )
        question = st.text_area(
            "💬 Question / Topic for Debate:",
            value=default_question,
            height=90,
            placeholder="e.g. Is next-token prediction sufficient to achieve general intelligence?",
        )

        st.markdown("---")
        st.markdown("#### 🤖 Debaters Roster")
        st.caption("⚖️ Supreme Judge Dredd automatically assigns stances and assesses if 2 or 3 debaters are optimal for the topic.")

        # Debater 1 (Alex)
        with st.expander("🔷 Debater 1: Alex", expanded=True):
            model1 = st.selectbox(
                "Model:",
                all_models,
                index=default_d1_idx,
                format_func=lambda m: format_model_dropdown_label(m, model_info_map),
                key="d1_model",
            )
            _render_model_status_badge(model1, model_info_map)

        # Debater 2 (Charlie)
        with st.expander("🟣 Debater 2: Charlie", expanded=True):
            model2 = st.selectbox(
                "Model:",
                all_models,
                index=default_d2_idx,
                format_func=lambda m: format_model_dropdown_label(m, model_info_map),
                key="d2_model",
            )
            _render_model_status_badge(model2, model_info_map)

        # Debater 3 (Shahar)
        with st.expander("🔥 Debater 3: Shahar (Summoned for Complex Topics)", expanded=True):
            model3 = st.selectbox(
                "Model:",
                all_models,
                index=default_d3_idx,
                format_func=lambda m: format_model_dropdown_label(m, model_info_map),
                key="d3_model",
            )
            _render_model_status_badge(model3, model_info_map)

        st.markdown("---")
        
        # AI Judge Dredd Configuration
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
                help="Supreme Judge Dredd evaluates every round, decrees winners in his elevated speech bubble, and crowns the final champion!",
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
            help="Competitive Dialectic tests assigned stances with point scoring.",
        )

        max_rounds = st.slider("⏱️ Max Rounds Limit:", min_value=2, max_value=6, value=3)

        # Check for any selected models with missing keys or offline status
        selected_models = [model1, model2, judge_model] + ([model3] if model3 else [])
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
            "question": question.strip(),
            "model1": model1,
            "model2": model2,
            "model3": model3,
            "judge_model": judge_model,
            "mode": mode,
            "max_rounds": max_rounds,
            "unready_warnings": unready_warnings,
            "is_valid": len(unready_warnings) == 0,
        }

