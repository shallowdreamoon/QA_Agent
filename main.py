from typing import Any, Dict, List

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.skills.extractor import extract_info
from app.skills.generator import generate_result
from app.skills.scenario import detect_scenario
from app.tools import retriever
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

    scenario_obj = detect_scenario(query)
    extracted = extract_info(query)
    retrieved = retriever.search(extracted)
    ruled = apply_rules(extracted)
    generated = generate_result(
        query=query,
        scenario=scenario_obj.get("scenario", "海外侵权风险"),
        info=extracted,
        docs=retrieved,
        rule=ruled,
    )

    result = {
        "scenario": str(generated.get("scenario") or scenario_obj.get("scenario", "海外侵权风险")),
        "country": str(generated.get("country") or extracted.get("country", "")),
        "ip_type": str(generated.get("ip_type") or extracted.get("ip_type", "")),
        "risk_level": str(generated.get("risk_level") or ruled.get("risk_level", "中")),
        "risk_points": generated.get("risk_points") if isinstance(generated.get("risk_points"), list) else [],
        "basis": generated.get("basis") if isinstance(generated.get("basis"), list) else ruled.get("rule_basis", []),
        "suggestions": generated.get("suggestions") if isinstance(generated.get("suggestions"), list) else [],
    }

    return AskResponse(**result).model_dump()
