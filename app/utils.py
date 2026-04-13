import json
from typing import Any, Dict, Optional


def strip_code_fence(text: str) -> str:
    cleaned = (text or "").strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if len(lines) >= 3:
            cleaned = "\n".join(lines[1:-1]).strip()
    return cleaned


def safe_json_loads(text: str) -> Dict[str, Any]:
    return json.loads(strip_code_fence(text))


def safe_parse(text: str) -> Optional[Dict[str, Any]]:
    try:
        return safe_json_loads(text)
    except Exception:
        return None
