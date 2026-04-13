from typing import Dict, List


def apply_rules(country: str, ip_type: str, action: str) -> Dict[str, List[str]]:
    basis = []
    risk_level = "中"

    if country == "US" and ip_type == "专利" and action == "销售":
        risk_level = "中高"
        basis.append("规则: 美国 + 专利 + 销售 => 中高风险")

    if country == "EU" and ip_type == "商标":
        risk_level = "中"
        basis.append("规则: 欧盟 + 商标 => 注册与近似冲突风险")

    if country == "JP" and ip_type == "版权" and action == "研发":
        risk_level = "中"
        basis.append("规则: 日本 + 版权 + 研发 => 代码/内容许可合规风险")

    if not basis:
        basis.append("规则: 未命中特殊组合，采用通用中风险基线")

    return {"risk_level": risk_level, "rule_basis": basis}
