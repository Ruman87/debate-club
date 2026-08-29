"""
Dynamic Stance and Complexity Analyzer for Debate-Club.
Evaluates debate topic complexity to determine whether 2 or 3 debaters are optimal,
and assigns bespoke non-polar positions for each debater.
"""

import logging
import json
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def assess_topic_complexity(question: str) -> int:
    """
    Evaluates whether a debate topic is best suited for 2 debaters (binary proposition)
    or 3 debaters (multi-faceted / nuanced / synthesis-demanding topic).
    """
    q_lower = question.lower().strip()
    
    # Binary / yes-no keywords with simple polarity
    simple_binary_cues = [
        "is it better to", "which is better", "should i choose a or b",
        "vim or emacs", "tabs or spaces", "react or vue", "python or rust"
    ]
    for cue in simple_binary_cues:
        if cue in q_lower:
            return 2

    # Nuanced relationship, ethics, policy, technology, philosophy topics
    # Benefit substantially from triangulation and a middle ground
    return 3


def generate_assigned_stances(
    question: str,
    num_debaters: int = 3,
    generator_model: Optional[str] = None,
) -> Dict[str, Dict[str, str]]:
    """
    Generates distinct assigned stances for Alex (FOR), Charlie (AGAINST), and Shahar (MIDDLE GROUND).
    Uses curated domain heuristics or dynamic LLM synthesis when appropriate.
    """
    q_lower = question.lower().strip()
    
    # Custom high-quality heuristics for common debate topics
    if "girlfriend" in q_lower or "break up" in q_lower or "crazy" in q_lower:
        stances = {
            "Alex": {
                "stance_type": "for",
                "label": "FOR (Affirmative)",
                "mandate": "Argue firmly in favor of breaking up. Emphasize personal boundaries, self-preservation, the emotional toll of dealing with irrational/toxic behavior, and the risk of prolonging an unhealthy dynamic.",
            },
            "Charlie": {
                "stance_type": "against",
                "label": "AGAINST (Negative)",
                "mandate": "Argue against breaking up hastily. Advocate for emotional maturity, empathy, open communication, identifying underlying mental health or stress factors, and avoiding labeling a partner without honest dialogue.",
            },
        }
        if num_debaters >= 3:
            stances["Shahar"] = {
                "stance_type": "middle_ground",
                "label": "MIDDLE GROUND (Synthesis)",
                "mandate": "Argue for a structured middle ground: establish clear conditional boundaries, propose relationship therapy or honest mediation, and set a defined timeline to evaluate change before making a final decision.",
            }
        return stances

    elif "agi" in q_lower or "existential risk" in q_lower or ("ai" in q_lower and ("risk" in q_lower or "danger" in q_lower or "threat" in q_lower)):
        stances = {
            "Alex": {
                "stance_type": "for",
                "label": "FOR (Urgent Safety Containment)",
                "mandate": "Argue that advanced AI presents severe existential and systemic risks requiring strict compute thresholds, proactive safety containment, and alignment audits before deployment.",
            },
            "Charlie": {
                "stance_type": "against",
                "label": "AGAINST (Open Acceleration)",
                "mandate": "Argue that AI risk is overblown or best solved through open-source competition, decentralized innovation, and iterative engineering rather than restrictive central bottlenecks.",
            },
        }
        if num_debaters >= 3:
            stances["Shahar"] = {
                "stance_type": "middle_ground",
                "label": "MIDDLE GROUND (Pragmatic Governance)",
                "mandate": "Argue for a tiered regulatory sandbox: strict compute governance for frontier models while keeping standard open-source research unrestricted.",
            }
        return stances

    elif "nuclear" in q_lower:
        stances = {
            "Alex": {
                "stance_type": "for",
                "label": "FOR (Nuclear Renaissance)",
                "mandate": "Argue that nuclear energy is the most reliable, clean, high-density baseload power essential for deep decarbonization and grid stability.",
            },
            "Charlie": {
                "stance_type": "against",
                "label": "AGAINST (Renewables & Storage First)",
                "mandate": "Argue against massive nuclear buildout due to extreme capital costs, multi-decade construction delays, waste liabilities, and the faster deployment curve of solar, wind, and batteries.",
            },
        }
        if num_debaters >= 3:
            stances["Shahar"] = {
                "stance_type": "middle_ground",
                "label": "MIDDLE GROUND (Hybrid Strategy)",
                "mandate": "Argue for extending existing safe reactor lifespans and funding modular micro-reactors (SMRs) while prioritizing rapid solar and wind deployment in the short term.",
            }
        return stances

    # Generalized high-impact stance formulation
    stances = {
        "Alex": {
            "stance_type": "for",
            "label": "FOR (Affirmative Proposition)",
            "mandate": f"Argue in the affirmative (PRO) for '{question}'. Build a compelling case with step-by-step causal warrants highlighting key systemic benefits, moral imperative, and the necessity of action.",
        },
        "Charlie": {
            "stance_type": "against",
            "label": "AGAINST (Negative Proposition)",
            "mandate": f"Argue firmly against the proposition (CON) for '{question}'. Expose unintended consequences, second-order economic/operational harms, and execute link turns demonstrating superior alternatives.",
        },
    }
    if num_debaters >= 3:
        stances["Shahar"] = {
            "stance_type": "middle_ground",
            "label": "MIDDLE GROUND (Third Way / Synthesis)",
            "mandate": f"Argue for a nuanced third-way middle ground on '{question}'. Harmonize valid concerns from both sides into an actionable, conditional policy framework with structured trade-off balancing.",
        }

    return stances
