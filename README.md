# ⚖️ Debate-Club: Graphic Novel Arena & Collegiate Dialectic

> **A Multi-LLM Competitive Deliberation Arena with Supreme Judge Dredd and Graphic Novel Speech Balloons**

**Debate-Club** pits elite AI models against each other on an illustrated debate arena stage. Characters (**Alex in Blue**, **Charlie in Purple**, **Shahar in Red**) defend dynamically assigned stances with causal warrants, execute championship rebuttals (**Link Turns**, **Even-If Concessions**), and form tactical non-polar coalitions while **Supreme Judge Dredd** adjudicates every round from his high throne and decrees the Grand Champion!

---

## 🌟 Key Features

- 🎭 **Graphic Novel Speech Balloon Stage**:
  - Live animated speech balloons over the speakers' podiums.
  - While an upcoming speaker formulates their point, the previous speaker's argument remains on stage with a live broadcast ticker.
  - Supreme Judge Dredd's elevated golden speech balloon delivers round rulings and final championship decrees.
- ⚖️ **Automated Complexity & Dynamic Stance Assignment**:
  - Supreme Judge Dredd automatically evaluates question complexity:
    - **Binary Topics** $\rightarrow$ 2 Debaters (Alex vs Charlie).
    - **Nuanced Topics** $\rightarrow$ 3 Debaters (Alex, Charlie, and Shahar).
  - Stances are bespoke and assigned per question.
- 🏆 **WUDC / Oxford Union Competitive Debate Standards**:
  - **AREI / SEAL Structure**: Assertion $\rightarrow$ Reasoning (Causal Warrants) $\rightarrow$ Evidence $\rightarrow$ Impact.
  - **Championship Rebuttal Arsenal**: Link Turns, "Even-If" delta refutations, mechanism breakdowns, and impact mitigations.
  - **Comparative Impact Calculus**: Clashing along Magnitude, Severity/Irreversibility, Probability, and Timeframe.
- 🤝 **Strategic Non-Polar Alliances**:
  - 3-way debate dynamics where middle-ground debaters can form tactical coalitions on shared premises against polar extremes.
- ⚖️ **Supreme Judge Dredd Scoreboard**:
  - Points allocated on **Mechanistic Warrants (0–10)**, **Clash & Rebuttals (0–10)**, and **Comparative Weighing (0–10)**.
  - Full round decrees, decisive clash point analysis, and transcript exports.
- 🤖 **Universal Multi-LLM Support**:
  - OpenAI (GPT-4o, GPT-5, o1, o3-mini)
  - Anthropic Claude
  - Google Gemini
  - xAI Grok
  - Groq Llama
  - Local Machine (Ollama: Qwen, Llama, DeepSeek-R1)
  - Offline Simulators

---

## 📦 Project Structure

```
debate-club/
├── app.py                     # Streamlit Web Application
├── cli.py                     # Command Line Interface (CLI) runner
├── requirements.txt           # Python dependencies
├── assets/                    # Arena stage artwork & character portraits
├── models/                    # Pydantic schemas & state models
│   ├── turn_response.py       # AREI, Link Turns, Warrants, and Weighing schema
│   └── debate_state.py        # DebateState, DebaterScore, JudgeRoundEvaluation
├── interfaces/                # Multi-provider LLM API Layer & robust JSON auto-repair
│   ├── llms.py                # OpenAI, Anthropic, Gemini, Grok, Groq, Ollama
│   └── model_registry.py      # Dynamic model discovery & local Ollama health checks
├── prompting/                 # Championship Prompt Engineering
│   ├── debater_prompts.py     # AREI, 4-step refutation, link turns, even-if
│   ├── judge_prompts.py       # WUDC / OIV adjudication & Judge Dredd decrees
│   └── stance_generator.py    # Automated complexity & stance assignment
├── debate/                    # Core Debate Orchestration
│   ├── debater.py             # Debater agent wrapper
│   ├── judge.py               # Supreme Judge Dredd scoring & evaluations
│   ├── moderator.py           # Consensus evaluator & synthesizer
│   └── engine.py              # Central debate loop coordinator
└── views/                     # Streamlit Presentation Components
    ├── styles.py              # Dark-mode glassmorphic styling & speech balloon CSS
    ├── stage.py               # Main debate arena photo with reactive speech bubbles
    ├── scoreboard.py          # Judge Dredd chamber, leaderboard, and clash breakdown
    ├── timeline.py            # Chronological graphic-novel dialogue stream
    └── control_panel.py       # Sidebar configuration & model selectors
```

---

## ⚙️ Installation & Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Keys (`.env`)** *(Optional if using Ollama or Simulator)*:
   ```env
   OPENAI_API_KEY=your_openai_key
   ANTHROPIC_API_KEY=your_anthropic_key
   GOOGLE_API_KEY=your_gemini_key
   GROQ_API_KEY=your_groq_key
   GROK_API_KEY=your_grok_key
   ```

---

## 🖥️ Running the Application

### Web UI (Streamlit)
```bash
streamlit run app.py
```

### CLI Mode
```bash
python cli.py --question "Should AI models have legal personhood rights?" --debater1 gpt-4o --debater2 claude-3-5-sonnet-latest --rounds 3
```
