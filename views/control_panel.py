"""
Workspace Control Panel & Sidebar Component for Debate-Club.
Supports dual-mode routing (Debate Mode vs Plan Mode), industry decision templates,
in-app BYOK key vault, live web grounding, and model configuration.
"""

import os
import streamlit as st
from typing import Dict, Any, List, Optional
from interfaces.model_registry import (
    get_all_models_with_status,
    get_providers_status_summary,
    ModelCategory,
    ModelInfo,
)
from prompting.templates import DECISION_TEMPLATES, get_all_template_categories, get_templates_for_category

PRESET_QUESTIONS = [
    "Is AGI an imminent existential risk or an overhyped engineering milestone?",
    "Will nuclear energy be the dominant clean baseload power source by 2040?",
    "Should remote work be mandated as a legal employee right?",
    "Is next-token prediction sufficient to achieve general intelligence?",
    "Should my friend break up with his girlfriend? She is acting completely crazy.",
]

PRESET_BRAINSTORM_OBJECTIVES = [
    "Design a viral zero-budget launch strategy for a B2B AI agent platform",
    "Architect a real-time multimodal search engine handling 100k queries/sec",
    "Formulate a high-impact developer community growth loop for an open-source LLM framework",
    "Design an autonomous code-review agent pipeline with AST security gates",
]


def format_model_dropdown_label(model_id: str, model_info_map: Dict[str, ModelInfo]) -> str:
    info = model_info_map.get(model_id)
    if not info:
        return model_id
    
    if info.is_available:
        badge = "🟢 Ready"
    elif info.category == ModelCategory.CLOUD_API:
        badge = "⚠️ Key Required"
    elif "Offline" in info.status_text:
        badge = "⚪ Offline"
    else:
        badge = "📥 Pull Required"

    return f"{info.name} ({badge})"


def _render_model_status_badge(model_id: str, model_info_map: Dict[str, ModelInfo]):
    info = model_info_map.get(model_id)
    if not info:
        return

    if info.is_available:
        css_class = "status-active-api" if info.category == ModelCategory.CLOUD_API else "status-local-running"
    elif info.category == ModelCategory.CLOUD_API:
        css_class = "status-missing-key"
    elif "Offline" in info.status_text:
        css_class = "status-local-offline"
    else:
        css_class = "status-simulation"

    st.markdown(
        f"<div class='model-status-card {css_class}'>"
        f"<span>{info.icon}</span><strong>{info.name}</strong> • {info.status_text}"
        f"</div>",
        unsafe_allow_html=True,
    )


def render_control_panel() -> Dict[str, Any]:
    """
    Renders the sidebar configuration control panel and returns validated settings.
    """
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

        # 2. In-App BYOK (Bring Your Own Key) Vault
        with st.expander("🔑 BYOK API Key Vault (In-Memory)", expanded=False):
            st.caption("🔒 Keys are held in session memory for your browser session and never stored permanently.")
            custom_openai = st.text_input("OpenAI API Key:", type="password", value=os.getenv("OPENAI_API_KEY", ""), key="byok_openai")
            custom_anthropic = st.text_input("Anthropic API Key:", type="password", value=os.getenv("ANTHROPIC_API_KEY", ""), key="byok_anthropic")
            custom_gemini = st.text_input("Google Gemini API Key:", type="password", value=os.getenv("GOOGLE_API_KEY", ""), key="byok_gemini")
            custom_groq = st.text_input("Groq API Key:", type="password", value=os.getenv("GROQ_API_KEY", ""), key="byok_groq")
            
            if st.button("💾 Apply API Keys", key="btn_apply_keys", use_container_width=True):
                if custom_openai: os.environ["OPENAI_API_KEY"] = custom_openai.strip()
                if custom_anthropic: os.environ["ANTHROPIC_API_KEY"] = custom_anthropic.strip()
                if custom_gemini: os.environ["GOOGLE_API_KEY"] = custom_gemini.strip()
                if custom_groq: os.environ["GROQ_API_KEY"] = custom_groq.strip()
                st.success("✅ Keys loaded into session!")
                st.rerun()

        # 3. Provider & Key Status Overview Expander
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

        # 4. Session History Archive
        from debate.history_manager import list_saved_sessions, load_session, delete_session
        saved_list = list_saved_sessions()
        loaded_state = None
        if saved_list:
            with st.expander(f"📜 Session Archive ({len(saved_list)} saved)", expanded=False):
                sess_options = ["-- None --"] + [f"{s['file_id']} | {s['question'][:28]}..." for s in saved_list]
                selected_sess = st.selectbox(
                    "Browse past sessions:",
                    options=sess_options,
                    key="history_sess_select",
                )
                if selected_sess != "-- None --":
                    sess_file = selected_sess.split(" | ")[0]
                    col_l, col_d = st.columns(2)
                    if col_l.button("📂 Load", use_container_width=True, key="btn_load_sess"):
                        loaded_state = load_session(sess_file)
                    if col_d.button("🗑️ Delete", use_container_width=True, key="btn_del_sess"):
                        delete_session(sess_file)
                        st.rerun()

        # 5. Live Web Grounding Toggle
        enable_web_grounding = st.checkbox("🌐 Live Web Search Grounding (RAG)", value=True, help="Automatically searches the web to provide debaters with verifiable empirical citations.")

        # 6. Graphic Novel Reading Pace
        reading_pace = st.select_slider(
            "⏱️ Speech Bubble Reading Pace:",
            options=[2.0, 3.5, 4.5, 6.0],
            value=4.0,
            format_func=lambda x: f"{x}s ({'⚡ Fast Skim' if x <= 2.0 else '📖 Standard Comic' if x <= 3.5 else '🎨 Story Mode' if x <= 4.5 else '🧐 Deep Read'})",
            help="Time allocated for each speech balloon on stage so you have plenty of time to read before the next turn."
        )

        st.markdown("---")

        # Models Setup
        all_model_infos = get_all_models_with_status()
        model_info_map = {m.id: m for m in all_model_infos}
        all_models = [m.id for m in all_model_infos]

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

        # === 6. INDUSTRY TEMPLATES SELECTOR ===
        with st.expander("📚 Decision & Strategy Templates Library", expanded=False):
            template_cat = st.selectbox("Industry Category:", get_all_template_categories(), key="template_cat")
            cat_templates = get_templates_for_category(template_cat)
            template_choice = st.selectbox(
                "Choose Template:",
                ["-- Select a Template --"] + [t["title"] for t in cat_templates],
                key="template_choice"
            )
            template_question = ""
            if template_choice != "-- Select a Template --":
                match_t = next((t for t in cat_templates if t["title"] == template_choice), None)
                if match_t:
                    template_question = match_t["question"]
                    st.caption(f"Tags: {', '.join(match_t.get('tags', []))}")

        # === PLAN MODE CONFIGURATION ===
        if is_plan_mode:
            st.markdown("#### 📋 Collaborative Mastermind Setup")
            
            preset_choice = st.selectbox(
                "💡 Choose a Brainstorming Idea (or write custom objective below):",
                ["Custom Objective..."] + PRESET_BRAINSTORM_OBJECTIVES,
                index=0,
            )
            default_obj = template_question if template_question else ("" if preset_choice == "Custom Objective..." else preset_choice)
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
            with st.expander("🔷 Engine 1: Alex (Lead Architect & Visionary)", expanded=True):
                model1 = st.selectbox(
                    "Model:",
                    all_models,
                    index=default_d1_idx,
                    format_func=lambda m: format_model_dropdown_label(m, model_info_map),
                    key="plan_m1",
                )
                _render_model_status_badge(model1, model_info_map)

            # Engine 2 (Chief Risk & Stress-Tester)
            with st.expander("🟣 Engine 2: Charlie (Chief Risk & Stress-Tester / Red Team)", expanded=True):
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
                with st.expander("🔥 Engine 3: Shahar (Systems Synthesizer & Execution Lead)", expanded=True):
                    model3 = st.selectbox(
                        "Model:",
                        all_models,
                        index=default_d3_idx,
                        format_func=lambda m: format_model_dropdown_label(m, model_info_map),
                        key="plan_m3",
                    )
                    _render_model_status_badge(model3, model_info_map)

            judge_model = None
            mode = "Collaborative Mastermind"
            max_rounds = st.slider("⏱️ Mastermind Co-Design Iterations:", min_value=2, max_value=5, value=3)

        # === DEBATE MODE CONFIGURATION ===
        else:
            st.markdown("#### ⚔️ Debate Arena Setup")

            preset_choice = st.selectbox(
                "💡 Choose a Preset Motion (or write custom topic below):",
                ["Custom Question..."] + PRESET_QUESTIONS,
                index=0,
            )
            default_question = template_question if template_question else ("" if preset_choice == "Custom Question..." else preset_choice)
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
                    unready_warnings.append(f"• **{sm}**: Missing API key (`{info.env_var}`). Add in BYOK Vault or `.env`.")
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
            "loaded_state": loaded_state,
            "enable_web_grounding": enable_web_grounding,
            "reading_pace": reading_pace,
        }
