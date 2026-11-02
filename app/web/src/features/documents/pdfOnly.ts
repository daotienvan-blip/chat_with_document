// Kiểm tra loại tệp trước khi tải lên (US-001-AC3). Máy chủ vẫn kiểm lại, kể cả nội dung tệp (S1-05).
export const PDF_ONLY_MESSAGE = "Please upload pdf file only";

/** Đuôi `.pdf` và, nếu trình duyệt có báo, loại nội dung là `application/pdf` (kéo thả có thể bỏ qua `accept` của ô chọn tệp). */
export function isPdfFile(f: File): boolean {
  return f.name.toLowerCase().endsWith(".pdf") && (f.type === "" || f.type === "application/pdf");
}
