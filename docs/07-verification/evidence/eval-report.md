# Báo cáo đánh giá — 20261028-191854

- Bộ dữ liệu: `synthetic.jsonl` (15 câu)
- AI: `extractive`; số chiều 384; truy xuất `exact`; min_relevance 0.0
- Độ đúng nội dung (G3, MET-002) cần người chấm cột cuối của CSV; ngưỡng `[TBD: OQ-004]`.

| Chỉ số | Giá trị |
|---|---|
| G5 câu ngoài tài liệu → not_found | 80% |
| Tỷ lệ câu trong phạm vi có trả lời | 100% |
| G4 nguồn đúng tài liệu (câu có trả lời) | 100% |
| Nguồn phủ đủ tài liệu kỳ vọng | 100% |
| Trang đúng (khi có kỳ vọng) | 100% |
| Ổn định giữa các lần chạy | 100% |

| id | loại | trạng thái | nguồn | kỳ vọng |
|---|---|---|---|---|
| q01 | in_scope | answered | hop-dong-A.pdf | hop-dong-A.pdf |
| q02 | in_scope | answered | hop-dong-A.pdf | hop-dong-A.pdf |
| q03 | in_scope | partial | hop-dong-A.pdf | hop-dong-A.pdf |
| q04 | in_scope | answered | hop-dong-A.pdf | hop-dong-A.pdf |
| q05 | in_scope | answered | bao-gia-B.pdf | bao-gia-B.pdf |
| q06 | in_scope | answered | bao-gia-B.pdf | bao-gia-B.pdf |
| q07 | in_scope | answered | quy-dinh-C.pdf | quy-dinh-C.pdf |
| q08 | in_scope | answered | quy-dinh-C.pdf | quy-dinh-C.pdf |
| q09 | multi_doc | answered | bao-gia-B.pdf, hop-dong-A.pdf | hop-dong-A.pdf, bao-gia-B.pdf |
| q10 | multi_doc | answered | bao-gia-B.pdf, hop-dong-A.pdf | hop-dong-A.pdf, bao-gia-B.pdf |
| q11 | out_of_scope | not_found | — | not_found |
| q12 | out_of_scope | not_found | — | not_found |
| q13 | out_of_scope | not_found | — | not_found |
| q14 | out_of_scope | not_found | — | not_found |
| q15 | out_of_scope | answered | hop-dong-A.pdf, quy-dinh-C.pdf | not_found |
