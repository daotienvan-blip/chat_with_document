// Panel "Tài liệu" (S1-04, S1-05, S2-06, S6-03): danh sách, trạng thái, polling, tải lên, xóa.
import { useEffect, useRef, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api, ApiError, uploadXhr, type Config, type Doc } from "../../api-client/client";
import { FAILURE_MESSAGES, toUiError } from "../../api-client/uiErrors";
import { Icon } from "../../components/Icon";
import { DeleteDialog } from "./DeleteDialog";

const MAX_BACKOFF = 30_000;

/** Chỉ poll khi còn tài liệu `processing`; lùi gấp đôi sau 429/503; tạm dừng khi thẻ ẩn (API_Design §3.7.3). */
export function useDocuments(config: Config | undefined) {
  const backoff = useRef(0);
  return useQuery({
    queryKey: ["documents"],
    queryFn: async () => {
      try {
        const r = await api.documents();
        backoff.current = 0;
        return r;
      } catch (e) {
        if (e instanceof ApiError && (e.status === 429 || e.status === 503)) {
          const base = Math.max(backoff.current * 2, (config?.pollIntervalMs ?? 2000) * 2);
          backoff.current = Math.min(MAX_BACKOFF, Math.max(base, (e.retryAfter ?? 0) * 1000));
        }
        throw e;
      }
    },
    refetchInterval: (q) => {
      const items = q.state.data?.items ?? [];
      if (!items.some((d) => d.status === "processing") && !backoff.current) return false;
      return backoff.current || config?.pollIntervalMs || 2000;
    },
    refetchIntervalInBackground: false,
  });
}

function formatSize(n: number) {
  return n >= 1024 * 1024 ? `${(n / 1024 / 1024).toFixed(1).replace(".", ",")} MB` : `${Math.max(1, Math.round(n / 1024))} KB`;
}

export function StatusBadge({ status }: { status: Doc["status"] | "uploading" | "upload-failed" }) {
  switch (status) {
    case "ready":
      return <span className="badge badge--ready"><Icon name="check" /> Sẵn sàng</span>;
    case "processing":
      return <span className="badge badge--proc"><Icon name="spinner" spin /> Đang xử lý</span>;
    case "failed":
      return <span className="badge badge--fail"><Icon name="x" /> Lỗi</span>;
    case "uploading":
      return <span className="badge badge--proc"><Icon name="upload" /> Đang tải lên</span>;
    default:
      return <span className="badge badge--wait"><Icon name="offline" /> Chưa tải được</span>;
  }
}

function DocumentRow({ doc, justReady, onDelete }: { doc: Doc; justReady: boolean; onDelete: (d: Doc, btn: HTMLButtonElement) => void }) {
  const fail = doc.failureReason ? FAILURE_MESSAGES[doc.failureReason] : undefined;
  const meta = [formatSize(doc.sizeBytes), doc.pageCount ? `${doc.pageCount} trang` : doc.status === "processing" ? "đang đọc trang…" : null]
    .filter(Boolean)
    .join(" · ");
  return (
    <li className={`doc${doc.status === "failed" ? " doc--failed" : ""}`} data-testid="doc-row">
      <span className="doc__icon"><Icon name="file" /></span>
      <span className="doc__name" title={doc.name}>{doc.name}</span>
      <span className="doc__actions">
        <button type="button" className="icon-btn" aria-label={`Xóa tài liệu ${doc.name}`} onClick={(e) => onDelete(doc, e.currentTarget)}>
          <Icon name="trash" />
        </button>
      </span>
      <span className="doc__meta">{meta}</span>
      <span className="doc__status">
        <StatusBadge status={doc.status} />
        {doc.status === "processing" && <span className="hint" style={{ marginLeft: 8 }}>chưa dùng để trả lời</span>}
      </span>
      {justReady && (
        <div className="doc__msg" role="status">
          <div className="alert alert--success"><Icon name="check" /><div className="alert__body">Tài liệu đã sẵn sàng để hỏi.</div></div>
        </div>
      )}
      {fail && (
        <div className="doc__msg">
          <div className="alert alert--danger" role="alert">
            <Icon name="warn" />
            <div className="alert__body"><span className="alert__title">{fail[0]}</span> {fail[1]}</div>
          </div>
        </div>
      )}
    </li>
  );
}

interface Pending {
  key: string;
  file: File;
  progress: number;
  state: "uploading" | "failed";
  message?: string;
  abort?: () => void;
}

export function DocumentsPanel({ config, docs }: { config?: Config; docs: ReturnType<typeof useDocuments> }) {
  const qc = useQueryClient();
  const fileInput = useRef<HTMLInputElement>(null);
  const [over, setOver] = useState(false);
  const [rejected, setRejected] = useState<string[]>([]);
  const [pending, setPending] = useState<Pending[]>([]);
  const [toDelete, setToDelete] = useState<{ doc: Doc; opener: HTMLButtonElement } | null>(null);
  const prevStatus = useRef<Record<string, string>>({});
  const [justReady, setJustReady] = useState<Set<string>>(new Set());

  const items = docs.data?.items ?? [];
  useEffect(() => {
    const now = new Set<string>();
    for (const d of items) {
      if (prevStatus.current[d.id] === "processing" && d.status === "ready") now.add(d.id);
      prevStatus.current[d.id] = d.status;
    }
    if (now.size) setJustReady((s) => new Set([...s, ...now]));
  }, [items]);

  const startUpload = (file: File, key = `${file.name}-${Date.now()}-${Math.random()}`) => {
    const { promise, abort } = uploadXhr(file, (progress) =>
      setPending((ps) => ps.map((p) => (p.key === key ? { ...p, progress } : p))),
    );
    setPending((ps) => [...ps.filter((p) => p.key !== key), { key, file, progress: 0, state: "uploading", abort }]);
    promise
      .then(() => {
        setPending((ps) => ps.filter((p) => p.key !== key));
        qc.invalidateQueries({ queryKey: ["documents"] });
      })
      .catch((e: ApiError) => {
        if (e.code === "ABORTED") return setPending((ps) => ps.filter((p) => p.key !== key));
        const ui = toUiError(e);
        if (e.code === "UNSUPPORTED_TYPE" || e.code === "FILE_TOO_LARGE" || e.code === "INVALID_REQUEST") {
          setPending((ps) => ps.filter((p) => p.key !== key));
          setRejected((r) => [...r, `${file.name}: ${ui.message}`]);
        } else {
          const msg = e.code === "NETWORK" ? "Mất kết nối khi đang tải lên. Chưa có tài liệu nào được tạo." : ui.message;
          setPending((ps) => ps.map((p) => (p.key === key ? { ...p, state: "failed", message: msg } : p)));
        }
      });
  };

  const accept = (files: FileList | null) => {
    if (!files) return;
    const errs: string[] = [];
    for (const f of Array.from(files)) {
      // Kiểm tra trước ở trình duyệt; máy chủ vẫn là nơi quyết định (S1-05).
      if (!f.name.toLowerCase().endsWith(".pdf")) errs.push(`${f.name}: Chỉ hỗ trợ tệp PDF.`);
      else if (config?.maxFileSizeMb && f.size > config.maxFileSizeMb * 1024 * 1024)
        errs.push(`${f.name}: Tệp lớn hơn giới hạn ${config.maxFileSizeMb} MB.`);
      else startUpload(f);
    }
    setRejected(errs);
  };

  return (
    <section className="panel" aria-labelledby="h-docs">
      <div className="panel__head"><h2 id="h-docs">Tài liệu</h2>{items.length > 0 && <span className="tag">{items.length}</span>}</div>
      <div className="panel__body">
        <div
          className={`drop${over ? " drop--over" : ""}`}
          onDragEnter={(e) => { e.preventDefault(); setOver(true); }}
          onDragOver={(e) => { e.preventDefault(); setOver(true); }}
          onDragLeave={(e) => { e.preventDefault(); setOver(false); }}
          onDrop={(e) => { e.preventDefault(); setOver(false); accept(e.dataTransfer.files); }}
        >
          <Icon name="upload" />
          <p>
            Chỉ hỗ trợ tệp PDF có văn bản
            {config?.maxFileSizeMb ? <>, tối đa <strong>{config.maxFileSizeMb} MB</strong> mỗi tệp</> : null}.
          </p>
          <input ref={fileInput} type="file" accept="application/pdf,.pdf" multiple className="sr-only" aria-label="Chọn tệp PDF"
            onChange={(e) => { accept(e.target.files); e.target.value = ""; }} />
          <button type="button" className="btn btn--primary" onClick={() => fileInput.current?.click()}>
            <Icon name="plus" /> Tải PDF lên
          </button>
          <p>Hoặc kéo thả tệp vào đây.</p>
        </div>
        {rejected.map((r) => (
          <div key={r} className="alert alert--danger" role="alert" style={{ marginTop: 8 }}>
            <Icon name="warn" /><div className="alert__body"><span className="alert__title">{r}</span></div>
          </div>
        ))}
        {docs.isError && (
          <div className="alert alert--warn" role="alert" style={{ marginTop: 12 }}>
            <Icon name="warn" />
            <div className="alert__body">
              Chưa tải được danh sách tài liệu.
              <div className="alert__actions"><button type="button" className="btn btn--sm" onClick={() => docs.refetch()}>Thử lại</button></div>
            </div>
          </div>
        )}
        {docs.isLoading && <p className="hint" role="status">Đang tải danh sách…</p>}
        {!docs.isLoading && items.length === 0 && pending.length === 0 && !docs.isError && (
          <div className="empty">
            <Icon name="doc" />
            <h3>Chưa có tài liệu nào</h3>
            <p>Tải lên một hoặc nhiều tệp PDF để bắt đầu hỏi đáp.</p>
          </div>
        )}
        <ul className="doc-list" aria-label="Danh sách tài liệu">
          {pending.map((p) => (
            <li key={p.key} className="doc">
              <span className="doc__icon"><Icon name="file" /></span>
              <span className="doc__name" title={p.file.name}>{p.file.name}</span>
              <span className="doc__actions">
                {p.state === "uploading" && <button type="button" className="btn btn--sm" onClick={() => p.abort?.()}><Icon name="x" /> Hủy</button>}
              </span>
              <span className="doc__meta">{formatSize(p.file.size)}</span>
              <span className="doc__status"><StatusBadge status={p.state === "uploading" ? "uploading" : "upload-failed"} /></span>
              {p.state === "uploading" ? (
                <div className="doc__msg">
                  <div className="bar" role="progressbar" aria-label={`Tiến độ tải ${p.file.name}`} aria-valuemin={0} aria-valuemax={100} aria-valuenow={p.progress}>
                    <i style={{ width: `${p.progress}%` }} />
                  </div>
                </div>
              ) : (
                <div className="doc__msg">
                  <div className="alert alert--warn" role="alert">
                    <Icon name="offline" />
                    <div className="alert__body">
                      <span className="alert__title">{p.message}</span>
                      <div className="alert__actions">
                        <button type="button" className="btn btn--sm btn--primary" onClick={() => startUpload(p.file, p.key)}><Icon name="refresh" /> Thử lại</button>
                        <button type="button" className="btn btn--sm" onClick={() => setPending((ps) => ps.filter((x) => x.key !== p.key))}>Bỏ qua</button>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </li>
          ))}
          {items.map((d) => (
            <DocumentRow key={d.id} doc={d} justReady={justReady.has(d.id) && d.status === "ready"} onDelete={(doc, opener) => setToDelete({ doc, opener })} />
          ))}
        </ul>
      </div>
      {toDelete && (
        <DeleteDialog
          doc={toDelete.doc}
          onClose={() => { const o = toDelete.opener; setToDelete(null); setTimeout(() => o.isConnected ? o.focus() : document.getElementById("h-docs")?.focus(), 0); }}
          onDeleted={() => { setToDelete(null); qc.invalidateQueries({ queryKey: ["documents"] }); }}
        />
      )}
    </section>
  );
}
