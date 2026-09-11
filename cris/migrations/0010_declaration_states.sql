-- Copyright (c) 2026 ICTU-CRIS contributors
-- SPDX-License-Identifier: Apache-2.0

-- Quy trình kê khai hai cấp theo docs/ba/03-state.md §3.2 (lát cắt H1): mở
-- CHECK trạng thái declaration từ bộ rút gọn (Nhap/ChoBoSung/Rut) sang đủ 8
-- trạng thái của quy trình khoa duyệt → phòng kiểm tra → chốt.
ALTER TABLE declaration DROP CONSTRAINT declaration_state_check;
ALTER TABLE declaration ADD CONSTRAINT declaration_state_check
  CHECK (state IN ('Nhap','ChoBoSung','ChoKhoaDuyet','KhoaDaDuyet','ChoPhongKiemTra','DatYeuCau','DaChot','Rut'));
