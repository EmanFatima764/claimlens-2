-- ClaimLens 2.0: columns the frontend report page and pipeline progress need.
-- Run AFTER 001_init_schema.sql in the Supabase SQL editor.

ALTER TABLE investigations
  ADD COLUMN IF NOT EXISTS current_stage VARCHAR(50);

ALTER TABLE sources
  ADD COLUMN IF NOT EXISTS domain TEXT,
  ADD COLUMN IF NOT EXISTS relevance_score FLOAT DEFAULT 0.5;

ALTER TABLE evidence
  ADD COLUMN IF NOT EXISTS stance VARCHAR(20) DEFAULT 'neutral';

ALTER TABLE verdicts
  ADD COLUMN IF NOT EXISTS confidence FLOAT DEFAULT 0.5;
