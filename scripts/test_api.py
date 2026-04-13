import json

from fastapi.testclient import TestClient

from main import app


def run_demo() -> None:
    client = TestClient(app)
    payload = {"query": "我们准备在美国销售产品，会不会有专利侵权风险？"}
    resp = client.post("/ask", json=payload)
    print("status:", resp.status_code)
    print(json.dumps(resp.json(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    run_demo()
