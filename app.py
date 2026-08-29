"""
Debate-Club: Multi-LLM Dialectic Debate & Consensus Platform.
Streamlit Web Application Entry Point with Live Stage Updating & AI Judge.

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
from views.asset_loader import get_image_base64_data_uri

# Initialize environment and logging
load_dotenv(override=True)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("debate_club")

# Streamlit Page Configuration
st.set_page_config(
    layout="wide",
    page_title="Debate-Club | Multi-LLM Dialectic Arena",
    page_icon="⚖️",
    initial_sidebar_state="expanded",
)

# Apply CSS Styling
if hasattr(st, "html"):
    st.html(CUSTOM_CSS)
else:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# App Header
st.markdown(
    """
    <div class="main-header">
        <div class="main-title">⚖️ DEBATE-CLUB</div>
        <div class="subtitle">
            Multi-LLM Competitive Dialectic Deliberation Arena. Models debate assigned positions, 
            form strategic 2-vs-1 alliances, and earn points from the AI Judge!
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Render Sidebar Control Panel
config = render_control_panel()

# Initialize Session State
if "engine" not in st.session_state:
    st.session_state.engine = None
if "auto_run" not in st.session_state:
    st.session_state.auto_run = False


def start_debate():
    """Initializes a new debate session with assigned stances."""
    if not config["question"]:
        st.warning("⚠️ Please provide a question or topic to debate!")
        return

    if not config.get("is_valid", True):
        warning_msg = "\n".join(config.get("unready_warnings", []))
        st.error(
            f"🚫 **Cannot Start Debate: Unconfigured Model(s) Selected**\n\n"
            f"{warning_msg}\n\n"
            f"👉 *Select an active model from the sidebar (e.g. Ollama or Simulator), or add API key(s) to `.env`.*"
        )
        return

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
    Executes exactly one turn while proactively keeping the previous debater's
    argument displayed during thinking, then presenting the new speech balloon,
    and showing Judge Dredd's ruling when a round concludes.
    """
    if engine.is_finished():
        return

    # 1. Identify upcoming speaker
    next_idx = engine.state.current_turn_index % len(engine.debaters)
    next_debater = engine.debaters[next_idx]
    stance_str = getattr(next_debater.config, "stance_type", "for").upper()
    was_round_end = False

    # 2. Render live state: previous debater's point remains on stage, ticker indicates upcoming speaker
    with stage_ph.container():
        render_arena_stage(engine.state, upcoming_debater_idx=next_idx, is_thinking=True)

    # 3. Execute turn
    prog_bar = prog_ph.progress(
        0.2,
        text=f"🎙️ Round {engine.state.current_round}: {next_debater.name} ({next_debater.model_name}) is defending [{stance_str}]...",
    )
    try:
        prev_turns_count = len(engine.state.turns)
        engine.step_turn(prog_bar.progress)
        # Check if full round just concluded and Judge evaluated
        if len(engine.state.turns) % len(engine.debaters) == 0 and len(engine.state.turns) > prev_turns_count:
            was_round_end = True
    except Exception as e:
        st.error(f"❌ Error during turn execution: {e}")
        st.session_state.auto_run = False
    finally:
        prog_bar.empty()

    # 4. Render updated stage with completed speech balloon (or Judge Dredd if round concluded)
    with stage_ph.container():
        if was_round_end and engine.state.round_evaluations:
            render_arena_stage(engine.state, show_judge_verdict=True)
            if st.session_state.auto_run:
                time.sleep(2.5)  # Let user read Judge Dredd's round ruling
        else:
            render_arena_stage(engine.state, is_thinking=False)


# Top Action Control Bar
col1, col2, col3, col4 = st.columns([1.5, 1, 1, 1])

with col1:
    if st.button("🚀 Start New Debate", use_container_width=True, type="primary"):
        start_debate()
        st.rerun()

with col2:
    is_active = st.session_state.engine is not None and not st.session_state.engine.is_finished()
    next_turn_clicked = st.button("⏭️ Next Turn", disabled=not is_active, use_container_width=True)

with col3:
    is_active = st.session_state.engine is not None and not st.session_state.engine.is_finished()
    button_label = "⏸️ Pause" if st.session_state.auto_run else "⏩ Run Full Debate"
    if st.button(button_label, disabled=not is_active, use_container_width=True):
        st.session_state.auto_run = not st.session_state.auto_run
        st.rerun()

with col4:
    if st.button("🔄 Reset", use_container_width=True):
        st.session_state.engine = None
        st.session_state.auto_run = False
        st.rerun()

# Main Display Area
if st.session_state.engine is not None:
    engine: DebateEngine = st.session_state.engine

    st.markdown(f"#### ❓ Question: *\"{engine.state.question}\"*")
    st.markdown("---")

    # Placeholders for live reactive stage & progress updates
    prog_placeholder = st.empty()
    stage_placeholder = st.empty()

    # Handle manual Next Turn click
    if next_turn_clicked and not engine.is_finished():
        execute_turn_with_live_stage(engine, stage_placeholder, prog_placeholder)
        st.rerun()

    # Handle Auto-Run Loop Step
    elif st.session_state.auto_run and not engine.is_finished():
        execute_turn_with_live_stage(engine, stage_placeholder, prog_placeholder)
        time.sleep(1.8)  # Pacing pause so speech balloon can be comfortably read
        if st.session_state.auto_run and not engine.is_finished():
            st.rerun()
        else:
            st.session_state.auto_run = False
            st.rerun()
    else:
        # Default static render of the current state
        with stage_placeholder.container():
            render_arena_stage(engine.state, is_thinking=False)

    # 2. Render AI Judge Scoreboard, Alliances & Leaderboard
    render_judge_scoreboard(engine.state)

    # 3. Render chronological graphic novel speech balloon stream
    render_debate_timeline(engine.state)

    # 4. Render Final Verdict & Winner (if debate concluded)
    if engine.is_finished():
        if engine.state.grand_winner:
            st.success(f"🏆 **DEBATE CHAMPION DECLARED BY AI JUDGE: {engine.state.grand_winner.upper()}!**")
        render_final_verdict(engine.state)

        # Export debate transcript
        transcript_json = json.dumps(engine.state.model_dump(), default=str, indent=2)
        st.download_button(
            label="📥 Export Full Debate Transcript (JSON)",
            data=transcript_json,
            file_name=f"debate_transcript_{len(engine.state.turns)}_turns.json",
            mime="application/json",
        )

    # 5. Render Consensus Analytics & Convergence Graph
    with st.expander("📊 Consensus Analytics & Agreement Trajectory", expanded=engine.is_finished()):
        render_consensus_meter(engine.state)

else:
    # Welcome / Intro Screen
    if not config.get("is_valid", True):
        st.warning(
            "⚠️ **Unconfigured Cloud Models Selected in Sidebar:**\n\n"
            + "\n".join(config.get("unready_warnings", []))
            + "\n\nSwitch to **Local Machine (Ollama)** or **Simulator** models to run debates immediately, or add your API keys to `.env`."
        )

    hero_uri = get_image_base64_data_uri("assets/arena_stage.jpg")
    if hero_uri:
        st.markdown(
            f"""
            <div class="arena-stage-banner">
                <img src="{hero_uri}" style="width: 100%; height: auto; display: block;" alt="Debate Arena">
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.info(
        "👋 **Welcome to Debate-Club: Graphic Novel Arena!**\n\n"
        "**Debaters & Presiding Judge:**\n"
        "- 🔷 **Alex** (Blue Spotlight)\n"
        "- 🟣 **Charlie** (Purple Spotlight)\n"
        "- 🔥 **Shahar** (Red Spotlight — Summoned for complex topics)\n"
        "- ⚖️ **Supreme Judge Dredd**: Presides from his elevated throne, evaluates question complexity (2 or 3 debaters), dynamically assigns each model a bespoke position to defend, scores every round, and crowns the Grand Champion!\n\n"
        "Enter any debate question, select your models in the sidebar, and click **🚀 Start New Debate**!"
    )
