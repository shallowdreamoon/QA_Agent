import re
from typing import Dict

from app.llm import call_llm, safe_json_loads

EXTRACT_PROMPT = """
你是知识产权信息抽取助手。
从用户问题中抽取：
- country（国家，ISO简写优先，如 US/EU/CN/JP）
- ip_type（专利/商标/版权）
- action（销售/并购/研发）

只输出JSON，格式：
{"country":"","ip_type":"","action":""}

用户问题：{query}
""".strip()

COUNTRY_MAP = {
    "美国": "US",
    "us": "US",
    "usa": "US",
    "欧盟": "EU",
    "欧洲": "EU",
    "eu": "EU",
    "中国": "CN",
    "cn": "CN",
    "日本": "JP",
    "jp": "JP",
}


def _rule_extract(query: str) -> Dict[str, str]:
    q = query.lower()
    country = ""
    for k, v in COUNTRY_MAP.items():
        if k in q:
            country = v
            break

    if re.search(r"专利|patent", q):
        ip_type = "专利"
    elif re.search(r"商标|trademark", q):
        ip_type = "商标"
    elif re.search(r"版权|著作权|copyright", q):
        ip_type = "版权"
    else:
        ip_type = ""

    if re.search(r"并购|收购|acquisition|m&a", q):
        action = "并购"
    elif re.search(r"研发|开发|research|r&d", q):
        action = "研发"
    elif re.search(r"销售|售卖|sell|sale|market", q):
        action = "销售"
    else:
        action = ""

    return {"country": country, "ip_type": ip_type, "action": action}


def extract_info(query: str) -> Dict[str, str]:
    prompt = EXTRACT_PROMPT.format(query=query)
    raw = call_llm(prompt)

    try:
        parsed = safe_json_loads(raw)
        out = {
            "country": str(parsed.get("country", "")).strip(),
            "ip_type": str(parsed.get("ip_type", "")).strip(),
            "action": str(parsed.get("action", "")).strip(),
        }
    except Exception:
        out = _rule_extract(query)

    rule = _rule_extract(query)
    out["country"] = out["country"] or rule["country"]
    out["ip_type"] = out["ip_type"] or rule["ip_type"]
    out["action"] = out["action"] or rule["action"]
    return out
