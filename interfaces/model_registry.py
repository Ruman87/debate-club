"""
Model Registry & Availability Checker for Debate-Club.
Categorizes models into Cloud API, Local Machine (Ollama), and Built-in Simulation.
Provides live status detection for API keys and local Ollama instance.
"""

import os
import json
import urllib.request
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv

load_dotenv(override=True)


class ModelCategory(str, Enum):
    CLOUD_API = "cloud_api"
    LOCAL_MACHINE = "local_machine"
    SIMULATION = "simulation"


@dataclass
class ModelInfo:
    id: str
    name: str
    category: ModelCategory
    provider: str
    env_var: Optional[str]
    is_available: bool
    status_text: str
    description: str


# Mapping of Cloud API Providers to their required environment variables
API_PROVIDER_ENV_VARS = {
    "OpenAI": "OPENAI_API_KEY",
    "Anthropic": "ANTHROPIC_API_KEY",
    "Google Gemini": "GOOGLE_API_KEY",
    "xAI Grok": "GROK_API_KEY",
    "Groq": "GROQ_API_KEY",
}

# Standard catalog of models
STANDARD_MODEL_CATALOG = [
    # --- Machine-based (Local Ollama) ---
    {"id": "ollama/llama3.2:latest", "provider": "Ollama (Local)", "category": ModelCategory.LOCAL_MACHINE, "env_var": None},
    {"id": "ollama/deepseek-r1:1.5b", "provider": "Ollama (Local)", "category": ModelCategory.LOCAL_MACHINE, "env_var": None},
    {"id": "ollama/gpt-oss:latest", "provider": "Ollama (Local)", "category": ModelCategory.LOCAL_MACHINE, "env_var": None},
    {"id": "ollama/gemma3:270m", "provider": "Ollama (Local)", "category": ModelCategory.LOCAL_MACHINE, "env_var": None},
    {"id": "ollama/llama3", "provider": "Ollama (Local)", "category": ModelCategory.LOCAL_MACHINE, "env_var": None},
    {"id": "ollama/mistral", "provider": "Ollama (Local)", "category": ModelCategory.LOCAL_MACHINE, "env_var": None},
    {"id": "ollama/qwen2.5", "provider": "Ollama (Local)", "category": ModelCategory.LOCAL_MACHINE, "env_var": None},

    # --- Built-in Simulation (Zero config / Free) ---
    {"id": "mock-debater-alpha", "provider": "Simulator", "category": ModelCategory.SIMULATION, "env_var": None},
    {"id": "mock-debater-beta", "provider": "Simulator", "category": ModelCategory.SIMULATION, "env_var": None},

    # --- Cloud API: OpenAI ---
    {"id": "gpt-4o", "provider": "OpenAI", "category": ModelCategory.CLOUD_API, "env_var": "OPENAI_API_KEY"},
    {"id": "gpt-4o-mini", "provider": "OpenAI", "category": ModelCategory.CLOUD_API, "env_var": "OPENAI_API_KEY"},
    {"id": "gpt-5", "provider": "OpenAI", "category": ModelCategory.CLOUD_API, "env_var": "OPENAI_API_KEY"},
    {"id": "gpt-5-mini", "provider": "OpenAI", "category": ModelCategory.CLOUD_API, "env_var": "OPENAI_API_KEY"},
    {"id": "o1", "provider": "OpenAI", "category": ModelCategory.CLOUD_API, "env_var": "OPENAI_API_KEY"},
    {"id": "o3-mini", "provider": "OpenAI", "category": ModelCategory.CLOUD_API, "env_var": "OPENAI_API_KEY"},

    # --- Cloud API: Anthropic ---
    {"id": "claude-3-5-sonnet-latest", "provider": "Anthropic", "category": ModelCategory.CLOUD_API, "env_var": "ANTHROPIC_API_KEY"},
    {"id": "claude-3-5-haiku-latest", "provider": "Anthropic", "category": ModelCategory.CLOUD_API, "env_var": "ANTHROPIC_API_KEY"},
    {"id": "claude-3-opus-latest", "provider": "Anthropic", "category": ModelCategory.CLOUD_API, "env_var": "ANTHROPIC_API_KEY"},
    {"id": "claude-sonnet-4-5", "provider": "Anthropic", "category": ModelCategory.CLOUD_API, "env_var": "ANTHROPIC_API_KEY"},
    {"id": "claude-haiku-4-5", "provider": "Anthropic", "category": ModelCategory.CLOUD_API, "env_var": "ANTHROPIC_API_KEY"},

    # --- Cloud API: Google Gemini ---
    {"id": "gemini-3.6-flash", "provider": "Google Gemini", "category": ModelCategory.CLOUD_API, "env_var": "GOOGLE_API_KEY"},
    {"id": "gemini-3.7-flash", "provider": "Google Gemini", "category": ModelCategory.CLOUD_API, "env_var": "GOOGLE_API_KEY"},
    {"id": "gemini-flash-latest", "provider": "Google Gemini", "category": ModelCategory.CLOUD_API, "env_var": "GOOGLE_API_KEY"},
    {"id": "gemini-pro-latest", "provider": "Google Gemini", "category": ModelCategory.CLOUD_API, "env_var": "GOOGLE_API_KEY"},
    {"id": "gemini-2.5-flash-lite", "provider": "Google Gemini", "category": ModelCategory.CLOUD_API, "env_var": "GOOGLE_API_KEY"},
    {"id": "gemini-2.5-pro", "provider": "Google Gemini", "category": ModelCategory.CLOUD_API, "env_var": "GOOGLE_API_KEY"},

    # --- Cloud API: xAI Grok ---
    {"id": "grok-2", "provider": "xAI Grok", "category": ModelCategory.CLOUD_API, "env_var": "GROK_API_KEY"},
    {"id": "grok-2-mini", "provider": "xAI Grok", "category": ModelCategory.CLOUD_API, "env_var": "GROK_API_KEY"},
    {"id": "grok-4", "provider": "xAI Grok", "category": ModelCategory.CLOUD_API, "env_var": "GROK_API_KEY"},
    {"id": "grok-4-fast", "provider": "xAI Grok", "category": ModelCategory.CLOUD_API, "env_var": "GROK_API_KEY"},

    # --- Cloud API: Groq ---
    {"id": "llama-3.3-70b-versatile", "provider": "Groq", "category": ModelCategory.CLOUD_API, "env_var": "GROQ_API_KEY"},
    {"id": "llama-3.1-8b-instant", "provider": "Groq", "category": ModelCategory.CLOUD_API, "env_var": "GROQ_API_KEY"},
    {"id": "mixtral-8x7b-32768", "provider": "Groq", "category": ModelCategory.CLOUD_API, "env_var": "GROQ_API_KEY"},
    {"id": "openai/gpt-oss-120b", "provider": "Groq", "category": ModelCategory.CLOUD_API, "env_var": "GROQ_API_KEY"},
]


def check_ollama_status(base_url: str = "http://localhost:11434") -> Tuple[bool, List[str]]:
    """
    Checks if the local Ollama server is running and fetches the list of locally installed models.
    """
    try:
        req = urllib.request.Request(f"{base_url}/api/tags", headers={"User-Agent": "DebateClub"})
        with urllib.request.urlopen(req, timeout=0.8) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                models = [m["name"] for m in data.get("models", [])]
                return True, models
    except Exception:
        pass
    return False, []


def get_all_models_with_status() -> List[ModelInfo]:
    """
    Returns a comprehensive list of all models with their live availability status.
    Dynamically includes locally installed Ollama models at the top of local models.
    """
    load_dotenv(override=True)
    ollama_running, local_ollama_models = check_ollama_status()
    
    # Track models to avoid duplicates
    seen_ids = set()
    model_infos: List[ModelInfo] = []

    # 1. First add dynamically detected Ollama models if any
    for local_m in local_ollama_models:
        full_id = f"ollama/{local_m}" if not local_m.startswith("ollama/") else local_m
        if full_id not in seen_ids:
            seen_ids.add(full_id)
            model_infos.append(
                ModelInfo(
                    id=full_id,
                    name=local_m,
                    category=ModelCategory.LOCAL_MACHINE,
                    provider="Ollama (Local)",
                    env_var=None,
                    is_available=True,
                    status_text="🟢 Running on Mac",
                    description="Runs 100% locally on your machine via Ollama (free, private, no API key).",
                )
            )

    # 2. Add standard catalog models
    for entry in STANDARD_MODEL_CATALOG:
        m_id = entry["id"]
        if m_id in seen_ids:
            continue
        seen_ids.add(m_id)

        cat = entry["category"]
        prov = entry["provider"]
        env_var = entry["env_var"]

        if cat == ModelCategory.LOCAL_MACHINE:
            clean_name = m_id.replace("ollama/", "")
            is_installed = (
                clean_name in local_ollama_models
                or f"{clean_name}:latest" in local_ollama_models
                or any(m.startswith(f"{clean_name}:") for m in local_ollama_models)
            )
            if not ollama_running:
                is_avail = False
                status = "⚪ Offline (Start Ollama)"
                desc = "Machine-based model. Start Ollama locally ('ollama serve') to activate."
            elif not is_installed:
                is_avail = False
                status = f"⚪ Not Downloaded (Run 'ollama pull {clean_name}')"
                desc = f"Model '{clean_name}' is not downloaded on your Mac. Run 'ollama pull {clean_name}' in your terminal to install it."
            else:
                is_avail = True
                status = "🟢 Ready on Mac"
                desc = f"Runs 100% locally on your machine via Ollama (free, private, no API key)."
        elif cat == ModelCategory.SIMULATION:
            is_avail = True
            status = "🟢 Ready (Built-in)"
            desc = "Built-in offline simulator for rapid testing without API keys."
        else:  # CLOUD_API
            has_key = bool(os.getenv(env_var)) if env_var else False
            is_avail = has_key
            status = f"🟢 Connected" if has_key else f"⚠️ Missing {env_var}"
            desc = (
                f"Cloud API model provided by {prov}. Connected via {env_var}."
                if has_key
                else f"Cloud API model provided by {prov}. Requires {env_var} in .env to use."
            )

        model_infos.append(
            ModelInfo(
                id=m_id,
                name=m_id,
                category=cat,
                provider=prov,
                env_var=env_var,
                is_available=is_avail,
                status_text=status,
                description=desc,
            )
        )

    return model_infos


def get_model_info_map() -> Dict[str, ModelInfo]:
    """Returns a dict mapping model ID to its ModelInfo."""
    models = get_all_models_with_status()
    return {m.id: m for m in models}


def format_model_dropdown_label(model_id: str, model_info_map: Optional[Dict[str, ModelInfo]] = None) -> str:
    """
    Formats the label displayed in the Streamlit selectbox options.
    Clearly emphasizes API vs Local Machine vs Simulator, and indicates if API key is missing or model not downloaded.
    """
    if model_info_map is None:
        model_info_map = get_model_info_map()

    info = model_info_map.get(model_id)
    if not info:
        # Fallback if unknown model
        return model_id

    if info.category == ModelCategory.CLOUD_API:
        if info.is_available:
            return f"☁️ [API] {info.id} (🟢 Ready)"
        else:
            return f"☁️ [API] {info.id} (⚠️ No API Key)"
    elif info.category == ModelCategory.LOCAL_MACHINE:
        if info.is_available:
            return f"💻 [Local] {info.id} (🟢 Ready on Mac)"
        elif "Offline" in info.status_text:
            return f"💻 [Local] {info.id} (⚪ Offline - Start Ollama)"
        else:
            return f"💻 [Local] {info.id} (⚪ Not Downloaded)"
    elif info.category == ModelCategory.SIMULATION:
        return f"🧪 [Simulator] {info.id} (🟢 Free / Offline)"

    return info.id

    return info.id


def get_recommended_default_indices(model_ids: List[str], model_info_map: Dict[str, ModelInfo]) -> Tuple[int, int, int]:
    """
    Finds the best default indices for Debater 1, Debater 2, and Debater 3.
    Prefers available/ready models (e.g. Local Ollama or Simulator if API keys are missing).
    """
    available_indices = [i for i, mid in enumerate(model_ids) if model_info_map.get(mid, None) and model_info_map[mid].is_available]
    
    if len(available_indices) >= 3:
        return available_indices[0], available_indices[1], available_indices[2]
    elif len(available_indices) == 2:
        return available_indices[0], available_indices[1], available_indices[0]
    elif len(available_indices) == 1:
        return available_indices[0], available_indices[0], available_indices[0]
    
    # Fallback to standard indices
    return 0, min(1, len(model_ids) - 1), min(2, len(model_ids) - 1)


def get_providers_status_summary() -> List[Dict[str, Any]]:
    """
    Returns high-level status of all cloud providers and local machine Ollama.
    """
    load_dotenv(override=True)
    ollama_running, local_models = check_ollama_status()
    
    summary = []
    # Local Machine
    summary.append({
        "provider": "💻 Local Machine (Ollama)",
        "type": "Local",
        "is_active": ollama_running,
        "detail": f"{len(local_models)} model{'s' if len(local_models) != 1 else ''} loaded on Mac" if ollama_running else "Offline (run 'ollama serve')",
        "env_var": None,
    })

    # Cloud Providers
    for prov_name, env_var in API_PROVIDER_ENV_VARS.items():
        is_set = bool(os.getenv(env_var))
        summary.append({
            "provider": f"☁️ {prov_name}",
            "type": "Cloud API",
            "is_active": is_set,
            "detail": f"Active ({env_var})" if is_set else f"Missing {env_var}",
            "env_var": env_var,
        })

    # Simulator
    summary.append({
        "provider": "🧪 Built-in Simulator",
        "type": "Simulation",
        "is_active": True,
        "detail": "Always ready (built-in offline mock)",
        "env_var": None,
    })

    return summary
