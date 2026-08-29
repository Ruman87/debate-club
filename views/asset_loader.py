"""
Asset Loader & Image Encoder Utility for Debate-Club.
Loads and caches local images as base64 data URIs for high-performance HTML/CSS embedding.
"""

import os
import base64
from functools import lru_cache
from typing import Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


@lru_cache(maxsize=16)
def get_image_base64_data_uri(image_relative_or_abs_path: str) -> Optional[str]:
    """
    Reads an image from disk and returns its base64 data URI string.
    """
    if not image_relative_or_abs_path:
        return None

    if os.path.isabs(image_relative_or_abs_path):
        filepath = image_relative_or_abs_path
    else:
        filepath = os.path.join(BASE_DIR, image_relative_or_abs_path)

    if not os.path.exists(filepath):
        # Check assets fallback
        fallback = os.path.join(ASSETS_DIR, os.path.basename(image_relative_or_abs_path))
        if os.path.exists(fallback):
            filepath = fallback
        else:
            return None

    ext = os.path.splitext(filepath)[1].lower().replace(".", "")
    if ext == "jpg":
        mime = "image/jpeg"
    elif ext == "png":
        mime = "image/png"
    elif ext == "webp":
        mime = "image/webp"
    else:
        mime = f"image/{ext}"

    try:
        with open(filepath, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            return f"data:{mime};base64,{encoded}"
    except Exception:
        return None


def get_character_avatar_uri(debater_name: str, fallback_path: Optional[str] = None) -> Optional[str]:
    """
    Returns data URI for a debater character by name (Alex, Charlie, Shahar/Sam).
    """
    name_lower = debater_name.lower()
    if "alex" in name_lower or "alpha" in name_lower:
        return get_image_base64_data_uri("assets/alex.jpg")
    elif "charlie" in name_lower or "beta" in name_lower:
        return get_image_base64_data_uri("assets/charlie.jpg")
    elif "shahar" in name_lower or "sam" in name_lower or "gamma" in name_lower:
        return get_image_base64_data_uri("assets/shahar.jpg")
    elif "dredd" in name_lower or "judge" in name_lower:
        return get_image_base64_data_uri("assets/judge_dredd.jpg")

    if fallback_path:
        return get_image_base64_data_uri(fallback_path)
    return None
