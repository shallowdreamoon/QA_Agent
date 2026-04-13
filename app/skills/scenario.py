from typing import Dict

from app.llm import LLMClientError, call_llm
from app.utils import safe_json_loads

PROMPT = """
你是知识产权场景分类器。
请将用户问题分类到以下三类之一：
1. 海外知识产权布局
2. 海外侵权风险
3. 海外并购IP风险

规则：
- 只输出 JSON
- 不要解释

输出格式：
{"scenario":""}

问题：{query}
""".strip()


VALID = {"海外知识产权布局", "海外侵权风险", "海外并购IP风险"}


def _rule_scenario(query: str) -> str:
    q = query.lower()
    if any(k in q for k in ["并购", "收购", "acquisition", "m&a"]):
        return "海外并购IP风险"
    if any(k in q for k in ["布局", "申请", "注册", "保护", "strategy"]):
        return "海外知识产权布局"
    return "海外侵权风险"


def detect_scenario(query: str) -> Dict[str, str]:
    prompt = PROMPT.replace("{query}", query)
    try:
        text = call_llm(prompt)
        data = safe_json_loads(text)
        scenario = data.get("scenario", "")
        if scenario in VALID:
            return {"scenario": scenario}
    except (LLMClientError, ValueError, TypeError, KeyError):
        pass

    return {"scenario": _rule_scenario(query)}
