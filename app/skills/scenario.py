import json
from typing import Dict

from app.llm import call_llm, safe_json_loads

SCENARIO_PROMPT = """
你是知识产权风控助手。
判断用户问题属于以下哪一类：
- 海外知识产权布局
- 海外侵权风险
- 海外并购IP风险

只输出JSON，格式：
{"scenario": "..."}

用户问题：{query}
""".strip()


def _rule_scenario(query: str) -> str:
    q = query.lower()
    if any(k in q for k in ["并购", "收购", "m&a", "acquisition"]):
        return "海外并购IP风险"
    if any(k in q for k in ["布局", "申请", "注册", "保护", "strategy"]):
        return "海外知识产权布局"
    return "海外侵权风险"


def detect_scenario(query: str) -> Dict[str, str]:
    prompt = SCENARIO_PROMPT.format(query=query)
    raw = call_llm(prompt)

    try:
        parsed = safe_json_loads(raw)
        scenario = parsed.get("scenario") or _rule_scenario(query)
    except Exception:
        scenario = _rule_scenario(query)

    if scenario not in {"海外知识产权布局", "海外侵权风险", "海外并购IP风险"}:
        scenario = _rule_scenario(query)

    return {"scenario": scenario}
