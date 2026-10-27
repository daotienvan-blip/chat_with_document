// Client REST có kiểu sinh từ docs/04-design/openapi.yaml (S0-07).
import type { components } from "./generated";

export type Config = components["schemas"]["Config"];
export type Doc = components["schemas"]["Document"];
export type DocumentList = components["schemas"]["DocumentList"];
export type Answer = components["schemas"]["Answer"];
export type Source = components["schemas"]["Source"];
export type Problem = components["schemas"]["Problem"];

export const API = "/api/v1";

/** Lỗi đã chuẩn hóa. code = ProblemCode, hoặc NETWORK / TIMEOUT / ABORTED do phía trình duyệt sinh. */
export class ApiError extends Error {
  constructor(
    public code: string,
    public status: number,
    public detail: string,
    public requestId?: string,
    public limit?: number,
    public retryAfter?: number,
  ) {
    super(detail);
  }
}

async function toError(res: Response): Promise<ApiError> {
  const ra = Number(res.headers.get("Retry-After")) || undefined;
  try {
    const p = (await res.json()) as Partial<Problem>;
    if (p && typeof p.code === "string") {
      return new ApiError(p.code, res.status, p.detail ?? "", p.requestId, p.limit ?? undefined, ra);
    }
  } catch {
    /* thân không phải JSON (ví dụ lỗi ở tầng proxy) */
  }
  const code = res.status === 429 ? "RATE_LIMITED" : res.status === 413 ? "FILE_TOO_LARGE" : res.status >= 500 ? "INTERNAL_ERROR" : "INVALID_REQUEST";
  return new ApiError(code, res.status, "", res.headers.get("X-Request-Id") ?? undefined, undefined, ra);
}

export async function request<T>(path: string, init: RequestInit & { timeoutMs?: number } = {}): Promise<T> {
  const ctrl = new AbortController();
  const outer = init.signal;
  let timedOut = false;
  const timer = init.timeoutMs
    ? setTimeout(() => {
        timedOut = true;
        ctrl.abort();
      }, init.timeoutMs)
    : undefined;
  outer?.addEventListener("abort", () => ctrl.abort());
  try {
    const res = await fetch(API + path, { ...init, signal: ctrl.signal });
    if (!res.ok) throw await toError(res);
    if (res.status === 204) return undefined as T;
    return (await res.json()) as T;
  } catch (e) {
    if (e instanceof ApiError) throw e;
    if (timedOut) throw new ApiError("TIMEOUT", 0, "");
    if (outer?.aborted) throw new ApiError("ABORTED", 0, "");
    throw new ApiError("NETWORK", 0, "");
  } finally {
    if (timer) clearTimeout(timer);
  }
}

export const api = {
  config: () => request<Config>("/config"),
  documents: () => request<DocumentList>("/documents"),
  deleteDocument: (id: string) => request<void>(`/documents/${id}`, { method: "DELETE" }),
  ask: (question: string, signal?: AbortSignal) =>
    request<Answer>("/questions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
      signal,
      timeoutMs: 45_000,
    }),
  fileUrl: (id: string, page?: number) => `${API}/documents/${id}/file${page ? `#page=${page}` : ""}`,
};

/** Tải lên bằng XHR để có tiến độ (fetch không báo tiến độ tải lên). */
export function uploadXhr(file: File, onProgress: (pct: number) => void): { promise: Promise<Doc>; abort: () => void } {
  const xhr = new XMLHttpRequest();
  const promise = new Promise<Doc>((resolve, reject) => {
    xhr.open("POST", `${API}/documents`);
    xhr.upload.onprogress = (e) => e.lengthComputable && onProgress(Math.round((e.loaded / e.total) * 100));
    xhr.onload = async () => {
      if (xhr.status === 202) return resolve(JSON.parse(xhr.responseText) as Doc);
      const res = new Response(xhr.responseText, {
        status: xhr.status,
        headers: { "Retry-After": xhr.getResponseHeader("Retry-After") ?? "" },
      });
      reject(await toError(res));
    };
    xhr.onerror = () => reject(new ApiError("NETWORK", 0, ""));
    xhr.onabort = () => reject(new ApiError("ABORTED", 0, ""));
    const fd = new FormData();
    fd.append("file", file);
    xhr.send(fd);
  });
  return { promise, abort: () => xhr.abort() };
}
