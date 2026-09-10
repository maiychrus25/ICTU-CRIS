# Thông báo giấy phép (License Notice)

Tài liệu này giải thích lý do chọn giấy phép, ma trận tương thích với các thư
viện/dịch vụ đang dùng, quy định header bản quyền cho từng tệp, và phạm vi áp
dụng của giấy phép đối với dữ liệu.

## 1. Mục đích chọn Apache-2.0 (Why Apache-2.0)

Dự án ICTU-CRIS phát hành theo giấy phép Apache-2.0 (toàn văn tại `LICENSE`,
chủ sở hữu bản quyền: ICTU-CRIS contributors) vì các lý do sau:

- **Cho phép trường, đơn vị khác dùng và sửa**: Apache-2.0 cho phép các
  trường đại học hoặc đơn vị khác tái sử dụng, sửa đổi và triển khai lại mã
  nguồn, kể cả khi tích hợp vào dịch vụ nội bộ không phát hành ra ngoài
  (không có điều khoản "network copyleft" như AGPL).
- **Có điều khoản cấp quyền bằng sáng chế (patent grant)**: Apache-2.0 cấp
  quyền sáng chế tường minh từ người đóng góp cho người dùng, giảm rủi ro
  tranh chấp sáng chế khi các trường/đơn vị khác sử dụng lại mã nguồn.
- **Yêu cầu giữ NOTICE**: bản phân phối lại (kể cả bản sửa đổi) phải giữ
  nguyên thông báo bản quyền, giấy phép, và tệp `NOTICE` (nếu có), đảm bảo
  ghi công tác giả gốc được duy trì qua các lần fork/tái phân phối.
- **Tương thích rộng với thư viện**: Apache-2.0 tương thích với phần lớn
  giấy phép mã nguồn mở phổ biến (MIT, BSD, PostgreSQL License) và với thư
  viện LGPL dùng ở dạng thư viện không sửa đổi (xem ma trận bên dưới), nên
  không giới hạn việc chọn thư viện trong tương lai.

## 2. Ma trận tương thích (Compatibility Matrix)

| Thành phần | Giấy phép | Cách sử dụng | Tương thích với Apache-2.0 |
|---|---|---|---|
| `psycopg` 3 | LGPL-3.0-or-later | Dùng như thư viện (import qua PyPI), không sửa mã nguồn | Có — LGPL cho phép liên kết động/import không sửa đổi mà không áp đặt giấy phép lên mã gọi nó |
| PostgreSQL 16 | PostgreSQL License | Dịch vụ ngoài (chạy qua image `postgres:16`), không nhúng mã vào repo | Có — PostgreSQL License tương tự MIT/BSD, cho phép mọi mục đích sử dụng |
| `pytest` | MIT | Chỉ dùng khi phát triển (`dev` dependency), không phân phối cùng sản phẩm | Có — MIT tương thích hoàn toàn với Apache-2.0 |
| Docker (Docker CE) | Apache-2.0 | Công cụ đóng gói/chạy môi trường (toolchain), không nhúng mã vào repo | Có — cùng giấy phép |
| Python 3.12 (CPython) | PSF License | Toolchain/runtime | Có — PSF License cho phép sử dụng, sửa đổi, phân phối tự do |
| Bộ sách DX-OS (opendigitransform.gitbook.io/dx-os) | CC BY 4.0 | Chỉ trích dẫn làm tài liệu tham khảo phương pháp luận trong tài liệu dự án, không sao chép nội dung | Có — chỉ cần ghi công tác giả (attribution) khi trích dẫn, không áp dụng lên mã nguồn |

## 3. Quy định header từng tệp (Per-file Header)

Mỗi tệp mã nguồn có phần mở rộng `.py`, `.sql`, `.sh`, `.yml`, `.yaml` phải
có hai dòng header ở đầu tệp — dùng `--` cho `.sql`, `#` cho các loại còn
lại:

```
Copyright (c) 2026 ICTU-CRIS contributors
SPDX-License-Identifier: Apache-2.0
```

Ví dụ áp dụng theo cú pháp comment của từng loại tệp:

**Tệp `.py`:**

```python
# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
```

**Tệp `.sql`:**

```sql
-- Copyright (c) 2026 ICTU-CRIS contributors
-- SPDX-License-Identifier: Apache-2.0
```

Việc thiếu header ở tệp mã nguồn được chặn tự động bởi test
`tests/test_spdx.py`, chạy như một phần của bộ kiểm thử (`pytest -v`) và
trong CI (`.github/workflows/ci.yml`).

## 4. Dữ liệu (Data)

Giấy phép Apache-2.0 của dự án áp dụng cho **mã nguồn**, không áp dụng cho
**dữ liệu**:

- Dữ liệu thô kéo từ kho công khai của trường (repository.ictu.edu.vn) không
  thuộc phạm vi giấy phép này — quyền sở hữu và điều khoản sử dụng dữ liệu đó
  do trường quyết định.
- Fixture kiểm thử trong `tests/fixtures/` đã ẩn danh thông tin cá nhân
  giảng viên (tên, email, điện thoại, ngày sinh), phục vụ mục đích kiểm thử
  tự động; tên tác giả trên fixture bài báo là dữ liệu thư mục công khai.
- Dữ liệu thật (kết quả thu thập từ `khao-sat-nguon/`) nằm ngoài repo, được
  loại trừ qua `.gitignore`, không bao giờ được đẩy lên Git.
