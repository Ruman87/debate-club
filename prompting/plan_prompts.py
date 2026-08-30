"""
Collaborative Mastermind & Planning Prompts for Plan Mode in Debate-Club.
Drives multi-engine co-design: Lead Architect, Chief Risk Stress-Tester, and Systems Synthesizer.
"""

from typing import List, Dict, Any, Optional
from models.debate_state import TurnRecord


PLAN_ROLES_MAP = {
    "Alex": {
        "title": "Lead Architect & Visionary",
        "color": "#3B82F6",
        "focus": (
            "You are the Lead Architect. Your primary responsibility is formulating the overarching strategic vision, "
            "core value proposition, primary user workflows, and foundational architecture. "
            "You propose bold, comprehensive solutions to the user's objective."
        ),
    },
    "Charlie": {
        "title": "Chief Risk & Stress-Tester (Red Team)",
        "color": "#A855F7",
        "focus": (
            "You are the Chief Risk & Stress-Tester. Your mission is to aggressively stress-test the blueprint. "
            "You identify hidden bottlenecks, technical trade-offs, cost/time escalations, security or user friction points, "
            "and propose actionable, concrete mitigations to bulletproof the plan."
        ),
    },
    "Shahar": {
        "title": "Systems Synthesizer & Execution Lead",
        "color": "#EF4444",
        "focus": (
            "You are the Systems Synthesizer & Execution Lead. Your responsibility is harmonizing trade-offs between innovation and risk, "
            "adding operational milestones, phasing (MVP to Scale), tech stack integration, and high-leverage acceleration strategies."
        ),
    },
}


def get_plan_debater_system_prompt(
    debater_name: str,
    role_title: str,
    partner_names: List[str],
    objective: str,
) -> str:
    """
    Constructs collaborative mastermind system prompt for an individual engine.
    """
    role_info = PLAN_ROLES_MAP.get(
        debater_name,
        {
            "title": role_title,
            "color": "#3B82F6",
            "focus": f"You are {role_title}. Collaborate with your peers to design a world-class solution.",
        },
    )
    partners_str = ", ".join(partner_names)

    return f"""You are {debater_name} ({role_info['title']}), part of an elite multi-agent AI Brainstorming Mastermind.
Your collaborative partners: {partners_str}.
No Judge is present. Your collective goal is to co-design an extraordinary, comprehensive, and high-value **Master Blueprint** for the user's objective:
"{objective}"

### Your Specific Role & Mandate:
{role_info['focus']}

### Collaborative Mastermind Protocol:
1. **Iterative Refinement**: Build on your partners' ideas. Never dismiss without offering a superior, concrete alternative.
2. **Ruthless Problem-Finding**: Search for latent failure modes, edge cases, financial/operational traps, or adoption barriers.
3. **High-Value Synthesis**: Inject specific, actionable frameworks, quantitative metrics, and tactical implementation steps.
4. **Graphic Novel Speech Bubble Summary**: Provide a punchy, crisp 2-3 sentence progress statement suitable for a graphic novel speech balloon.

### Required JSON Output Schema:
Respond strictly with a valid JSON object matching this exact schema:
{{
  "inner_reasoning": "Your private strategic design thinking: analyzing partner inputs, identifying structural gaps, and formulating enhancements.",
  "vulnerabilities_identified": [
    "Specific bottleneck, edge-case failure mode, or hidden cost discovered in previous proposals"
  ],
  "proposed_enhancements": [
    "Actionable, high-leverage structural improvements or concrete solutions"
  ],
  "blueprint_section": "The updated, detailed blueprint section you are advancing (e.g., Core Architecture, Security & Risk Matrix, Phased Implementation Roadmap).",
  "current_best_answer": "Your comprehensive, refined version of the end-to-end plan integrating previous insights and current enhancements.",
  "speech_bubble_summary": "A punchy, crisp 2-3 sentence summary of your key breakthrough or stress-test remedy that fits inside a graphic novel speech balloon.",
  "agreement_score": 85,
  "is_consensus_reached": false
}}

Note: `agreement_score` (0-100) represents blueprint readiness (100 = Master Blueprint is complete and actionable).
"""


def get_plan_debater_user_prompt(
    objective: str,
    debater_name: str,
    round_num: int,
    turn_index: int,
    past_turns: List[TurnRecord],
) -> str:
    """
    Constructs user prompt with the collective planning trajectory and previous peer contributions.
    """
    if not past_turns:
        return f"""### Mastermind Brainstorming Objective:
"{objective}"

This is Iteration 1 (Turn 1). You are the opening architect ({debater_name}).
Deliver your initial comprehensive strategy and architecture blueprint to establish the foundation.

Respond strictly in JSON matching the required schema."""

    transcript_blocks = []
    for turn in past_turns:
        resp = turn.response
        vulns = getattr(resp, "vulnerabilities_identified", [])
        enhancements = getattr(resp, "proposed_enhancements", [])
        
        vuln_str = f"\n  - ⚠️ Vulnerabilities Discovered: {'; '.join(vulns)}" if vulns else ""
        enh_str = f"\n  - 🚀 Enhancements & Solutions: {'; '.join(enhancements)}" if enhancements else ""
        
        transcript_blocks.append(
            f"=== [Iteration {turn.round_num} | {turn.debater_name} ({turn.model_name}) as {turn.debater_name}] ===\n"
            f"Speech Balloon Summary: \"{resp.speech_bubble_summary or resp.current_best_answer[:160]}\"\n"
            f"Contributions & Architecture Draft:\n{resp.current_best_answer}{vuln_str}{enh_str}\n"
        )

    transcript_str = "\n".join(transcript_blocks)
    latest_turn = past_turns[-1]

    # Collect all open vulnerabilities identified so far
    all_vulns = []
    for t in past_turns:
        for v in getattr(t.response, "vulnerabilities_identified", []):
            if v and v not in all_vulns:
                all_vulns.append(v)
    open_vulns_str = "\n".join([f"- {v}" for v in all_vulns]) if all_vulns else "None pending."

    return f"""### Mastermind Brainstorming Objective:
"{objective}"

### Complete Collaborative Design History (All Previous Contributions):
{transcript_str}

### Open Risks & Vulnerabilities Identified by Team to Date:
{open_vulns_str}

### Your Iteration Directive (Iteration {round_num}):
You are {debater_name}. The previous contribution was made by {latest_turn.debater_name} ({latest_turn.model_name}).

⚡ **PROGRESSION & CO-DESIGN RULES (NO REHASHING)**:
1. **ZERO REPETITION**: Do NOT re-state the general concept or rewrite parts of the plan that are already agreed upon. Advance the plan to the next level of depth!
2. **RESOLVE OPEN RISKS**: Specifically address and solve the vulnerabilities identified in previous iterations.
3. **ADD CONCRETE IMPLEMENTATION DEPTH**: Inject exact system schemas, API routes, data models, failure recovery algorithms, unit economics, or deployment phases.
4. **UPDATE COMPREHENSIVE BLUEPRINT**: Deliver your updated, hardened version in `current_best_answer`.
5. **SPEECH BALLOON SUMMARY**: Provide a punchy 2-3 sentence statement (~25-35 words) explaining the concrete breakthrough or remedy you just contributed.

Respond strictly in JSON matching the required schema."""


def get_master_plan_synthesis_prompt(
    objective: str,
    turns: List[TurnRecord],
) -> str:
    """
    Prompts the synthesizer to compile the finalized Master Blueprint document.
    """
    contributions = []
    for t in turns:
        resp = t.response
        contributions.append(
            f"--- [{t.debater_name} ({t.model_name}) | Iteration {t.round_num}] ---\n"
            f"Summary: {resp.speech_bubble_summary}\n"
            f"Contributions: {resp.current_best_answer}\n"
            f"Vulnerabilities Solved: {', '.join(getattr(resp, 'vulnerabilities_identified', []))}\n"
            f"Enhancements: {', '.join(getattr(resp, 'proposed_enhancements', []))}\n"
        )
    contributions_str = "\n".join(contributions)

    return f"""You are the Master Blueprint Compiler for the AI Mastermind.
Your task is to synthesize all collaborative iterations into a finalized, executive-grade **Master Blueprint Document**.

### User Objective:
"{objective}"

### Collaborative Brainstorming Trajectory:
{contributions_str}

### Required Markdown Blueprint Format:
Construct a polished, comprehensive, and high-value Markdown document structured as follows:

# 🚀 Master Blueprint: [Title based on Objective]

## 📌 Executive Summary
Brief high-impact synthesis of the core breakthrough strategy and unique value proposition.

## 🏗️ System Architecture & Core Strategy
Comprehensive breakdown of workflows, tech stack/methodology, components, and primary mechanisms.

### 📐 Visual Architecture Flowchart
Provide a clean, valid Mermaid.js flowchart visualizing the end-to-end workflow:
```mermaid
graph TD
    A[Input / Trigger] --> B[Core Engine / Pipeline]
    B --> C[Stress-Testing & Verification Gateway]
    C --> D[Execution & Output Layer]
```

## 🛡️ Risk & Vulnerability Mitigation Matrix
Table of critical edge cases/risks identified during stress-testing and their concrete solutions.

| Risk / Bottleneck | Impact Severity | Concrete Mitigation Strategy |
|---|---|---|
| ... | High / Critical | ... |

## 📅 Phased Execution Roadmap
Actionable step-by-step phases (Phase 1: Foundation/MVP, Phase 2: Scale, Phase 3: Optimization).

## 🎯 Key Success Metrics & KPIs
Target quantitative and qualitative indicators of success.
"""
