# S0-07 — Khung web: app shell, token thiết kế và api-client sinh kiểu từ OpenAPI

| | |
|---|---|
| **Lát cắt** | S0 — Khung chạy được (walking skeleton) (mốc M0) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S0-01](S0-01-khoi-tao-repo-cong-cu-va-quy-uoc-kiem-thu.md), [S0-03](S0-03-nen-tang-server-cau-hinh-log-loi-problem.md) |
| **Truy vết** | C-14 (nhất quán thiết kế) |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — Khung web, token từ `html_design`, kiểu sinh từ OpenAPI |

## Mục tiêu

SPA hiển thị khung ứng dụng đúng thiết kế (tiêu đề, dòng lưu ý dữ liệu, hai vùng) và gọi được `GET /config` bằng client có kiểu sinh từ `openapi.yaml`.

## Đọc trước

- html_design/index.html, scr-01…06 (CSS, bố cục)
- API_Design §3.1, §3.5
- Blueprint §2.4, §2.5
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `web/src/components/{tokens.css,ui/*}`
- `web/src/api-client/{generated.ts,client.ts,problem.ts}`
- `web/src/app/{App.tsx,Layout.tsx}`
- `web/vite.config.ts` (proxy dev `/api` → server)
- `web/src/**/*.test.tsx`

## Các bước

1. Chuyển các token màu/khoảng cách từ `html_design` sang `tokens.css` (giữ đúng giá trị đã kiểm tương phản).
2. Sinh kiểu TypeScript từ `docs/04-design/openapi.yaml` (script `npm run gen:api`); commit kết quả; CI kiểm tra không lệch.
3. `client.ts`: hàm gọi chung, đặt `AbortController`, đọc `application/problem+json` thành `ApiError {code, detail, status, limit?, requestId, retryAfter?}`; lỗi mạng → `ApiError` mã `NETWORK`.
4. Layout: header, dòng lưu ý dữ liệu (`[vị trí lưu trữ]` là chuỗi cấu hình), hai vùng, liên kết “Bỏ qua”; TanStack Query provider; `useConfig()`.
5. Test: render khung; `useConfig` với MSW; `ApiError` từ một phản hồi `problem+json`.

## Tiêu chí hoàn thành

- [ ] `npm --prefix web run build` và `make check` xanh.
- [ ] `npm --prefix web run gen:api` không tạo thay đổi trong git.
- [ ] Mở `npm run dev` cùng server (S0-03) thấy khung và `GET /config` thành công (kiểm tra tay, ghi lại trong mô tả PR).
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Chưa có danh sách tài liệu (S1-04), khung hỏi (S3-06).

## Ghi chú và rủi ro

- Chữ ≥ 16 px, dùng `rem`; vòng focus 3 px (Blueprint §2.5). Không thêm thư viện UI lớn: dùng CSS thường.
