-- Copyright (c) 2026 ICTU-CRIS contributors
-- SPDX-License-Identifier: Apache-2.0

-- Lát cắt K1: học hàm (Giáo sư/Phó Giáo sư) tách khỏi học vị (degree_raw).
-- Nguồn ghi riêng ở archive.rank (cris/source/repository.py parse_gv, data-rank)
-- nhưng chưa có cột nào lưu lại — thêm ở đây; cris.people.import_people cập
-- nhật cột này (ngoại lệ tối thiểu, chỉ dòng vals, ngoài phạm vi K1 thường
-- không sửa tầng nghiệp vụ có sẵn).
ALTER TABLE person ADD COLUMN rank text;
