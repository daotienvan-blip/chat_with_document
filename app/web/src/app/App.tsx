import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api-client/client";
import { Icon } from "../components/Icon";
import { ChatPanel } from "../features/chat/ChatPanel";
import { DocumentsPanel, useDocuments } from "../features/documents/documents";

// Vị trí lưu trữ thật chờ OQ-005; chuỗi này đổi qua biến build VITE_STORAGE_LOCATION.
const STORAGE_LOCATION = import.meta.env.VITE_STORAGE_LOCATION ?? "[vị trí lưu trữ — chờ OQ-005]";

export function App() {
  const config = useQuery({ queryKey: ["config"], queryFn: api.config, staleTime: Infinity });
  const docs = useDocuments(config.data);
  const items = docs.data?.items;
  const hasReady = !!items?.some((d) => d.status === "ready");
  const liveIds = useMemo(() => (items ? new Set(items.map((d) => d.id)) : undefined), [items]);

  return (
    <>
      <a className="skip" href="#q">Bỏ qua tới khung hỏi đáp</a>
      <header className="app-header">
        <span className="logo"><Icon name="chat" /></span>
        <h1>Chat với tài liệu</h1>
        <span className="tag">MVP</span>
      </header>
      <div className="notice" role="note">
        <Icon name="info" />
        <p>
          <strong>Lưu ý về dữ liệu:</strong> tài liệu được lưu tại <em>{STORAGE_LOCATION}</em> và{" "}
          <strong>mọi người dùng ứng dụng này đều xem được tất cả tài liệu</strong>. Chỉ tải tài liệu mà mọi người được phép xem.
          Luôn kiểm chứng nguồn trước khi dùng câu trả lời.
        </p>
      </div>
      <main className="layout">
        <DocumentsPanel config={config.data} docs={docs} />
        <ChatPanel config={config.data} enabled={hasReady} liveIds={liveIds} />
      </main>
    </>
  );
}
