// Chip nguồn (S4-03): ngay dưới câu trả lời, mở PDF ở thẻ mới tại trang đầu. Đã xóa ⇒ không bấm được.
import { api, type Source } from "../../api-client/client";
import { Icon } from "../../components/Icon";

export function SourceChip({ source, gone }: { source: Source; gone?: boolean }) {
  if (gone) {
    return (
      <span className="chip chip--gone" aria-disabled="true" title="Tài liệu đã bị xóa">
        <Icon name="file" /> {source.documentName} <span>(đã xóa)</span>
      </span>
    );
  }
  const pages = source.pages.length ? `tr. ${source.pages.join(", ")}` : "";
  return (
    <a className="chip" href={api.fileUrl(source.documentId, source.pages[0])} target="_blank" rel="noopener"
      aria-label={`Mở ${source.documentName}${pages ? `, ${pages}` : ""} trong thẻ mới`}>
      <Icon name="file" /> {source.documentName}{pages ? ` · ${pages}` : ""} <Icon name="ext" />
    </a>
  );
}
