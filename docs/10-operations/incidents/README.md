# Quy trình sự cố

```
Chỉ số ra khỏi dải kiểm soát (dashboards.md §2)
  → mở incident record INC-<ngày>-<số>.md (mẫu bên dưới)
  → giảm thiểu theo runbook.md (người trực; agent chỉ đọc và đề xuất)
  → post-incident review trong 5 ngày làm việc
  → intent mới cho thay đổi khắc phục (INC-…-intent.md) → vòng SDLC thường: PR ≤ 400 dòng, L0–L2
  → bài học vào test / tài liệu / SOP
```

**Agent không thay đổi production.** Agent được: đọc metrics/log/trạng thái, tái hiện ngoài production, soạn incident record, viết intent và PR sửa (qua review như mọi PR).

## Danh sách

| Mã | Mức | Tóm tắt | Trạng thái |
|---|---|---|---|
| [INC-2026-10-28-01](INC-2026-10-28-01.md) | Sev3 (quy trình giao hàng, không phải production) | PR #1 được merge vào `main` khi CI đỏ và không có review | Đang khắc phục |

## Mẫu

```markdown
# INC-YYYY-MM-DD-NN — <tóm tắt>
| Mục | Giá trị |
|---|---|
| Mức | Sev1/2/3 |
| Phát hiện | <thời điểm, bởi ai/cảnh báo nào> |
| Ảnh hưởng | <ai, bao lâu, dữ liệu nào> |
| Người trực / chỉ huy | |
## Dòng thời gian (UTC)
## Nguyên nhân gốc (5 why)
## Giảm thiểu đã làm
## Post-incident review (không đổ lỗi)
## Hành động — mỗi dòng có chủ sở hữu, hạn, liên kết PR
| # | Loại (test/tài liệu/SOP/mã) | Hành động | Chủ | Hạn | Trạng thái |
## Intent mới
```
