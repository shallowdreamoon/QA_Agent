# IP-Agent (MVP)

企业出海知识产权风险智能问答系统（MVP）。

## 1. 功能概览

系统实现以下流程：

用户输入 → 场景识别（LLM）→ 信息抽取（LLM）→ IPBench检索（BM25）→ 规则判断 → 结果生成（LLM）→ JSON校验输出。

### 输出JSON格式（固定）

```json
{
  "scenario": "",
  "country": "",
  "ip_type": "",
  "risk_level": "",
  "risk_points": [],
  "basis": [],
  "suggestions": []
}
```

## 2. 项目结构

```text
.
├── main.py
├── app
│   ├── llm.py
│   ├── skills
│   │   ├── scenario.py
│   │   ├── extractor.py
│   │   └── generator.py
│   └── tools
│       ├── retriever.py
│       └── rules.py
├── data
│   └── ipbench.json
├── scripts
│   └── test_api.py
└── requirements.txt
```

## 3. 安装与运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

服务启动后：

- 健康检查：`GET /health`
- 问答接口：`POST /ask`

## 4. 接口说明

### `POST /ask`

请求：

```json
{
  "query": "我们准备在美国销售产品，会不会有专利侵权风险？"
}
```

返回：

```json
{
  "scenario": "海外侵权风险",
  "country": "US",
  "ip_type": "专利",
  "risk_level": "中高",
  "risk_points": ["..."],
  "basis": ["..."],
  "suggestions": ["..."]
}
```

## 5. LLM配置

默认通过 `OPENAI_API_KEY` 调用 OpenAI。可选环境变量：

- `OPENAI_API_KEY`
- `OPENAI_MODEL`（默认 `gpt-4o-mini`）

若未配置 API Key，系统会启用确定性 fallback 逻辑（规则+模板），保证可演示。

## 6. 示例测试脚本

```bash
python scripts/test_api.py
```

## 7. 模块可单独调用

- 场景识别：`app/skills/scenario.py::detect_scenario`
- 信息抽取：`app/skills/extractor.py::extract_info`
- 检索：`app/tools/retriever.py::retrieve_topk`
- 规则：`app/tools/rules.py::apply_rules`
- 生成：`app/skills/generator.py::generate_result`

