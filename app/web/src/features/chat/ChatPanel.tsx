// Khung hỏi đáp (S3-06, S5-02, S7-03): gửi, chờ, ba loại phản hồi, lỗi có thể thử lại, cuộc trao đổi mới.
import { useEffect, useRef, useState } from "react";
import { api, ApiError, type Answer, type Config } from "../../api-client/client";
import { toUiError, type UiError } from "../../api-client/uiErrors";
import { Icon } from "../../components/Icon";
import { clearTurns, loadTurns, saveTurns, type Turn } from "../../state/conversation";
import { SourceChip } from "../sources/SourceChip";

function AnswerCard({ answer, liveIds }: { answer: Answer; liveIds?: Set<string> }) {
  const sources = (
    answer.sources.length > 0 && (
      <div className="sources">
        <span className="sources__label">Nguồn</span>
        {answer.sources.map((s) => (
          <SourceChip key={s.documentId} source={s} gone={liveIds ? !liveIds.has(s.documentId) : false} />
        ))}
      </div>
    )
  );
  if (answer.status === "not_found") {
    return (
      <article className="a a--notfound" aria-label="Không tìm thấy thông tin">
        <div className="a__label"><Icon name="none" /> Không tìm thấy thông tin</div>
        <p className="a__text">{answer.answer}</p>
        <p className="hint">Thử đặt lại câu hỏi bằng từ khóa khác, hoặc tải thêm tài liệu liên quan.</p>
      </article>
    );
  }
  if (answer.status === "partial") {
    return (
      <article className="a a--partial" aria-label="Câu trả lời một phần">
        <div className="a__label"><Icon name="half" fill /> Trả lời một phần</div>
        <p className="a__text">{answer.answer}</p>
        <div className="missing"><Icon name="warn" /><span>Một phần câu hỏi không có trong các tài liệu đã tải.</span></div>
        {sources}
      </article>
    );
  }
  return (
    <article className="a a--answered" aria-label="Câu trả lời có căn cứ">
      <div className="a__label"><Icon name="check" /> Có căn cứ từ tài liệu</div>
      <p className="a__text">{answer.answer}</p>
      {sources}
    </article>
  );
}

function ErrorCard({ error, onRetry, onEdit }: { error: UiError; onRetry: () => void; onEdit: () => void }) {
  const [wait, setWait] = useState(error.retryAfter && error.retryable ? error.retryAfter : 0);
  useEffect(() => {
    if (wait <= 0) return;
    const t = setTimeout(() => setWait((w) => w - 1), 1000);
    return () => clearTimeout(t);
  }, [wait]);
  return (
    <article className="a a--error" aria-label={`Lỗi: ${error.title}`}>
      <div className="a__label" role="alert"><Icon name="warn" /> {error.title}</div>
      <p className="a__text">{error.message}</p>
      <div className="alert__actions">
        {error.retryable && (
          <button type="button" className="btn btn--sm btn--primary" disabled={wait > 0} onClick={onRetry}>
            <Icon name="refresh" /> {wait > 0 ? `Gửi lại sau ${wait} giây` : "Gửi lại"}
          </button>
        )}
        <button type="button" className="btn btn--sm" onClick={onEdit}>Sửa câu hỏi</button>
      </div>
    </article>
  );
}

export function ChatPanel({ config, enabled, liveIds }: { config?: Config; enabled: boolean; liveIds?: Set<string> }) {
  const [turns, setTurns] = useState<Turn[]>(() => loadTurns());
  const [q, setQ] = useState("");
  const [fieldErr, setFieldErr] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const qRef = useRef<HTMLTextAreaElement>(null);
  const logRef = useRef<HTMLDivElement>(null);
  const sending = turns.some((t) => t.state === "sending");
  const limit = config?.maxQuestionLength ?? null;

  useEffect(() => saveTurns(turns), [turns]);
  useEffect(() => {
    logRef.current?.scrollTo?.({ top: logRef.current.scrollHeight });
  }, [turns]);

  const ask = async (question: string, turnId?: string) => {
    const id = turnId ?? `t${Date.now()}`;
    setTurns((ts) => (turnId ? ts.map((t) => (t.id === id ? { ...t, state: "sending", error: undefined } : t)) : [...ts, { id, question, state: "sending" }]));
    const ctrl = new AbortController();
    abortRef.current = ctrl;
    try {
      const answer = await api.ask(question, ctrl.signal);
      setTurns((ts) => ts.map((t) => (t.id === id ? { ...t, state: "done", answer } : t)));
      setQ((cur) => (cur === question ? "" : cur));
    } catch (e) {
      if (e instanceof ApiError && e.code === "ABORTED") {
        setTurns((ts) => ts.filter((t) => t.id !== id));
        return;
      }
      const ui = toUiError(e);
      if (ui.fieldError) {
        setTurns((ts) => ts.filter((t) => t.id !== id));
        setFieldErr(ui.message);
        return;
      }
      setTurns((ts) => ts.map((t) => (t.id === id ? { ...t, state: "error", error: ui } : t)));
    } finally {
      abortRef.current = null;
    }
  };

  const submit = () => {
    const question = q.trim();
    if (!question || sending || !enabled) return; // EC-08: không gửi khi rỗng
    if (limit && question.length > limit) return setFieldErr(`Câu hỏi dài hơn ${limit} ký tự. Hãy rút gọn trước khi gửi.`);
    setFieldErr(null);
    void ask(question);
  };

  const tooLong = limit !== null && q.length > limit;
  return (
    <section className="panel chat" aria-labelledby="h-chat">
      <div className="panel__head">
        <h2 id="h-chat">Cuộc trao đổi</h2>
        <button type="button" className="btn btn--sm" disabled={turns.length === 0 || sending}
          onClick={() => { setTurns([]); clearTurns(); qRef.current?.focus(); }}>
          <Icon name="refresh" /> Cuộc trao đổi mới
        </button>
      </div>
      <div className="log" ref={logRef} role="log" aria-live="polite" tabIndex={0} aria-label="Nội dung cuộc trao đổi">
        {!enabled && turns.length === 0 && (
          <div className="empty">
            <Icon name="chat" />
            <h3>Hãy tải tài liệu trước</h3>
            <p>Khung hỏi sẽ mở khi có ít nhất một tài liệu ở trạng thái <strong>Sẵn sàng</strong>.</p>
          </div>
        )}
        {enabled && turns.length === 0 && (
          <p className="hint">Đặt câu hỏi về nội dung các tài liệu đã tải. Ví dụ: “Điều khoản thanh toán là gì?” Mỗi câu hỏi được trả lời độc lập.</p>
        )}
        {turns.map((t) => (
          <div className="turn" key={t.id}>
            <div className="q">{t.question}</div>
            {t.state === "sending" && (
              <div className="a" style={{ borderLeftColor: "var(--info-fg)" }} aria-label="Đang xử lý câu hỏi">
                <div className="typing" role="status"><Icon name="spinner" spin /> <span>Đang tìm trong các tài liệu…</span></div>
              </div>
            )}
            {t.state === "done" && t.answer && <AnswerCard answer={t.answer} liveIds={liveIds} />}
            {t.state === "error" && t.error && (
              <ErrorCard error={t.error} onRetry={() => void ask(t.question, t.id)}
                onEdit={() => { setQ(t.question); setTurns((ts) => ts.filter((x) => x.id !== t.id)); qRef.current?.focus(); }} />
            )}
          </div>
        ))}
      </div>
      <form className="composer" onSubmit={(e) => { e.preventDefault(); submit(); }} aria-label="Đặt câu hỏi">
        <label htmlFor="q">Câu hỏi của bạn</label>
        <textarea id="q" ref={qRef} className="field" rows={3} value={q} disabled={!enabled}
          placeholder={enabled ? "Ví dụ: Điều khoản thanh toán là gì?" : "Hãy tải ít nhất một tài liệu trước khi đặt câu hỏi"}
          aria-invalid={tooLong || !!fieldErr || undefined} aria-describedby={fieldErr || tooLong ? "q-err" : undefined}
          onChange={(e) => { setQ(e.target.value); setFieldErr(null); }}
          onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); submit(); } }} />
        {(fieldErr || tooLong) && (
          <p className="field-err" id="q-err" role="alert"><Icon name="warn" /><span>{fieldErr ?? `Câu hỏi dài hơn ${limit} ký tự. Hãy rút gọn trước khi gửi.`}</span></p>
        )}
        <div className="composer__row">
          <span className={`counter${tooLong ? " counter--bad" : ""}`}>{q.length}{limit ? ` / ${limit}` : " ký tự"}</span>
          <span style={{ display: "flex", gap: 8 }}>
            {sending && <button type="button" className="btn" onClick={() => abortRef.current?.abort()}><Icon name="x" /> Hủy</button>}
            <button type="submit" className="btn btn--primary" disabled={!enabled || sending || !q.trim() || tooLong}>
              {sending ? <><Icon name="spinner" spin /> Đang gửi…</> : <><Icon name="send" /> Gửi</>}
            </button>
          </span>
        </div>
        <p className="hint">Nhấn Enter để gửi, Shift+Enter để xuống dòng. Luôn kiểm chứng nguồn trước khi dùng câu trả lời.</p>
      </form>
    </section>
  );
}
