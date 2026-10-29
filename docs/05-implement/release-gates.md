# Cổng phát hành — bằng chứng (PRD §5.1) — 2026-10-28

> Trạng thái trung thực. “Đạt (demo)” = đạt trên bản demo cục bộ với AI giả; **không** đồng nghĩa sẵn sàng phát hành. Người chịu trách nhiệm `[TBD: OQ-007]`.

| Cổng | Tiêu chí | Bằng chứng | Trạng thái |
|---|---|---|---|
| G1 | 100% story P0 đạt toàn bộ AC | `make test-int`, `make check`, `make trace` (22/23 AC có test; US-015 chờ OQ-005) | Chưa — US-015 (P0) chờ phê duyệt; chưa UAT |
| G2 | 0 lỗi nghiêm trọng mở với P0 | Tạm theo dõi trong `docs/07-verification/test-report.md` §5 | Chưa — DEF-001 đã sửa (PR `fix/def-001-not-found`, chờ L2); F-02, F-03 (Major) còn mở |
| G3 | Tỷ lệ câu trả lời đúng ≥ ngưỡng | `make eval` → CSV cho người chấm | **Chặn** OQ-004, DEP-002; chưa có mô hình thật |
| G4 | 100% câu có nội dung tài liệu có nguồn đúng | G-L2/G-L3 + test tích hợp; eval tổng hợp 100% | Đạt (demo) — cần chạy lại với AI thật + bộ thật |
| G5 | Câu ngoài tài liệu → “không tìm thấy” 100% | `test_not_found_paths`; `test_extractive_accents_def001`; smoke; eval tổng hợp **5/5 = 100%** (2026-10-29, sau sửa DEF-001) | Đạt (demo) — bộ 5 câu nhỏ; còn rủi ro khớp từng âm tiết ("công ty" vs "công tác") và G-L1 tắt (`RAG_MIN_RELEVANCE=0`) — cần chạy lại với AI thật + bộ thật |
| G8 | Vị trí lưu trữ được duyệt và cấu hình | `app/deploy/DATA_LOCATION.md` | **Chặn** OQ-005 |
| G9 | 0 lỗ hổng cao/nghiêm trọng; NFR-SEC-001/002 | Phân quyền CSDL (test + chạy thật trong `make prod-up`), xác thực tệp, không lộ lỗi; TLS ≥ 1.2, tiêu đề bảo mật, allowlist, container không root; câu hỏi ≤ 4.000 ký tự, thân ≤ 64 KB ở proxy — F-03 (`make proxy-test` 15/15, 2026-10-29) | Chưa — gitleaks toàn bộ lịch sử git: 0 bí mật (2026-10-28); chưa quét lỗ hổng phụ thuộc/ảnh; TLS mới chạy cục bộ với chứng chỉ tự ký; mã hóa lưu trữ phụ thuộc hạ tầng (OQ-005) |
| G11 | Có quy trình xóa khi sự cố | `runbook.md` mục “Xóa khẩn cấp” | Đạt (tài liệu) — OQ-D01 về sao lưu còn mở |
| G12 | Business owner xác nhận UAT, số thao tác | Chưa UAT; giao diện chưa thử trên trình duyệt thật | Chưa |
| G13 | Mọi NFR mức Must đạt | NFR-CAP-001 cấu hình được (giá trị chờ OQ-009); NFR-SEC-001/002 chưa triển khai | Chưa |

**Kết luận:** chưa đủ điều kiện phát hành. Bản demo chứng minh luồng 13 use case chạy được đầu-cuối.
