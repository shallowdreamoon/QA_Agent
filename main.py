from typing import Any, Dict, List

from fastapi import FastAPI
from pydantic import BaseModel, Field, ValidationError

from app.skills.extractor import extract_info
from app.skills.generator import generate_result
from app.skills.scenario import detect_scenario
from app.tools.retriever import retrieve_topk
from app.tools.rules import apply_rules

app = FastAPI(title="IP-Agent MVP")


class AskRequest(BaseModel):
    query: str = Field(..., min_length=1)


class AskResponse(BaseModel):
    scenario: str
    country: str
    ip_type: str
    risk_level: str
    risk_points: List[str]
    basis: List[str]
    suggestions: List[str]


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> Dict[str, Any]:
    query = req.query.strip()

    scenario = detect_scenario(query)["scenario"]
    extracted = extract_info(query)
    retrieved = retrieve_topk(query, topk=3)
    ruled = apply_rules(
        country=extracted.get("country", ""),
        ip_type=extracted.get("ip_type", ""),
        action=extracted.get("action", ""),
    )

    generated = generate_result(
        query=query,
        scenario=scenario,
        extracted=extracted,
        retrieval_results=retrieved,
        rule_result=ruled,
    )

    # Final JSON validation
    try:
        return AskResponse(**generated).model_dump()
    except ValidationError:
        safe = {
            "scenario": scenario,
            "country": extracted.get("country", ""),
            "ip_type": extracted.get("ip_type", ""),
            "risk_level": ruled.get("risk_level", "中"),
            "risk_points": [x.get("risk_point", "") for x in retrieved if x.get("risk_point")],
            "basis": ruled.get("rule_basis", []),
            "suggestions": ["建议进行本地知识产权检索与法律评估。"],
        }
        return AskResponse(**safe).model_dump()
