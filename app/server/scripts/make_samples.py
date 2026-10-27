"""Sinh bộ PDF MINH HỌA cho demo (dữ liệu giả, không phải tài liệu thật). Chạy: python scripts/make_samples.py ../samples"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tests.fixtures.pdfs import encrypted_pdf, text_pdf  # noqa: E402

DOCS = {
    "hop-dong-A.pdf": [
        "HỢP ĐỒNG MUA BÁN SỐ A-2026 (TÀI LIỆU MINH HỌA)\n\n"
        "Điều 1. Đối tượng hợp đồng. Bên bán cung cấp 500 bộ thiết bị đo cho bên mua.\n\n"
        "Điều 2. Giá trị hợp đồng. Tổng giá trị hợp đồng là 1,2 tỷ đồng, đã bao gồm thuế giá trị gia tăng.\n\n"
        "Điều 3. Điều khoản thanh toán. Bên mua thanh toán toàn bộ giá trị hợp đồng trong vòng 30 ngày kể từ "
        "ngày nhận hóa đơn hợp lệ. Phí phạt chậm thanh toán là 0,05% giá trị chậm trả cho mỗi ngày chậm.",
        "Điều 4. Thời hạn giao hàng. Bên bán giao hàng trong vòng 45 ngày kể từ ngày ký hợp đồng, tại kho của bên "
        "mua ở Bình Dương.\n\n"
        "Điều 5. Bảo hành. Thiết bị được bảo hành 12 tháng kể từ ngày nghiệm thu.\n\n"
        "Điều 6. Giải quyết tranh chấp. Tranh chấp được giải quyết tại Trung tâm Trọng tài Quốc tế Việt Nam.",
    ],
    "bao-gia-B.pdf": [
        "BÁO GIÁ SỐ B-17 (TÀI LIỆU MINH HỌA)\n\n"
        "Sản phẩm: thiết bị đo model M2. Đơn giá 2,3 triệu đồng mỗi bộ, chưa gồm thuế giá trị gia tăng.\n\n"
        "Điều khoản thanh toán: khách hàng trả trước 50% khi đặt hàng, phần còn lại thanh toán khi nhận hàng.\n\n"
        "Thời hạn giao hàng: 20 ngày làm việc kể từ khi nhận tiền đặt cọc.\n\n"
        "Báo giá có hiệu lực trong 15 ngày.",
    ],
    "quy-dinh-C.pdf": [
        "QUY ĐỊNH NỘI BỘ VỀ CÔNG TÁC PHÍ (TÀI LIỆU MINH HỌA)\n\n"
        "Mục 1. Nhân viên đi công tác được thanh toán chi phí đi lại theo hóa đơn thực tế.\n\n"
        "Mục 2. Phụ cấp lưu trú là 400 nghìn đồng mỗi ngày đối với công tác trong nước.\n\n"
        "Mục 3. Hồ sơ thanh toán công tác phí phải nộp cho phòng kế toán trong vòng 10 ngày sau chuyến công tác.",
    ],
}


def main(out: str) -> None:
    d = Path(out)
    d.mkdir(parents=True, exist_ok=True)
    for name, pages in DOCS.items():
        (d / name).write_bytes(text_pdf(pages))
    (d / "co-mat-khau.pdf").write_bytes(encrypted_pdf())
    (d / "khong-phai-pdf.txt").write_text("Tệp này không phải PDF — dùng để thử thông báo từ chối.\n", encoding="utf-8")
    print("\n".join(sorted(p.name for p in d.iterdir())))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "samples")
