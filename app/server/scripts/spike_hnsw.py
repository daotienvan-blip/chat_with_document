"""Spike S3-00: HNSW so với quét chính xác khi có điều kiện lọc searchable.

Chạy: python scripts/spike_hnsw.py [--db URL] [--n 40000] [--dim 384]
Dùng CSDL riêng (mặc định cwd_test); XÓA dữ liệu trong documents/chunks/jobs của CSDL đó.
Vector ngẫu nhiên: chỉ đo độ trễ / số dòng trả về / recall so với quét chính xác, không đo chất lượng ngữ nghĩa.
"""
from __future__ import annotations

import argparse
import random
import statistics
import time

from sqlalchemy import create_engine, text

ap = argparse.ArgumentParser()
ap.add_argument("--db", default="postgresql+psycopg:///cwd_test")
ap.add_argument("--n", type=int, default=40000)
ap.add_argument("--docs", type=int, default=200)
ap.add_argument("--dim", type=int, default=64)
ap.add_argument("--queries", type=int, default=100)
a = ap.parse_args()

eng = create_engine(a.db)
with eng.begin() as c:
    dim = c.execute(text("SELECT atttypmod FROM pg_attribute WHERE attrelid='chunks'::regclass "
                         "AND attname='embedding'")).scalar_one()
    c.execute(text("TRUNCATE jobs, chunks, documents"))
    c.execute(text("""
        INSERT INTO documents (id, name, size_bytes, storage_key, content_sha256, status, failure_reason, ready_at,
                               deleted_at)
        SELECT gen_random_uuid(), 'd' || i || '.pdf', 1, 'documents/' || gen_random_uuid() || '.pdf', repeat('a', 64),
               CASE WHEN i % 10 = 1 THEN 'processing' ELSE 'ready' END, NULL,
               CASE WHEN i % 10 = 1 THEN NULL ELSE now() END,
               CASE WHEN i % 10 = 2 THEN now() ELSE NULL END
        FROM generate_series(1, :docs) i"""), dict(docs=a.docs))
    t0 = time.time()
    c.execute(text(f"""
        INSERT INTO chunks (document_id, chunk_index, page_start, page_end, text, embedding)
        SELECT d.id, s.i, 1, 1, 'x',
               (SELECT array_agg(random() - 0.5)::vector({dim}) FROM generate_series(1, {dim}) WHERE s.i >= 0)
        FROM (SELECT id, row_number() OVER () AS rn FROM documents) d
        CROSS JOIN generate_series(0, :per - 1) s(i)"""), dict(per=a.n // a.docs))
    print(f"nạp {a.n} đoạn ({dim} chiều) trong {time.time() - t0:.1f}s")
    c.execute(text("ANALYZE chunks; ANALYZE documents"))
    ver = c.execute(text("SELECT version()")).scalar_one().split(" on ")[0]
    pgv = c.execute(text("SELECT extversion FROM pg_extension WHERE extname='vector'")).scalar_one()

SQL = """SELECT c.id FROM chunks c JOIN documents d ON d.id = c.document_id
         WHERE d.status='ready' AND d.deleted_at IS NULL ORDER BY {order} LIMIT 20"""
qs = [[random.uniform(-0.5, 0.5) for _ in range(dim)] for _ in range(a.queries)]


def run(mode: str, ef: int | None = None, iterative: bool = False):
    lat, rows, results = [], [], []
    with eng.connect() as c:
        for q in qs:
            lit = "[" + ",".join(f"{x:.5f}" for x in q) + "]"
            with c.begin():
                if ef:
                    c.execute(text(f"SET LOCAL hnsw.ef_search = {ef}"))
                if iterative:
                    c.execute(text("SET LOCAL hnsw.iterative_scan = relaxed_order"))
                order = f"(c.embedding <=> '{lit}'::vector)" + (" + 0" if mode == "exact" else "")
                t = time.perf_counter()
                ids = [r[0] for r in c.execute(text(SQL.format(order=order))).all()]
                lat.append((time.perf_counter() - t) * 1000)
            rows.append(len(ids))
            results.append(ids)
    return lat, rows, results


exact_lat, exact_rows, exact_res = run("exact")
report = [("exact", None, False, exact_lat, exact_rows, 1.0)]
for ef, it in [(40, False), (100, False), (200, False), (40, True), (100, True)]:
    lat, rows, res = run("hnsw", ef, it)
    recall = statistics.mean(len(set(r) & set(e)) / max(1, len(e)) for r, e in zip(res, exact_res, strict=True))
    report.append(("hnsw", ef, it, lat, rows, recall))

print(f"\n{ver}, pgvector {pgv}, {a.n} đoạn, {a.docs} tài liệu (10% processing, 10% đã xóa), {a.queries} truy vấn\n")
print("| Chế độ | ef_search | Quét lặp | p50 ms | p95 ms | Dòng trả về (min/TB) | Recall@20 so với exact |")
print("|---|---|---|---|---|---|---|")
for mode, ef, it, lat, rows, rec in report:
    lat.sort()
    print(f"| {mode} | {ef or '—'} | {'có' if it else 'không'} | {statistics.median(lat):.1f} | "
          f"{lat[int(len(lat) * 0.95) - 1]:.1f} | {min(rows)}/{statistics.mean(rows):.1f} | {rec:.3f} |")
with eng.begin() as c:
    c.execute(text("TRUNCATE jobs, chunks, documents"))
