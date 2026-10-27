import { act, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { App } from "./App";
import { toUiError } from "../api-client/uiErrors";
import { ApiError } from "../api-client/client";

type Route = (url: string, init?: RequestInit) => Response | Promise<Response>;
const json = (body: unknown, status = 200, headers: Record<string, string> = {}) =>
  new Response(body === undefined ? null : JSON.stringify(body), {
    status,
    headers: { "Content-Type": status >= 400 ? "application/problem+json" : "application/json", ...headers },
  });

const doc = (over: Record<string, unknown> = {}) => ({
  id: "11111111-1111-1111-1111-111111111111", name: "hop-dong-A.pdf", sizeBytes: 482113, pageCount: 12,
  status: "ready", failureReason: null, createdAt: "2026-10-27T03:00:00Z", ...over,
});
const config = { maxFileSizeMb: null, maxQuestionLength: null, language: null, pollIntervalMs: 2000 };

let calls: string[] = [];
function setup(routes: Record<string, Route>) {
  calls = [];
  vi.stubGlobal("fetch", vi.fn(async (input: string, init?: RequestInit) => {
    const key = `${init?.method ?? "GET"} ${input}`;
    calls.push(key);
    const h = routes[key] ?? routes[input];
    if (!h) return json({ code: "NOT_FOUND", detail: "x", requestId: "r" }, 404);
    return h(input, init);
  }));
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}><App /></QueryClientProvider>);
}

beforeEach(() => sessionStorage.clear());
afterEach(() => vi.unstubAllGlobals());

it("[US-006-AC2] kho trống: hướng dẫn tải và khóa khung hỏi", async () => {
  setup({ "/api/v1/config": () => json(config), "/api/v1/documents": () => json({ items: [], total: 0 }) });
  expect(await screen.findByText("Chưa có tài liệu nào")).toBeInTheDocument();
  expect(screen.getByLabelText("Câu hỏi của bạn")).toBeDisabled();
  expect(screen.getByRole("button", { name: /Gửi/ })).toBeDisabled();
});

it("[US-002-AC2][US-003-AC2] trạng thái có chữ, lý do lỗi và tài liệu chưa sẵn sàng", async () => {
  setup({
    "/api/v1/config": () => json(config),
    "/api/v1/documents": () => json({ items: [
      doc({ id: "a", status: "processing", pageCount: null }),
      doc({ id: "b", name: "quy-dinh-C.pdf", status: "failed", failureReason: "FILE_ENCRYPTED" }),
    ], total: 2 }),
  });
  expect(await screen.findByText("Đang xử lý")).toBeInTheDocument();
  expect(screen.getByText("chưa dùng để trả lời")).toBeInTheDocument();
  expect(screen.getByText("Tệp có mật khẩu.")).toBeInTheDocument();
  expect(screen.getByText(/Bỏ mật khẩu rồi tải lại/)).toBeInTheDocument();
  expect(screen.getByLabelText("Câu hỏi của bạn")).toBeDisabled(); // chưa có tài liệu ready
});

it("[US-001-AC3] tệp không phải PDF bị từ chối, không tạo dòng", async () => {
  setup({ "/api/v1/config": () => json(config), "/api/v1/documents": () => json({ items: [], total: 0 }) });
  await screen.findByText("Chưa có tài liệu nào");
  const input = screen.getByLabelText("Chọn tệp PDF");
  await userEvent.upload(input, new File(["x"], "bao-cao.docx"), { applyAccept: false });
  expect(await screen.findByRole("alert")).toHaveTextContent("bao-cao.docx: Chỉ hỗ trợ tệp PDF.");
  expect(screen.queryAllByTestId("doc-row")).toHaveLength(0);
});

it("[US-006-AC1][US-007-AC1][US-008-AC1] hỏi, hiển thị nguồn dạng chip mở đúng trang; giữ qua tải lại", async () => {
  const user = userEvent.setup();
  setup({
    "/api/v1/config": () => json(config),
    "/api/v1/documents": () => json({ items: [doc()], total: 1 }),
    "POST /api/v1/questions": () => json({ status: "answered", answer: "Thanh toán trong 30 ngày.",
      sources: [{ documentId: doc().id, documentName: "hop-dong-A.pdf", pages: [4, 5] }] }),
  });
  const box = await screen.findByLabelText("Câu hỏi của bạn");
  await waitFor(() => expect(box).toBeEnabled());
  await user.type(box, "   ");
  expect(screen.getByRole("button", { name: /Gửi/ })).toBeDisabled(); // EC-08
  await user.clear(box);
  await user.type(box, "Điều khoản thanh toán là gì?{Enter}");
  expect(await screen.findByText("Có căn cứ từ tài liệu")).toBeInTheDocument();
  const chip = screen.getByRole("link", { name: "Mở hop-dong-A.pdf, tr. 4, 5 trong thẻ mới" });
  expect(chip).toHaveAttribute("href", `/api/v1/documents/${doc().id}/file#page=4`);
  expect(chip).toHaveAttribute("target", "_blank");
  expect(JSON.parse(sessionStorage.getItem("cwd.conversation.v1")!)).toHaveLength(1);
  await user.click(screen.getByRole("button", { name: /Cuộc trao đổi mới/ }));
  expect(screen.queryByText("Có căn cứ từ tài liệu")).not.toBeInTheDocument();
});

it("[US-010-AC1][US-010-AC2] không tìm thấy và trả lời một phần có kiểu hiển thị riêng", async () => {
  const user = userEvent.setup();
  const answers = [
    { status: "not_found", answer: "Không tìm thấy thông tin trong các tài liệu đã tải.", sources: [] },
    { status: "partial", answer: "Phạt 0,05%/ngày.", sources: [{ documentId: "gone", documentName: "da-xoa.pdf", pages: [] }] },
  ];
  setup({
    "/api/v1/config": () => json(config),
    "/api/v1/documents": () => json({ items: [doc()], total: 1 }),
    "POST /api/v1/questions": () => json(answers.shift()),
  });
  const box = await screen.findByLabelText("Câu hỏi của bạn");
  await waitFor(() => expect(box).toBeEnabled());
  await user.type(box, "Giá cổ phiếu?{Enter}");
  expect(await screen.findByText("Không tìm thấy thông tin")).toBeInTheDocument();
  await user.type(box, "Phạt và bảo hành?{Enter}");
  expect(await screen.findByText("Trả lời một phần")).toBeInTheDocument();
  const gone = screen.getByText(/da-xoa\.pdf/).closest(".chip")!;
  expect(gone).toHaveAttribute("aria-disabled", "true"); // tài liệu không còn trong danh sách ⇒ "(đã xóa)"
  expect(within(gone as HTMLElement).getByText("(đã xóa)")).toBeInTheDocument();
});

it("[EC-07] lỗi AI giữ câu hỏi, đếm ngược Retry-After rồi gửi lại", async () => {
  vi.useFakeTimers({ shouldAdvanceTime: true });
  const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
  let n = 0;
  setup({
    "/api/v1/config": () => json(config),
    "/api/v1/documents": () => json({ items: [doc()], total: 1 }),
    "POST /api/v1/questions": () => (n++ === 0
      ? json({ type: "x", title: "x", status: 503, code: "SYSTEM_BUSY", detail: "bận", requestId: "r1" }, 503, { "Retry-After": "2" })
      : json({ status: "answered", answer: "OK", sources: [{ documentId: doc().id, documentName: "hop-dong-A.pdf", pages: [1] }] })),
  });
  const box = await screen.findByLabelText("Câu hỏi của bạn");
  await waitFor(() => expect(box).toBeEnabled());
  await user.type(box, "Câu hỏi giữ nguyên{Enter}");
  expect(await screen.findByText("Hệ thống đang bận")).toBeInTheDocument();
  expect(box).toHaveValue("Câu hỏi giữ nguyên");
  const retry = screen.getByRole("button", { name: /Gửi lại sau 2 giây/ });
  expect(retry).toBeDisabled();
  for (let i = 0; i < 3; i++) await act(async () => { vi.advanceTimersByTime(1000); });
  await user.click(await screen.findByRole("button", { name: /^Gửi lại$/ }));
  expect(await screen.findByText("OK")).toBeInTheDocument();
  vi.useRealTimers();
});

it("[US-005-AC1] hộp thoại xóa: focus vào Hủy, Esc đóng, xác nhận gọi DELETE", async () => {
  const user = userEvent.setup();
  let items = [doc()];
  setup({
    "/api/v1/config": () => json(config),
    "/api/v1/documents": () => json({ items, total: items.length }),
    [`DELETE /api/v1/documents/${doc().id}`]: () => { items = []; return new Response(null, { status: 204 }); },
  });
  const del = await screen.findByRole("button", { name: "Xóa tài liệu hop-dong-A.pdf" });
  await user.click(del);
  const dialog = screen.getByRole("alertdialog");
  expect(within(dialog).getByRole("button", { name: "Hủy" })).toHaveFocus();
  await user.keyboard("{Escape}");
  expect(screen.queryByRole("alertdialog")).not.toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "Xóa tài liệu hop-dong-A.pdf" }));
  await user.tab(); await user.tab();
  expect(within(screen.getByRole("alertdialog")).getByRole("button", { name: "Hủy" })).toHaveFocus(); // bẫy Tab
  await user.click(within(screen.getByRole("alertdialog")).getByRole("button", { name: /Xóa tài liệu/ }));
  await waitFor(() => expect(screen.queryByRole("alertdialog")).not.toBeInTheDocument());
  expect(calls).toContain(`DELETE /api/v1/documents/${doc().id}`);
  expect(await screen.findByText("Chưa có tài liệu nào")).toBeInTheDocument();
});

it("ánh xạ lỗi: mã lạ ⇒ lỗi chung có mã tham chiếu; lỗi trường không thử lại", () => {
  const u = toUiError(new ApiError("SOMETHING_NEW", 500, "", "abc"));
  expect(u.retryable).toBe(true);
  expect(u.message).toContain("abc");
  const t = toUiError(new ApiError("QUESTION_TOO_LONG", 400, "", "r", 10));
  expect(t.fieldError).toBe(true);
  expect(t.message).toContain("10 ký tự");
});
