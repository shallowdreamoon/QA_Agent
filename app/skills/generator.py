from typing import Any, Dict, List

from app.llm import call_llm, safe_json_loads

GENERATE_PROMPT = """
你是企业出海知识产权风险分析助手。
根据输入生成严格JSON：
{
  "scenario": "",
  "country": "",
  "ip_type": "",
  "risk_level": "",
  "risk_points": [],
  "basis": [],
  "suggestions": []
}

输入：
- 用户问题: {query}
- 抽取信息: {extracted}
- 检索结果: {retrieved}
- 规则结果: {ruled}

仅输出JSON。
""".strip()


def _fallback_generate(
    scenario: str,
    extracted: Dict[str, str],
    retrieval_results: List[Dict[str, Any]],
    rule_result: Dict[str, Any],
) -> Dict[str, Any]:
    risk_points = [r.get("risk_point", "") for r in retrieval_results if r.get("risk_point")]
    basis = list(rule_result.get("rule_basis", []))
    basis.extend([f"IPBench匹配: {r.get('text', '')[:80]}" for r in retrieval_results])

    suggestions = [
        "在目标市场开展FTO（自由实施）检索。",
        "对核心商标/专利进行本地注册与监控。",
        "必要时咨询当地知识产权律师出具法律意见。",
    ]

    return {
        "scenario": scenario,
        "country": extracted.get("country", ""),
        "ip_type": extracted.get("ip_type", ""),
        "risk_level": rule_result.get("risk_level", "中"),
        "risk_points": risk_points[:5],
        "basis": basis[:6],
        "suggestions": suggestions,
    }


def generate_result(
    query: str,
    scenario: str,
    extracted: Dict[str, str],
    retrieval_results: List[Dict[str, Any]],
    rule_result: Dict[str, Any],
) -> Dict[str, Any]:
    prompt = GENERATE_PROMPT.format(
        query=query,
        extracted=extracted,
        retrieved=retrieval_results,
        ruled=rule_result,
    )
    raw = call_llm(prompt)

    try:
        parsed = safe_json_loads(raw)
    except Exception:
        return _fallback_generate(scenario, extracted, retrieval_results, rule_result)

    fallback = _fallback_generate(scenario, extracted, retrieval_results, rule_result)
    for key in ["scenario", "country", "ip_type", "risk_level", "risk_points", "basis", "suggestions"]:
        if key not in parsed or parsed[key] in (None, ""):
            parsed[key] = fallback[key]

    for key in ["risk_points", "basis", "suggestions"]:
        if not isinstance(parsed.get(key), list):
            parsed[key] = fallback[key]

    return parsed
