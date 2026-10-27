// Cuộc trao đổi chỉ lưu trong sessionStorage (ADR-06): mất khi đóng thẻ; máy chủ không lưu.
import type { Answer } from "../api-client/client";
import type { UiError } from "../api-client/uiErrors";

export interface Turn {
  id: string;
  question: string;
  state: "sending" | "done" | "error";
  answer?: Answer;
  error?: UiError;
}

const KEY = "cwd.conversation.v1";

export function loadTurns(): Turn[] {
  try {
    const raw = sessionStorage.getItem(KEY);
    const turns = raw ? (JSON.parse(raw) as Turn[]) : [];
    // lượt đang gửi khi tải lại trang không thể tiếp tục: bỏ đi
    return Array.isArray(turns) ? turns.filter((t) => t.state === "done") : [];
  } catch {
    return [];
  }
}

export function saveTurns(turns: Turn[]) {
  try {
    sessionStorage.setItem(KEY, JSON.stringify(turns.filter((t) => t.state === "done")));
  } catch {
    /* sessionStorage có thể bị chặn: vẫn hoạt động, chỉ không giữ khi tải lại */
  }
}

export function clearTurns() {
  try {
    sessionStorage.removeItem(KEY);
  } catch {
    /* bỏ qua */
  }
}
