import re
from typing import Dict

from app.llm import LLMClientError, call_llm
from app.utils import safe_json_loads

PROMPT = """
你是知识产权信息抽取器。
从问题中抽取：
- country
- ip_type（专利/商标/版权）
- action（销售/并购/研发/未知）

规则：
- 只输出 JSON
- 不要解释

输出格式：
{"country":"","ip_type":"","action":""}

问题：{query}
""".strip()


COUNTRY_MAP = {
    "美国": "美国",
    "us": "美国",
    "usa": "美国",
    "欧盟": "欧盟",
    "eu": "欧盟",
    "欧洲": "欧盟",
    "日本": "日本",
    "jp": "日本",
    "中国": "中国",
    "cn": "中国",
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

    if re.search(r"销售|售卖|sell|sale", q):
        action = "销售"
    elif re.search(r"并购|收购|acquisition|m&a", q):
        action = "并购"
    elif re.search(r"研发|开发|research|r&d", q):
        action = "研发"
    else:
        action = "未知"

    return {"country": country, "ip_type": ip_type, "action": action}


def extract_info(query: str) -> Dict[str, str]:
    prompt = PROMPT.replace("{query}", query)
    try:
        text = call_llm(prompt)
        data = safe_json_loads(text)
        info = {
            "country": str(data.get("country", "")).strip(),
            "ip_type": str(data.get("ip_type", "")).strip(),
            "action": str(data.get("action", "")).strip(),
        }
        fallback = _rule_extract(query)
        info["country"] = info["country"] or fallback["country"]
        info["ip_type"] = info["ip_type"] or fallback["ip_type"]
        info["action"] = info["action"] or fallback["action"]
        return info
    except (LLMClientError, ValueError, TypeError, KeyError):
        return _rule_extract(query)
