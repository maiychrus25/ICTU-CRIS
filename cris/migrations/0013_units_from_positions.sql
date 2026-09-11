-- Copyright (c) 2026 ICTU-CRIS contributors
-- SPDX-License-Identifier: Apache-2.0
-- `jobTitle` ở kho nguồn là chức vụ ("Hiệu trưởng", "Hiệu phó", "Trưởng khoa"), từng bị
-- nhập thành đơn vị. Gom hiệu trưởng/hiệu phó về đơn vị thật "Ban Giám hiệu" (giữ id của
-- đơn vị HIEUTRUONG để hồ sơ kê khai/tài khoản đã trỏ tới nó không đổi); "Trưởng khoa"
-- không phải đơn vị → bỏ gán và tắt.
UPDATE unit SET code='BGH', name='Ban Giám hiệu',
       aliases = ARRAY['Hiệu trưởng','Hiệu phó','Phó Hiệu trưởng']
WHERE code='HIEUTRUONG';
UPDATE person SET unit_id=(SELECT id FROM unit WHERE code='BGH')
WHERE unit_id IN (SELECT id FROM unit WHERE code='HIEUPHO');
UPDATE app_user SET unit_id=(SELECT id FROM unit WHERE code='BGH')
WHERE unit_id IN (SELECT id FROM unit WHERE code='HIEUPHO');
UPDATE declaration SET unit_id=(SELECT id FROM unit WHERE code='BGH')
WHERE unit_id IN (SELECT id FROM unit WHERE code='HIEUPHO');
UPDATE person SET unit_id=NULL WHERE unit_id IN (SELECT id FROM unit WHERE code='TRUONGKHOA');
UPDATE unit SET active=false WHERE code IN ('HIEUPHO','TRUONGKHOA');
