ALTER TABLE source_record DROP CONSTRAINT source_record_source_source_key_content_hash_key;
ALTER TABLE source_record ADD CONSTRAINT source_record_version_unique UNIQUE (source, source_key, version);
