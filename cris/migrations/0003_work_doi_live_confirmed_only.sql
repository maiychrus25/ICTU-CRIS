-- Copyright (c) 2026 ICTU-CRIS contributors
-- SPDX-License-Identifier: Apache-2.0
DROP INDEX work_doi_live;
CREATE UNIQUE INDEX work_doi_live ON work(doi) WHERE doi IS NOT NULL AND state = 'DaXacNhan';
