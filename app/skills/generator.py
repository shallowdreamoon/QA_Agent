from typing import Any, Dict, List

from app.llm import LLMClientError, call_llm
from app.utils import safe_json_loads

PROMPT = """
你是知识产权风险分析助手。
请基于输入输出严格 JSON。

用户问题：{query}
抽取信息：{info}
检索结果：{docs}
规则结果：{rule}
场景：{scenario}

只输出 JSON，不要解释。
格式：
{
  "scenario": "",
  "country": "",
  "ip_type": "",
  "risk_level": "",
  "risk_points": [],
  "basis": [],
  "suggestions": []
}
""".strip()


def _template_result(
    scenario: str,
    info: Dict[str, str],
    docs: List[Dict[str, Any]],
    rule: Dict[str, Any],
) -> Dict[str, Any]:
    risk_points = [d.get("risk_point", "") for d in docs if d.get("risk_point")]
    basis = list(rule.get("rule_basis", []))
    basis.extend([f"检索依据: {d.get('text', '')[:60]}" for d in docs])
    return {
        "scenario": scenario,
        "country": info.get("country", ""),
        "ip_type": info.get("ip_type", ""),
        "risk_level": rule.get("risk_level", "中"),
        "risk_points": risk_points[:5],
        "basis": basis[:6],
        "suggestions": [
            "进行目标市场侵权与在先权利检索。",
            "对核心专利或商标进行本地注册与监控。",
            "在商业化前获取当地律师法律意见。",
        ],
    }


def generate_result(
    query: str,
    scenario: str,
    info: Dict[str, str],
    docs: List[Dict[str, Any]],
    rule: Dict[str, Any],
) -> Dict[str, Any]:
    prompt = (
        PROMPT.replace("{query}", query)
        .replace("{info}", str(info))
        .replace("{docs}", str(docs))
        .replace("{rule}", str(rule))
        .replace("{scenario}", scenario)
    )
    try:
        text = call_llm(prompt)
        data = safe_json_loads(text)
        if isinstance(data, dict):
            return data
    except (LLMClientError, ValueError, TypeError, KeyError):
        pass
    return _template_result(scenario, info, docs, rule)
