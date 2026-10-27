// Mã lỗi → thông báo và hành vi giao diện (API_Design §3.5.5, Blueprint §3.5.4, SCR-05). Mã lạ ⇒ lỗi chung.
import { ApiError } from "./client";

export interface UiError {
  title: string;
  message: string;
  retryable: boolean;
  retryAfter?: number;
  requestId?: string;
  fieldError?: boolean;
}

const TABLE: Record<string, Omit<UiError, "retryAfter" | "requestId">> = {
  AI_UNAVAILABLE: { title: "Dịch vụ AI tạm thời không dùng được", message: "Dịch vụ AI tạm thời không dùng được. Câu hỏi của bạn vẫn được giữ.", retryable: true },
  AI_TIMEOUT: { title: "Hết thời gian chờ", message: "Hết thời gian chờ. Câu hỏi của bạn vẫn được giữ.", retryable: true },
  TIMEOUT: { title: "Hết thời gian chờ", message: "Hết thời gian chờ. Câu hỏi của bạn vẫn được giữ.", retryable: true },
  SYSTEM_BUSY: { title: "Hệ thống đang bận", message: "Hệ thống đang bận. Tài liệu của bạn không bị mất. Vui lòng thử lại.", retryable: true },
  RATE_LIMITED: { title: "Bạn thao tác quá nhanh", message: "Bạn thao tác quá nhanh. Vui lòng thử lại sau ít giây.", retryable: true },
  NETWORK: { title: "Mất kết nối", message: "Không kết nối được tới máy chủ. Kiểm tra mạng rồi gửi lại. Câu hỏi của bạn vẫn được giữ.", retryable: true },
  STORAGE_UNAVAILABLE: { title: "Chưa lưu được tệp", message: "Chưa lưu được tệp. Vui lòng thử lại.", retryable: true },
  QUESTION_TOO_LONG: { title: "Câu hỏi quá dài", message: "Câu hỏi quá dài. Hãy rút gọn trước khi gửi.", retryable: false, fieldError: true },
  EMPTY_QUESTION: { title: "Câu hỏi rỗng", message: "Vui lòng nhập câu hỏi.", retryable: false, fieldError: true },
  UNSUPPORTED_TYPE: { title: "Sai định dạng", message: "Chỉ hỗ trợ tệp PDF.", retryable: false },
  FILE_TOO_LARGE: { title: "Tệp quá lớn", message: "Tệp lớn hơn giới hạn cho phép.", retryable: false },
  NOT_FOUND: { title: "Không tìm thấy", message: "Tài liệu không còn tồn tại.", retryable: false },
  INVALID_REQUEST: { title: "Yêu cầu không hợp lệ", message: "Yêu cầu không hợp lệ. Vui lòng thử lại.", retryable: false },
};

export function toUiError(e: unknown): UiError {
  const err = e instanceof ApiError ? e : new ApiError("NETWORK", 0, "");
  const base = TABLE[err.code];
  if (!base) {
    const ref = err.requestId ? ` Mã tham chiếu: ${err.requestId}.` : "";
    return { title: "Đã xảy ra lỗi", message: `Đã xảy ra lỗi. Vui lòng thử lại; nếu còn lặp lại, hãy báo mã tham chiếu.${ref}`, retryable: true, requestId: err.requestId };
  }
  let message = base.message;
  if (err.code === "FILE_TOO_LARGE" && err.limit) message = `Tệp lớn hơn giới hạn ${err.limit} MB.`;
  if (err.code === "QUESTION_TOO_LONG" && err.limit) message = `Câu hỏi dài hơn ${err.limit} ký tự. Hãy rút gọn trước khi gửi.`;
  return { ...base, message, retryAfter: err.retryAfter, requestId: err.requestId };
}

export const FAILURE_MESSAGES: Record<string, [string, string]> = {
  FILE_CORRUPT: ["Tệp bị hỏng, không đọc được.", "Hãy tải lại tệp khác."],
  FILE_ENCRYPTED: ["Tệp có mật khẩu.", "Bỏ mật khẩu rồi tải lại."],
  NO_EXTRACTABLE_TEXT: ["Tệp không có văn bản đọc được (có thể là ảnh quét).", "Dùng bản có văn bản."],
  PROCESSING_ERROR: ["Xử lý tài liệu không thành công.", "Vui lòng thử tải lại."],
};
