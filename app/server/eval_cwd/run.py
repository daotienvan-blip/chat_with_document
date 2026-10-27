"""Bộ đánh giá chất lượng AI (S8-04): chạy bộ câu hỏi, tính chỉ số tự động, xuất CSV cho người chấm.

Chạy: python -m eval_cwd.run [--dataset eval_cwd/datasets/synthetic.jsonl] [--llm extractive|http] [--out ../var/eval]
Dùng CSDL TEST_DATABASE_URL (mặc định cwd_test) — XÓA dữ liệu ở đó. Ngưỡng độ đúng (G3) chưa có: [TBD: OQ-004].
Bộ tổng hợp chỉ kiểm tra công cụ; bộ thật do business owner cung cấp (DEP-002), không commit nội dung nhạy cảm.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import statistics
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, text

from cwd_server.adapters.stores import InMemoryObjectStore
from cwd_server.container import build_container
from cwd_server.core.documents.validate_upload import validate_upload
from cwd_server.persistence.db import render_schema
from cwd_server.platform.config import Settings
from cwd_server.worker.__main__ import build_runner
from scripts.make_samples import DOCS
from tests.fixtures.pdfs import text_pdf

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default=str(ROOT / "eval_cwd" / "datasets" / "synthetic.jsonl"))
    ap.add_argument("--llm", default="extractive")
    ap.add_argument("--out", default=str(ROOT.parent / "var" / "eval"))
    ap.add_argument("--runs", type=int, default=2)
    a = ap.parse_args()
    db = os.environ.get("TEST_DATABASE_URL", "postgresql+psycopg:///cwd_test")
    s = Settings(_env_file=None, database_url=db, object_store="memory", llm_provider=a.llm, embedding_dim=384,
                 rate_limit_enabled=False)
    eng = create_engine(db)
    with eng.begin() as c:
        c.execute(text("DROP TABLE IF EXISTS jobs, chunks, documents CASCADE"))
        c.execute(text(render_schema(s.schema_sql, s.embedding_dim)))
    eng.dispose()
    cont = build_container(s, store=InMemoryObjectStore())
    for name, pages in DOCS.items():
        cont.documents.upload(validate_upload(io.BytesIO(text_pdf(pages)), name, 50))
    build_runner(cont)[0].run_until_idle()
    rows = [json.loads(line) for line in Path(a.dataset).read_text(encoding="utf-8").splitlines() if line.strip()]

    runs = []
    for _ in range(a.runs):
        res = []
        for r in rows:
            out = cont.answers.ask(r["question"])
            res.append((r, out))
        runs.append(res)
    res = runs[0]
    stable = all(json.dumps([(o.status, o.answer, [(s.document_name, s.pages) for s in o.sources]) for _, o in rx])
                 == json.dumps([(o.status, o.answer, [(s.document_name, s.pages) for s in o.sources]) for _, o in res])
                 for rx in runs[1:])

    def got_docs(o):
        return {s.document_name for s in o.sources}
    in_scope = [(r, o) for r, o in res if r["kind"] != "out_of_scope"]
    oos = [(r, o) for r, o in res if r["kind"] == "out_of_scope"]
    answered = [(r, o) for r, o in in_scope if o.status.value != "not_found"]
    m = {
        "G5 câu ngoài tài liệu → not_found": statistics.mean([o.status.value == "not_found" for _, o in oos]) if oos else None,
        "Tỷ lệ câu trong phạm vi có trả lời": statistics.mean([o.status.value != "not_found" for _, o in in_scope]),
        "G4 nguồn đúng tài liệu (câu có trả lời)": statistics.mean(
            [got_docs(o) <= set(r["expected_docs"]) and bool(got_docs(o)) for r, o in answered]) if answered else None,
        "Nguồn phủ đủ tài liệu kỳ vọng": statistics.mean(
            [set(r["expected_docs"]) <= got_docs(o) for r, o in answered]) if answered else None,
        "Trang đúng (khi có kỳ vọng)": statistics.mean(
            [any(set(r["expected_pages"]) & set(s.pages) for s in o.sources) for r, o in answered
             if r.get("expected_pages")]) if answered else None,
        "Ổn định giữa các lần chạy": 1.0 if stable else 0.0,
    }
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    with open(out / f"grading-{stamp}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "kind", "question", "status", "answer", "sources", "expected_docs", "dung_noi_dung (người chấm: 1/0)"])
        for r, o in res:
            w.writerow([r["id"], r["kind"], r["question"], o.status.value, o.answer,
                        "; ".join(f"{s.document_name} tr.{s.pages}" for s in o.sources), ", ".join(r["expected_docs"]), ""])
    lines = [f"# Báo cáo đánh giá — {stamp}", "", f"- Bộ dữ liệu: `{Path(a.dataset).name}` ({len(rows)} câu)",
             f"- AI: `{a.llm}`; số chiều {s.embedding_dim}; truy xuất `{s.retrieval_mode}`; min_relevance {s.rag_min_relevance}",
             "- Độ đúng nội dung (G3, MET-002) cần người chấm cột cuối của CSV; ngưỡng `[TBD: OQ-004]`.", "",
             "| Chỉ số | Giá trị |", "|---|---|"]
    lines += [f"| {k} | {'—' if v is None else f'{v:.0%}'} |" for k, v in m.items()]
    lines += ["", "| id | loại | trạng thái | nguồn | kỳ vọng |", "|---|---|---|---|---|"]
    lines += [f"| {r['id']} | {r['kind']} | {o.status.value} | {', '.join(sorted(got_docs(o))) or '—'} | "
              f"{', '.join(r['expected_docs']) or 'not_found'} |" for r, o in res]
    (out / f"report-{stamp}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:16]))
    print(f"\nĐã ghi {out}/report-{stamp}.md và grading-{stamp}.csv")
    cont.db.engine.dispose()


if __name__ == "__main__":
    main()
