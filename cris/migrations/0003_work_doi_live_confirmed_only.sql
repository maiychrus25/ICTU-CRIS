DROP INDEX work_doi_live;
CREATE UNIQUE INDEX work_doi_live ON work(doi) WHERE doi IS NOT NULL AND state = 'DaXacNhan';
