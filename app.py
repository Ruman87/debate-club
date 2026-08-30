"""
Debate-Club: Multi-LLM Dialectic Arena & Collaborative Mastermind Platform.
Streamlit Web Application supporting both Debate Mode (Competitive Arena with Judge Dredd)
and Plan Mode (Collaborative Co-Design & Master Blueprint Synthesis).

Run with:
    streamlit run app.py
"""

import os
import json
import time
import logging
import streamlit as st
from dotenv import load_dotenv

from models.debate_state import DebateState
from debate.engine import DebateEngine
from views.styles import CUSTOM_CSS
from views.control_panel import render_control_panel
from views.timeline import render_debate_timeline
from views.consensus_gauge import render_consensus_meter, render_final_verdict
from views.stage import render_arena_stage
from views.scoreboard import render_judge_scoreboard
from views.blueprint_view import render_master_blueprint
from views.certificate_view import render_decision_certificate
from views.asset_loader import get_image_base64_data_uri

# Initialize environment and logging
load_dotenv(override=True)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("debate_club")

# Streamlit Page Configuration
st.set_page_config(
    layout="wide",
    page_title="Debate-Club | Multi-LLM Arena & Mastermind",
    page_icon="⚖️",
    initial_sidebar_state="expanded",
)

# Apply CSS Styling
if hasattr(st, "html"):
    st.html(CUSTOM_CSS)
else:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Render Sidebar Control Panel
config = render_control_panel()
is_plan_mode = config.get("app_mode") == "plan"

# App Header
if is_plan_mode:
    st.markdown(
        """
        <div class="main-header">
            <div class="main-title">📋 DEBATE-CLUB • PLAN MODE</div>
            <div class="subtitle">
                Multi-Engine Collaborative Brainstorming Mastermind. Lead Architect, Red Team Stress-Tester, 
                and Systems Synthesizer work together without a judge to co-design a high-value Master Blueprint.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <div class="main-header">
            <div class="main-title">⚖️ DEBATE-CLUB • DEBATE ARENA</div>
            <div class="subtitle">
                Multi-LLM Competitive Dialectic Deliberation Arena. Models defend assigned positions, 
                form strategic coalitions, and earn points from Supreme Judge Dredd!
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Initialize Session State
if "engine" not in st.session_state:
    st.session_state.engine = None
if "auto_run" not in st.session_state:
    st.session_state.auto_run = False

# Handle session loaded from archive
if config.get("loaded_state") is not None:
    st.session_state.engine = DebateEngine(config["loaded_state"])
    st.session_state.auto_run = False


def start_session():
    """Initializes a new debate or brainstorming planning session based on selected mode."""
    if not config["question"]:
        st.warning("⚠️ Please provide a motion or brainstorm objective!")
        return

    if not config.get("is_valid", True):
        warning_msg = "\n".join(config.get("unready_warnings", []))
        st.error(
            f"🚫 **Cannot Start Session: Unconfigured Model(s) Selected**\n\n"
            f"{warning_msg}\n\n"
            f"👉 *Select an active model from the sidebar (e.g. Ollama or Simulator), or add API key(s) to `.env`.*"
        )
        return

    if is_plan_mode:
        engine = DebateEngine.create_plan_mode(
            objective=config["question"],
            engine1_model=config["model1"],
            engine2_model=config["model2"],
            engine3_model=config.get("model3"),
            num_engines=config.get("num_engines", 3),
            max_rounds=config["max_rounds"],
        )
    else:
        engine = DebateEngine.create_default(
            question=config["question"],
            debater1_model=config["model1"],
            debater2_model=config["model2"],
            debater3_model=config.get("model3"),
            judge_model=config.get("judge_model", "gpt-4o-mini"),
            mode=config["mode"],
            max_rounds=config["max_rounds"],
        )

    st.session_state.engine = engine
    st.session_state.auto_run = False


def execute_turn_with_live_stage(engine: DebateEngine, stage_ph, prog_ph):
    """
    Executes exactly one turn while keeping the previous debater's
    argument displayed during thinking, then presenting the new speech balloon,
    and showing Judge Dredd's ruling when a debate round concludes.
    """
    if engine.is_finished():
        return

    # 1. Identify upcoming speaker
    next_idx = engine.state.current_turn_index % len(engine.debaters)
    next_debater = engine.debaters[next_idx]
    is_plan = engine.state.app_mode == "plan"
    was_round_end = False

    # 2. Render live state
    with stage_ph.container():
        render_arena_stage(engine.state, upcoming_debater_idx=next_idx, is_thinking=True)

    # 3. Execute turn with progress
    role_label = next_debater.config.persona
    status_text = (
        f"🛠️ Iteration {engine.state.current_round}: {next_debater.name} ({next_debater.model_name}) is co-designing as [{role_label}]..."
        if is_plan
        else f"🎙️ Round {engine.state.current_round}: {next_debater.name} ({next_debater.model_name}) is defending [{getattr(next_debater.config, 'stance_type', 'for').upper()}]..."
    )
    prog_bar = prog_ph.progress(0.2, text=status_text)

    try:
        prev_turns_count = len(engine.state.turns)
        engine.step_turn(prog_bar.progress)
        if len(engine.state.turns) % len(engine.debaters) == 0 and len(engine.state.turns) > prev_turns_count:
            was_round_end = True
    except Exception as e:
        st.error(f"❌ Error during step execution: {e}")
        st.session_state.auto_run = False
    finally:
        prog_bar.empty()

    # 4. Render updated stage with completed speech balloon
    with stage_ph.container():
        if was_round_end and not is_plan and engine.state.round_evaluations:
            render_arena_stage(engine.state, show_judge_verdict=True)
            if st.session_state.auto_run:
                time.sleep(2.5)
        else:
            render_arena_stage(engine.state, is_thinking=False)


# Top Action Control Bar
col1, col2, col3, col4, col5 = st.columns([1.5, 0.95, 1.05, 1.15, 0.75])

start_btn_label = "🚀 Start Mastermind Plan" if is_plan_mode else "🚀 Start New Debate"
next_btn_label = "⏭️ Next Step" if is_plan_mode else "⏭️ Next Turn"
round_btn_label = "▶️ Run 1 Iteration" if is_plan_mode else "▶️ Run 1 Round"
run_all_label = "⏩ Run Full Mastermind" if is_plan_mode else "⏩ Run Full Debate"

with col1:
    if st.button(start_btn_label, use_container_width=True, type="primary"):
        start_session()
        st.rerun()

with col2:
    is_active = st.session_state.engine is not None and not st.session_state.engine.is_finished()
    next_turn_clicked = st.button(next_btn_label, disabled=not is_active, use_container_width=True)

with col3:
    is_active = st.session_state.engine is not None and not st.session_state.engine.is_finished()
    run_round_clicked = st.button(round_btn_label, disabled=not is_active, use_container_width=True)

with col4:
    is_active = st.session_state.engine is not None and not st.session_state.engine.is_finished()
    button_label = "⏸️ Pause" if st.session_state.auto_run else run_all_label
    if st.button(button_label, disabled=not is_active, use_container_width=True):
        st.session_state.auto_run = not st.session_state.auto_run
        st.rerun()

with col5:
    if st.button("🔄 Reset", use_container_width=True):
        st.session_state.engine = None
        st.session_state.auto_run = False
        st.rerun()

# Main Display Area
if st.session_state.engine is not None:
    engine: DebateEngine = st.session_state.engine
    current_is_plan = engine.state.app_mode == "plan"

    query_label = "🎯 Brainstorm Objective" if current_is_plan else "❓ Motion"
    st.markdown(f"#### {query_label}: *\"{engine.state.question}\"*")
    st.markdown("---")

    # Placeholders for live reactive stage & progress updates
    prog_placeholder = st.empty()
    stage_placeholder = st.empty()

    # Handle manual Next Step click
    if next_turn_clicked and not engine.is_finished():
        execute_turn_with_live_stage(engine, stage_placeholder, prog_placeholder)
        st.rerun()

    # Handle Run 1 Round click
    elif run_round_clicked and not engine.is_finished():
        start_round = engine.state.current_round
        while not engine.is_finished() and engine.state.current_round == start_round:
            execute_turn_with_live_stage(engine, stage_placeholder, prog_placeholder)
            if not engine.is_finished() and engine.state.current_round == start_round:
                time.sleep(1.8)
        st.rerun()

    # Handle Auto-Run Loop Step
    elif st.session_state.auto_run and not engine.is_finished():
        execute_turn_with_live_stage(engine, stage_placeholder, prog_placeholder)
        time.sleep(1.8)
        if st.session_state.auto_run and not engine.is_finished():
            st.rerun()
        else:
            st.session_state.auto_run = False
            st.rerun()
    else:
        with stage_placeholder.container():
            render_arena_stage(engine.state, is_thinking=False)

    # 1.5 Live Audience Cross-Examination Injection (Mid-session human-in-the-loop)
    if not engine.is_finished():
        with st.expander("🎤 Inject Audience Cross-Examination / Challenge", expanded=False):
            col_inv1, col_inv2 = st.columns([3.5, 1])
            with col_inv1:
                inv_q = st.text_input(
                    "Your cross-examination question or objection:",
                    placeholder="e.g. But what about the latency bottleneck under 50k writes/sec?",
                    key="txt_user_intervention",
                )
            with col_inv2:
                st.write("")
                st.write("")
                if st.button("⚡ Inject Challenge", key="btn_inject_inv", use_container_width=True):
                    if inv_q:
                        engine.inject_user_intervention(inv_q)
                        st.success(f"✅ Challenge registered! Debaters will address this in their upcoming speech.")

    # 2. Render Scoreboard (Debate Mode only)
    if not current_is_plan:
        render_judge_scoreboard(engine.state)

    # 3. Render Final Master Blueprint (Plan Mode completed)
    if current_is_plan and engine.is_finished():
        render_master_blueprint(engine.state)

    # 4. Render Chronological Graphic Novel Dialogue Stream
    render_debate_timeline(engine.state)

    # 5. Render Final Verdict (Debate Mode completed)
    if not current_is_plan and engine.is_finished():
        if engine.state.grand_winner:
            st.success(f"🏆 **DEBATE CHAMPION DECLARED BY SUPREME JUDGE DREDD: {engine.state.grand_winner.upper()}!**")
        render_final_verdict(engine.state)

    # 6. Render Official Decision Audit Certificate (Completed Sessions)
    if engine.is_finished():
        render_decision_certificate(engine.state)

    # 7. Render Consensus Analytics (Debate Mode only)
    if not current_is_plan:
        with st.expander("📊 Consensus Analytics & Agreement Trajectory", expanded=engine.is_finished()):
            render_consensus_meter(engine.state)

else:
    # Welcome / Intro Screen
    if not config.get("is_valid", True):
        st.warning(
            "⚠️ **Unconfigured Cloud Models Selected in Sidebar:**\n\n"
            + "\n".join(config.get("unready_warnings", []))
            + "\n\nSwitch to **Local Machine (Ollama)** or **Simulator** models to run immediately, or add your API keys to `.env`."
        )

    hero_img = "assets/plan_stage.jpg" if is_plan_mode else "assets/arena_stage.jpg"
    hero_uri = get_image_base64_data_uri(hero_img)
    if hero_uri:
        st.markdown(
            f"""
            <div class="arena-stage-banner">
                <img src="{hero_uri}" style="width: 100%; height: auto; display: block;" alt="Debate Arena">
            </div>
            """,
            unsafe_allow_html=True,
        )

    if is_plan_mode:
        st.info(
            "📋 **Welcome to Debate-Club: Plan Mode (Brainstorming Mastermind)!**\n\n"
            "In Plan Mode, 2 or 3 AI engines work collaboratively as an elite mastermind without a judge:\n"
            "- 🔷 **Alex [Lead Architect]**: Formulates the core vision, value proposition, and workflows.\n"
            "- 🟣 **Charlie [Chief Risk & Stress-Tester]**: Red-teams the proposal, identifies hidden bottlenecks/costs, and injects remedies.\n"
            "- 🔥 **Shahar [Systems Synthesizer]**: Unifies trade-offs, operational milestones, and scaling execution.\n\n"
            "Select 2 or 3 engines in the sidebar, enter an idea to architect, and click **🚀 Start Mastermind Plan**!"
        )
    else:
        st.info(
            "👋 **Welcome to Debate-Club: Graphic Novel Arena!**\n\n"
            "**Debaters & Presiding Judge:**\n"
            "- 🔷 **Alex** (Blue Spotlight)\n"
            "- 🟣 **Charlie** (Purple Spotlight)\n"
            "- 🔥 **Shahar** (Red Spotlight — Summoned for complex topics)\n"
            "- ⚖️ **Supreme Judge Dredd**: Presides from his elevated throne, evaluates question complexity, dynamically assigns bespoke positions, scores every round, and crowns the Grand Champion!\n\n"
            "Enter any debate question, select your models in the sidebar, and click **🚀 Start New Debate**!"
        )
