import json
from pathlib import Path
from typing import Dict, List

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "ipbench.json"


def _tokenize(text: str) -> List[str]:
    return [t for t in text.lower().replace("，", " ").replace(",", " ").split() if t]


def _simple_score(query: str, text: str) -> int:
    q_tokens = set(_tokenize(query))
    t_tokens = set(_tokenize(text))
    return len(q_tokens & t_tokens)


def retrieve_topk(query: str, topk: int = 3) -> List[Dict]:
    with DATA_PATH.open("r", encoding="utf-8") as f:
        docs = json.load(f)

    try:
        from rank_bm25 import BM25Okapi

        tokenized_corpus = [_tokenize(d.get("text", "")) for d in docs]
        bm25 = BM25Okapi(tokenized_corpus)
        scores = bm25.get_scores(_tokenize(query))
        ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
        return [d for d, s in ranked[:topk] if s > 0] or docs[:topk]
    except Exception:
        ranked = sorted(docs, key=lambda d: _simple_score(query, d.get("text", "")), reverse=True)
        return ranked[:topk]
