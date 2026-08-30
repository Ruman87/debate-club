"""
Real-Time Web Search & Grounding Engine (RAG) for Debate-Club.
Retrieves live citations, empirical statistics, and facts from the web
to ground debater turns and prevent hallucinations.
"""

import os
import json
import logging
import urllib.request
import urllib.parse
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


def search_web_grounding(query: str, max_results: int = 3) -> List[Dict[str, str]]:
    """
    Performs a real-time web search for empirical grounding facts.
    Supports Serper API, Tavily API, or DuckDuckGo instant API with safe fallback.
    """
    if not query or not query.strip():
        return []

    clean_query = query.strip()
    
    # 1. Check for Serper API Key
    serper_key = os.getenv("SERPER_API_KEY")
    if serper_key:
        try:
            url = "https://google.serper.dev/search"
            payload = json.dumps({"q": clean_query, "num": max_results}).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=payload,
                headers={"X-API-KEY": serper_key, "Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=4) as response:
                data = json.loads(response.read().decode("utf-8"))
                results = []
                for item in data.get("organic", [])[:max_results]:
                    results.append({
                        "title": item.get("title", ""),
                        "snippet": item.get("snippet", ""),
                        "link": item.get("link", "")
                    })
                if results:
                    return results
        except Exception as e:
            logger.warning(f"Serper search failed: {e}")

    # 2. Check for Tavily API Key
    tavily_key = os.getenv("TAVILY_API_KEY")
    if tavily_key:
        try:
            url = "https://api.tavily.com/search"
            payload = json.dumps({"query": clean_query, "max_results": max_results, "api_key": tavily_key}).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=4) as response:
                data = json.loads(response.read().decode("utf-8"))
                results = []
                for item in data.get("results", [])[:max_results]:
                    results.append({
                        "title": item.get("title", ""),
                        "snippet": item.get("content", ""),
                        "link": item.get("url", "")
                    })
                if results:
                    return results
        except Exception as e:
            logger.warning(f"Tavily search failed: {e}")

    # 3. DuckDuckGo Instant Search API (Free, no key required)
    try:
        encoded = urllib.parse.quote_plus(clean_query)
        ddg_url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1&skip_disambig=1"
        req = urllib.request.Request(ddg_url, headers={"User-Agent": "DebateClub-GroundingEngine/2.0"})
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode("utf-8"))
            results = []
            if data.get("AbstractText"):
                results.append({
                    "title": data.get("Heading", clean_query),
                    "snippet": data.get("AbstractText", ""),
                    "link": data.get("AbstractURL", "https://duckduckgo.com")
                })
            for topic in data.get("RelatedTopics", [])[:max_results - len(results)]:
                if isinstance(topic, dict) and topic.get("Text"):
                    results.append({
                        "title": topic.get("FirstURL", "").split("/")[-1].replace("_", " ") or "Context Source",
                        "snippet": topic.get("Text", ""),
                        "link": topic.get("FirstURL", "")
                    })
            if results:
                return results
    except Exception as e:
        logger.debug(f"DuckDuckGo API call: {e}")

    return []


def format_grounding_context(results: List[Dict[str, str]]) -> str:
    """
    Formats search results into a clean prompt section for debaters.
    """
    if not results:
        return ""

    lines = ["### 🌐 Live Grounding & Empirical Citations (Web Search):"]
    for idx, r in enumerate(results, 1):
        lines.append(f"{idx}. **{r['title']}**: \"{r['snippet']}\" [Source: {r.get('link', 'Web')}]")
    return "\n".join(lines)
