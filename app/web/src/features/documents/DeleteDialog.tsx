// Hộp thoại xác nhận xóa (S6-03, SCR-04): focus vào Hủy, bẫy Tab, Esc = Hủy (trừ khi đang xóa).
import { useEffect, useRef, useState } from "react";
import { api, ApiError, type Doc } from "../../api-client/client";
import { Icon } from "../../components/Icon";

export function DeleteDialog({ doc, onClose, onDeleted }: { doc: Doc; onClose: () => void; onDeleted: () => void }) {
  const [state, setState] = useState<"idle" | "deleting" | "error">("idle");
  const cancelRef = useRef<HTMLButtonElement>(null);
  const boxRef = useRef<HTMLDivElement>(null);

  useEffect(() => cancelRef.current?.focus(), []);

  const confirm = async () => {
    setState("deleting");
    try {
      await api.deleteDocument(doc.id);
      onDeleted();
    } catch (e) {
      if (e instanceof ApiError && e.status === 404) return onDeleted(); // đã bị xóa: coi như xong
      setState("error");
    }
  };

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Escape") {
      e.preventDefault();
      if (state !== "deleting") onClose();
      return;
    }
    if (e.key !== "Tab" || !boxRef.current) return;
    const f = Array.from(boxRef.current.querySelectorAll<HTMLElement>("button:not([disabled])"));
    if (!f.length) return;
    const first = f[0], last = f[f.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  };

  const busy = state === "deleting";
  return (
    <div className="backdrop" role="presentation" onKeyDown={onKeyDown}>
      <div className="dialog" role="alertdialog" aria-modal="true" aria-labelledby="dlg-title" aria-describedby="dlg-desc" ref={boxRef}>
        <div className="dialog__head">
          <span className="dialog__icon"><Icon name="trash" /></span>
          <h2 id="dlg-title">Xóa tài liệu “{doc.name}”?</h2>
        </div>
        <div className="dialog__body" id="dlg-desc">
          <p>Tài liệu sẽ bị gỡ khỏi kho dùng chung <strong>ngay</strong> và không còn được dùng để trả lời. Mọi người dùng ứng dụng đều không còn thấy tài liệu này.</p>
          <p>Thao tác này <strong>không thể hoàn tác</strong>. Các câu trả lời đã hiển thị được giữ nguyên, nhưng nguồn từ tài liệu này sẽ được đánh dấu “(đã xóa)”.</p>
        </div>
        {busy && <div className="alert alert--info" role="status"><Icon name="spinner" spin /><div className="alert__body">Đang xóa…</div></div>}
        {state === "error" && (
          <div className="alert alert--danger" role="alert">
            <Icon name="warn" />
            <div className="alert__body"><span className="alert__title">Chưa xóa được tài liệu.</span> Hệ thống đang bận hoặc mất kết nối. Tài liệu vẫn còn nguyên.</div>
          </div>
        )}
        <div className="dialog__foot">
          <button type="button" className="btn" ref={cancelRef} onClick={onClose} disabled={busy}>Hủy</button>
          <button type="button" className="btn btn--danger" onClick={confirm} disabled={busy}>
            <Icon name="trash" /> {state === "error" ? "Thử xóa lại" : "Xóa tài liệu"}
          </button>
        </div>
      </div>
    </div>
  );
}
