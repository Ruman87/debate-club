"""
Unified LLM Interface Layer for Debate-Club.
Supports OpenAI, Anthropic, Google Gemini, Groq, xAI Grok, Ollama (Local), and Mock/Simulator.
"""

import os
import re
import json
import time
import functools
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type, Optional
from dotenv import load_dotenv

load_dotenv(override=True)

logger = logging.getLogger(__name__)

# Base API URLs
ANTHROPIC_BASE_URL = "https://api.anthropic.com/v1/"
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
GROK_BASE_URL = "https://api.x.ai/v1"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
OLLAMA_BASE_URL = "http://localhost:11434/v1"


def with_retry(max_retries: int = 3, initial_delay: float = 1.0, backoff_factor: float = 2.0):
    """
    Decorator for robust LLM API calls with exponential backoff and rate-limit recovery.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_err = None
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_err = e
                    err_str = str(e).lower()
                    # Do not retry configuration / missing API key errors
                    if "is not configured in .env" in str(e) or "missing_key" in err_str or "not installed on your machine" in str(e):
                        raise e
                    logger.warning(
                        f"LLM call attempt {attempt}/{max_retries} encountered transient error: {e}. Retrying in {delay:.1f}s..."
                    )
                    if attempt < max_retries:
                        time.sleep(delay)
                        delay *= backoff_factor
            raise last_err
        return wrapper
    return decorator


def extract_json_from_text(text: str) -> Dict[str, Any]:
    """
    Ultra-robust JSON extractor and auto-repairer from LLM responses
    (handles DeepSeek/Qwen <think> tags, markdown wrappers, trailing commas, partial outputs).
    """
    if not text:
        return {}

    cleaned = text.strip()
    
    # 1. Strip DeepSeek / Qwen reasoning tags (<think>...</think>)
    cleaned = re.sub(r"<think>.*?</think>", "", cleaned, flags=re.DOTALL | re.IGNORECASE).strip()
    if "<think>" in cleaned.lower() and "</think>" not in cleaned.lower():
        cleaned = re.sub(r"<think>.*", "", cleaned, flags=re.DOTALL | re.IGNORECASE).strip()

    # 2. Strip Markdown code blocks
    if "```json" in cleaned:
        cleaned = cleaned.split("```json", 1)[1].split("```", 1)[0].strip()
    elif "```" in cleaned:
        cleaned = cleaned.split("```", 1)[1].split("```", 1)[0].strip()

    # 3. Find outer braces
    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        cleaned = cleaned[first_brace : last_brace + 1]
    elif first_brace != -1:
        cleaned = cleaned[first_brace:] + "}"

    # Try standard json loads
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 4. Attempt syntax repairs
    repaired = re.sub(r',\s*([\}\]])', r'\1', cleaned)

    try:
        return json.loads(repaired)
    except json.JSONDecodeError:
        pass

    # 5. Regex-based key-value field extractor for structured schemas
    extracted: Dict[str, Any] = {}
    
    string_keys = [
        "current_best_answer",
        "speech_bubble_summary",
        "inner_reasoning",
        "critique_or_rebuttal",
        "alliance_target",
        "alliance_pitch",
        "judge_commentary",
        "dredd_quote",
        "round_winner",
        "strongest_argument",
        "weakest_point",
        "summary_verdict",
        "grand_winner",
        "verdict_reasoning",
    ]
    
    for key in string_keys:
        pattern = rf'"{key}"\s*:\s*"((?:[^"\\]|\\.)*)"'
        match = re.search(pattern, cleaned, flags=re.DOTALL)
        if match:
            extracted[key] = match.group(1).replace('\\"', '"').replace('\\n', '\n').strip()
        else:
            pattern_unclosed = rf'"{key}"\s*:\s*"([^"\n\r]*)'
            match_unclosed = re.search(pattern_unclosed, cleaned)
            if match_unclosed:
                extracted[key] = match_unclosed.group(1).strip()

    num_keys = ["agreement_score", "logic_score", "rebuttal_score", "rhetoric_score", "round_num"]
    for key in num_keys:
        match = re.search(rf'"{key}"\s*:\s*(\d+)', cleaned)
        if match:
            try:
                extracted[key] = int(match.group(1))
            except ValueError:
                pass

    bool_keys = ["is_consensus_reached", "is_active"]
    for key in bool_keys:
        match = re.search(rf'"{key}"\s*:\s*(true|false)', cleaned, flags=re.IGNORECASE)
        if match:
            extracted[key] = match.group(1).lower() == "true"

    if extracted and ("current_best_answer" in extracted or "speech_bubble_summary" in extracted or "judge_commentary" in extracted or "dredd_quote" in extracted):
        return extracted

    raise ValueError(f"Could not parse valid JSON from model output: {cleaned[:100]}...")


class LLM(ABC):
    """
    Abstract Base Class for LLM providers.
    """

    model_names: List[str] = []
    model_name: str
    temperature: float
    client: Any

    def __init__(self, model_name: str, temperature: float = 0.7):
        self.model_name = model_name
        self.temperature = temperature
        self.setup_client()

    @abstractmethod
    def setup_client(self):
        """Initialize provider client with API keys."""
        pass

    @abstractmethod
    def send(self, system_prompt: str, user_prompt: str, max_tokens: int = 1500) -> str:
        """
        Send a conversation prompt to the LLM and return raw response string.
        """
        pass

    @classmethod
    def model_map(cls) -> Dict[str, Type["LLM"]]:
        """
        Dynamically map all model names supported by all registered subclasses.
        """
        mapping = {}
        for subclass in cls.__subclasses__():
            for name in subclass.model_names:
                mapping[name] = subclass
        return mapping

    @classmethod
    def for_model_name(cls, model_name: str, temperature: float = 0.7) -> "LLM":
        """
        Factory method to instantiate the appropriate LLM subclass.
        """
        mapping = cls.model_map()
        if model_name in mapping:
            return mapping[model_name](model_name, temperature)
        
        # Fallback: if model starts with gpt, claude, gemini, etc.
        if model_name.startswith("gpt") or model_name.startswith("o1") or model_name.startswith("o3"):
            return GPT(model_name, temperature)
        elif model_name.startswith("claude"):
            return Claude(model_name, temperature)
        elif model_name.startswith("gemini"):
            return Gemini(model_name, temperature)
        elif model_name.startswith("grok"):
            return Grok(model_name, temperature)
        elif "ollama" in model_name.lower():
            return Ollama(model_name, temperature)
        else:
            return MockLLM(model_name, temperature)

    @classmethod
    def all_model_names(cls) -> List[str]:
        try:
            from interfaces.model_registry import get_all_models_with_status
            return [m.id for m in get_all_models_with_status()]
        except Exception:
            return list(cls.model_map().keys())


class GPT(LLM):
    model_names = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-5",
        "gpt-5-mini",
        "o1",
        "o3-mini",
    ]

    def setup_client(self):
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key or "missing_key")

    @with_retry(max_retries=3, initial_delay=1.0)
    def send(self, system_prompt: str, user_prompt: str, max_tokens: int = 1500) -> str:
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError(f"OPENAI_API_KEY is not configured in .env for model '{self.model_name}'.")
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        kwargs: Dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
            "response_format": {"type": "json_object"},
        }
        if not (self.model_name.startswith("o1") or self.model_name.startswith("o3")):
            kwargs["temperature"] = self.temperature
            kwargs["max_tokens"] = max_tokens
        
        completion = self.client.chat.completions.create(**kwargs)
        return completion.choices[0].message.content or "{}"


class Claude(LLM):
    model_names = [
        "claude-3-5-sonnet-latest",
        "claude-3-5-haiku-latest",
        "claude-3-opus-latest",
        "claude-sonnet-4-5",
        "claude-haiku-4-5",
    ]

    def setup_client(self):
        import anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=api_key or "missing_key")

    @with_retry(max_retries=3, initial_delay=1.0)
    def send(self, system_prompt: str, user_prompt: str, max_tokens: int = 1500) -> str:
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise ValueError(f"ANTHROPIC_API_KEY is not configured in .env for model '{self.model_name}'.")
        message = self.client.messages.create(
            model=self.model_name,
            max_tokens=max_tokens,
            temperature=self.temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return message.content[0].text


class Gemini(LLM):
    model_names = [
        "gemini-3.6-flash",
        "gemini-3.7-flash",
        "gemini-flash-latest",
        "gemini-pro-latest",
        "gemini-2.5-flash-lite",
        "gemini-2.5-pro",
    ]

    def setup_client(self):
        from openai import OpenAI
        api_key = os.getenv("GOOGLE_API_KEY")
        self.client = OpenAI(
            api_key=api_key or "missing_key",
            base_url=GEMINI_BASE_URL,
        )

    @with_retry(max_retries=3, initial_delay=1.0)
    def send(self, system_prompt: str, user_prompt: str, max_tokens: int = 1500) -> str:
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError(f"GOOGLE_API_KEY is not configured in .env for model '{self.model_name}'.")
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.temperature,
            response_format={"type": "json_object"},
        )
        return completion.choices[0].message.content or "{}"


class Grok(LLM):
    model_names = [
        "grok-2",
        "grok-2-mini",
        "grok-4",
        "grok-4-fast",
    ]

    def setup_client(self):
        from openai import OpenAI
        api_key = os.getenv("GROK_API_KEY")
        self.client = OpenAI(
            api_key=api_key or "missing_key",
            base_url=GROK_BASE_URL,
        )

    @with_retry(max_retries=3, initial_delay=1.0)
    def send(self, system_prompt: str, user_prompt: str, max_tokens: int = 1500) -> str:
        if not os.getenv("GROK_API_KEY"):
            raise ValueError(f"GROK_API_KEY is not configured in .env for model '{self.model_name}'.")
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.temperature,
            response_format={"type": "json_object"},
        )
        return completion.choices[0].message.content or "{}"


class GroqAPI(LLM):
    model_names = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "openai/gpt-oss-120b",
    ]

    def setup_client(self):
        from groq import Groq
        api_key = os.getenv("GROK_API_KEY") or os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=api_key or "missing_key")

    @with_retry(max_retries=3, initial_delay=1.0)
    def send(self, system_prompt: str, user_prompt: str, max_tokens: int = 1500) -> str:
        if not (os.getenv("GROQ_API_KEY") or os.getenv("GROK_API_KEY")):
            raise ValueError(f"GROQ_API_KEY is not configured in .env for model '{self.model_name}'.")
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.temperature,
            response_format={"type": "json_object"},
        )
        return completion.choices[0].message.content or "{}"


class Ollama(LLM):
    model_names = [
        "ollama/llama3",
        "ollama/mistral",
        "ollama/qwen2.5",
    ]

    def setup_client(self):
        from openai import OpenAI
        self.client = OpenAI(
            base_url=os.getenv("OLLAMA_BASE_URL", OLLAMA_BASE_URL),
            api_key="ollama",
        )

    @with_retry(max_retries=3, initial_delay=1.0)
    def send(self, system_prompt: str, user_prompt: str, max_tokens: int = 1500) -> str:
        clean_model = self.model_name.replace("ollama/", "")
        try:
            completion = self.client.chat.completions.create(
                model=clean_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"},
            )
            return completion.choices[0].message.content or "{}"
        except Exception as e:
            if "not found" in str(e).lower() or "404" in str(e):
                raise RuntimeError(
                    f"Ollama model '{clean_model}' is not installed on your machine. "
                    f"Please run 'ollama pull {clean_model}' in your terminal or choose an installed model."
                ) from e
            raise e


class MockLLM(LLM):
    """
    Mock LLM for demonstration, offline testing, or simulation without live API keys.
    """
    model_names = [
        "mock-debater-alpha",
        "mock-debater-beta",
    ]

    def setup_client(self):
        pass

    def send(self, system_prompt: str, user_prompt: str, max_tokens: int = 1500) -> str:
        import random
        # Check if prompt is specifically for Master Blueprint compilation
        if "Master Blueprint Compiler" in system_prompt or "Master Blueprint Compiler" in user_prompt:
            return """# 🚀 Master Blueprint: Autonomous High-Value System Architecture

## 📌 Executive Summary
This blueprint establishes a state-of-the-art co-designed architecture combining an edge-first execution framework with adaptive risk controls and proactive developer toolchains.

## 🏗️ System Architecture & Core Strategy
1. **Core Ingestion & Context Layer**: Low-latency semantic streaming pipeline with real-time vector caching.
2. **Execution Engine**: Asynchronous dual-agent loop isolating high-throughput reasoning from runtime sandbox execution.
3. **Verification & Stress-Testing Gateway**: Automated AST analysis and regression safeguards.

## 🛡️ Risk & Vulnerability Mitigation Matrix

| Risk / Bottleneck | Impact Severity | Concrete Mitigation Strategy |
|---|---|---|
| Latency spikes under token saturation | High | Local speculative decoding and edge streaming caches |
| Hallucinated edge-case code execution | Critical | Strict sandbox containerization and deterministic lint verification |
| Cost scaling on frontier models | Medium | Dynamic model routing based on task complexity |

## 📅 Phased Execution Roadmap
- **Phase 1 (Weeks 1–4)**: Core MVP, foundational protocols, and baseline agent orchestration.
- **Phase 2 (Weeks 5–8)**: Red-team stress testing, automated benchmarks, and developer telemetry.
- **Phase 3 (Weeks 9–12)**: Production rollout, distributed edge nodes, and self-improving evaluation loops.

## 🎯 Key Success Metrics & KPIs
- Sub-200ms time-to-first-token on edge invocations.
- 99.4% syntax and verification test pass rate before execution.
- 40% reduction in token consumption via predictive context pruning.
"""

        # Check if this prompt is for the moderator
        if "Synthesize the definitive verdict" in user_prompt or "Chief Moderator" in user_prompt:
            moderator_response = {
                "summary_verdict": "After comprehensive deliberation across multiple rounds, both debaters reached convergence on a balanced, multi-tier strategy that combines theoretical rigor with practical empirical constraints.",
                "agreed_points": [
                    "Foundational trade-offs must be evaluated under real-world resource bounds",
                    "Iterative refinement and continuous stress-testing are necessary for robust solutions"
                ],
                "remaining_nuances": [
                    "Minor divergence remains regarding optimal weight allocation between edge-case mitigation and average-case performance"
                ],
                "final_consensus_score": 92,
                "conclusion_reason": "Consensus achieved through dialectic deliberation"
            }
            return json.dumps(moderator_response, indent=2)

        # Extract turn number from user_prompt if present
        turn_num = 1
        if "Turn 2" in user_prompt or "Round 2" in user_prompt:
            turn_num = 2
        elif "Turn 3" in user_prompt or "Round 3" in user_prompt:
            turn_num = 3
        elif "Turn 4" in user_prompt or "Round 4" in user_prompt:
            turn_num = 4

        agreement = min(40 + (turn_num * 20) + random.randint(-5, 10), 95)
        is_consensus = agreement >= 90

        sample_response = {
            "inner_reasoning": f"Analyzing the problem systematically. In round {turn_num}, we are bridging the remaining gaps and finding common ground.",
            "critique_or_rebuttal": f"While I appreciate the opponent's perspective, we must ensure edge cases and empirical constraints are prioritized.",
            "points_of_agreement": [
                "The core principles established in prior exchanges",
                "The necessity for practical trade-offs under resource constraints"
            ],
            "current_best_answer": f"Synthesized answer at iteration {turn_num}: A multi-faceted approach combining structural guarantees with empirical flexibility.",
            "agreement_score": agreement,
            "is_consensus_reached": is_consensus,
        }
        return json.dumps(sample_response, indent=2)

