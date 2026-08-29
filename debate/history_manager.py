"""
Session History Manager for Debate-Club.
Persists completed debate tournaments and mastermind blueprints to local disk,
allowing users to archive, browse, and re-load past sessions.
"""

import os
import re
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from models.debate_state import DebateState

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSIONS_DIR = os.path.join(BASE_DIR, ".sessions")


def _ensure_dir():
    if not os.path.exists(SESSIONS_DIR):
        os.makedirs(SESSIONS_DIR, exist_ok=True)


def _sanitize_filename(text: str, max_len: int = 35) -> str:
    clean = re.sub(r"[^\w\s-]", "", text).strip().replace(" ", "_")
    return clean[:max_len]


def save_session(state: DebateState) -> Optional[str]:
    """
    Saves a completed debate or mastermind plan state to disk.
    """
    try:
        _ensure_dir()
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = _sanitize_filename(state.question)
        filename = f"{state.app_mode}_{ts}_{slug}.json"
        filepath = os.path.join(SESSIONS_DIR, filename)

        data = state.model_dump()
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, default=str, indent=2)

        logger.info(f"Saved session to {filepath}")
        return filename
    except Exception as e:
        logger.error(f"Failed to save session history: {e}")
        return None


def list_saved_sessions() -> List[Dict[str, Any]]:
    """
    Returns metadata list of all saved sessions sorted by newest first.
    """
    _ensure_dir()
    sessions = []
    try:
        for f in os.listdir(SESSIONS_DIR):
            if not f.endswith(".json"):
                continue
            filepath = os.path.join(SESSIONS_DIR, f)
            try:
                with open(filepath, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    sessions.append({
                        "file_id": f,
                        "app_mode": data.get("app_mode", "debate"),
                        "question": data.get("question", "Untitled"),
                        "turns_count": len(data.get("turns", [])),
                        "grand_winner": data.get("grand_winner"),
                        "has_master_plan": bool(data.get("master_plan")),
                        "created_at": os.path.getmtime(filepath),
                    })
            except Exception:
                continue
    except Exception as e:
        logger.error(f"Failed to list saved sessions: {e}")

    # Sort newest first
    sessions.sort(key=lambda x: x["created_at"], reverse=True)
    return sessions


def load_session(file_id: str) -> Optional[DebateState]:
    """
    Loads a saved DebateState by file_id.
    """
    _ensure_dir()
    filepath = os.path.join(SESSIONS_DIR, file_id)
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return DebateState(**data)
    except Exception as e:
        logger.error(f"Failed to load session {file_id}: {e}")
        return None


def delete_session(file_id: str) -> bool:
    """
    Deletes a saved session from disk.
    """
    _ensure_dir()
    filepath = os.path.join(SESSIONS_DIR, file_id)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            return True
        except Exception as e:
            logger.error(f"Failed to delete session {file_id}: {e}")
            return False
    return False
