-- =====================================================================
-- "Chat với tài liệu" (MVP) — lược đồ PostgreSQL
-- Thiết kế: Database_Design.md (cùng thư mục). Phiên bản 0.1 (Draft), 2026-10-27.
--
-- Yêu cầu: PostgreSQL ≥ 13 (gen_random_uuid() có sẵn), tiện ích pgvector có HNSW.
-- Chưa chạy trên máy chủ PostgreSQL thật; mới được kiểm cú pháp bằng trình phân tích PostgreSQL.
-- Dùng làm nội dung migration đầu tiên (ví dụ Alembic revision 0001_init).
--
-- [TBD: OQ-S01] Số chiều vector (1536 bên dưới) phụ thuộc mô hình embedding.
-- [TBD: OQ-011] Cấu hình full-text 'simple' là mặc định tới khi chốt ngôn ngữ.
-- Không có bảng người dùng, phiên, hội thoại, nhật ký truy cập hay số liệu sử dụng (CON-005, BRD §5).
-- =====================================================================

CREATE EXTENSION IF NOT EXISTS vector;

-- ---------------------------------------------------------------------
-- documents: một dòng cho mỗi PDF đã được nhận (UC07, UC09, UC11, UC12)
-- ---------------------------------------------------------------------
CREATE TABLE documents (
    id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    name            text        NOT NULL,
    size_bytes      bigint      NOT NULL,
    page_count      int,
    storage_key     text        NOT NULL,
    content_sha256  char(64)    NOT NULL,
    status          text        NOT NULL,
    failure_reason  text,
    created_at      timestamptz NOT NULL DEFAULT now(),
    ready_at        timestamptz,
    deleted_at      timestamptz,

    CONSTRAINT documents_name_len     CHECK (char_length(name) BETWEEN 1 AND 255),
    CONSTRAINT documents_size_pos     CHECK (size_bytes > 0),
    CONSTRAINT documents_pages_pos    CHECK (page_count IS NULL OR page_count > 0),
    CONSTRAINT documents_key_format   CHECK (storage_key ~ '^documents/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.pdf$'),
    CONSTRAINT documents_sha_format   CHECK (content_sha256 ~ '^[0-9a-f]{64}$'),
    CONSTRAINT documents_status_enum  CHECK (status IN ('processing', 'ready', 'failed')),
    CONSTRAINT documents_reason_enum  CHECK (failure_reason IN ('FILE_CORRUPT', 'FILE_ENCRYPTED',
                                                                'NO_EXTRACTABLE_TEXT', 'PROCESSING_ERROR')),
    CONSTRAINT documents_failed_iff_reason CHECK ((status = 'failed') = (failure_reason IS NOT NULL)),
    CONSTRAINT documents_ready_iff_time    CHECK ((status = 'ready')  = (ready_at IS NOT NULL)),
    CONSTRAINT documents_storage_key_uq    UNIQUE (storage_key)
);

COMMENT ON TABLE  documents                 IS 'Tài liệu PDF trong kho dùng chung. Không có chủ sở hữu (CON-005).';
COMMENT ON COLUMN documents.name            IS 'Tên hiển thị, đã làm sạch từ tên tệp gốc. Không dùng để đặt khóa lưu trữ.';
COMMENT ON COLUMN documents.storage_key     IS 'Khóa đối tượng trong object storage: documents/{uuid}.pdf.';
COMMENT ON COLUMN documents.content_sha256  IS 'Băm nội dung; dùng cho ETag. Chưa chặn trùng (EC-12, OQ-014).';
COMMENT ON COLUMN documents.deleted_at      IS 'Xóa mềm: khác NULL = đã bị loại khỏi danh sách và truy xuất (BR-004).';

-- Danh sách tài liệu hiển thị (UC11)
CREATE INDEX documents_visible_idx ON documents (created_at DESC) WHERE deleted_at IS NULL;

-- ---------------------------------------------------------------------
-- chunks: đoạn văn bản có biên trang, vector và chỉ mục full-text (UC09, UC21)
-- Dữ liệu dẫn xuất: có thể dựng lại hoàn toàn từ PDF gốc.
-- ---------------------------------------------------------------------
CREATE TABLE chunks (
    id           uuid         PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id  uuid         NOT NULL REFERENCES documents (id) ON DELETE CASCADE,
    chunk_index  int          NOT NULL,
    page_start   int          NOT NULL,
    page_end     int          NOT NULL,
    text         text         NOT NULL,
    embedding    vector(1536) NOT NULL,
    tsv          tsvector     GENERATED ALWAYS AS (to_tsvector('simple', text)) STORED,

    CONSTRAINT chunks_index_nonneg CHECK (chunk_index >= 0),
    CONSTRAINT chunks_pages_ok     CHECK (page_start >= 1 AND page_start <= page_end),
    CONSTRAINT chunks_text_nonempty CHECK (char_length(text) > 0),
    CONSTRAINT chunks_doc_index_uq UNIQUE (document_id, chunk_index)
);

COMMENT ON TABLE  chunks            IS 'Đoạn văn bản của tài liệu. Nguồn hiển thị (tên, trang) lấy từ đây, không từ văn bản LLM (G-L3).';
COMMENT ON COLUMN chunks.embedding  IS 'Số chiều theo mô hình embedding [TBD: OQ-S01]. Đổi mô hình = dựng lại cột/bảng.';

-- Truy xuất vector (cosine). Xem Database_Design.md §3.4.5 về lọc sau chỉ mục xấp xỉ.
CREATE INDEX chunks_embedding_hnsw ON chunks USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
-- Truy xuất từ khóa
CREATE INDEX chunks_tsv_gin ON chunks USING gin (tsv);

-- ---------------------------------------------------------------------
-- jobs: hàng đợi việc nền trong CSDL (UC09, UC12)
-- document_id là tham chiếu logic, KHÔNG có khóa ngoại: purge_document xóa bản ghi documents
-- trong khi chính việc đó vẫn đang chạy.
-- ---------------------------------------------------------------------
CREATE TABLE jobs (
    id            uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    type          text        NOT NULL,
    document_id   uuid        NOT NULL,
    status        text        NOT NULL DEFAULT 'queued',
    attempts      int         NOT NULL DEFAULT 0,
    run_after     timestamptz NOT NULL DEFAULT now(),
    locked_until  timestamptz,
    last_error    text,
    request_id    text,
    created_at    timestamptz NOT NULL DEFAULT now(),
    finished_at   timestamptz,

    CONSTRAINT jobs_type_enum     CHECK (type IN ('process_document', 'purge_document')),
    CONSTRAINT jobs_status_enum   CHECK (status IN ('queued', 'running', 'done', 'failed')),
    CONSTRAINT jobs_attempts_nonneg CHECK (attempts >= 0),
    CONSTRAINT jobs_running_locked  CHECK (status <> 'running' OR locked_until IS NOT NULL)
);

COMMENT ON COLUMN jobs.last_error IS 'Chi tiết kỹ thuật; không bao giờ trả cho người dùng.';
COMMENT ON COLUMN jobs.request_id IS 'X-Request-Id của yêu cầu sinh ra việc; nối truy vết API → worker.';

-- Nhận việc: SELECT ... WHERE status = 'queued' AND run_after <= now() ORDER BY run_after FOR UPDATE SKIP LOCKED
CREATE INDEX jobs_queued_idx  ON jobs (run_after)    WHERE status = 'queued';
-- Quét việc quá hạn khóa
CREATE INDEX jobs_running_idx ON jobs (locked_until) WHERE status = 'running';
-- Dọn việc đã xong
CREATE INDEX jobs_finished_idx ON jobs (finished_at) WHERE status IN ('done', 'failed');
-- Tối đa một việc đang hoạt động cho mỗi (tài liệu, loại): enqueue lặp là vô hại (INSERT ... ON CONFLICT DO NOTHING)
CREATE UNIQUE INDEX jobs_active_uq ON jobs (document_id, type) WHERE status IN ('queued', 'running');

-- Việc có nhiều cập nhật/xóa: kích hoạt autovacuum sớm hơn mặc định
ALTER TABLE jobs SET (autovacuum_vacuum_scale_factor = 0.05, autovacuum_analyze_scale_factor = 0.05);

-- ---------------------------------------------------------------------
-- Phân quyền tối thiểu (Database_Design.md §4). Vai trò nhóm không đăng nhập;
-- vai trò đăng nhập theo môi trường được gán vào các vai trò này.
-- ---------------------------------------------------------------------
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'cwd_api') THEN
        CREATE ROLE cwd_api NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'cwd_worker') THEN
        CREATE ROLE cwd_worker NOLOGIN;
    END IF;
END
$$;

-- api: tạo tài liệu, xóa mềm, đọc để truy xuất, xếp việc
GRANT SELECT, INSERT ON documents TO cwd_api;
GRANT UPDATE (deleted_at) ON documents TO cwd_api;
GRANT SELECT ON chunks TO cwd_api;
GRANT INSERT ON jobs TO cwd_api;

-- worker: xử lý tài liệu, ghi/xóa đoạn, xóa vật lý, quản lý hàng đợi
GRANT SELECT, DELETE ON documents TO cwd_worker;
GRANT UPDATE (status, failure_reason, page_count, ready_at) ON documents TO cwd_worker;
GRANT SELECT, INSERT, DELETE ON chunks TO cwd_worker;
GRANT SELECT, INSERT, UPDATE, DELETE ON jobs TO cwd_worker;
