-- ClaimLens 2.0: verified_claims and independence_analysis tables.
-- Run AFTER 002_report_fields.sql in the Supabase SQL editor.

-- Per-claim verification results (from VerificationAgent)
CREATE TABLE IF NOT EXISTS verified_claims (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  investigation_id UUID NOT NULL REFERENCES investigations(id) ON DELETE CASCADE,
  claim_id UUID REFERENCES claims(id) ON DELETE CASCADE,
  verification_status VARCHAR(50) NOT NULL DEFAULT 'insufficient_evidence',
  confidence FLOAT DEFAULT 0.5,
  supporting_evidence JSONB DEFAULT '[]',
  contradicting_evidence JSONB DEFAULT '[]',
  reasoning TEXT DEFAULT '',
  unresolved_issues JSONB DEFAULT '[]',
  llm_fallback BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_verified_claims_investigation_id ON verified_claims(investigation_id);
CREATE INDEX IF NOT EXISTS idx_verified_claims_claim_id ON verified_claims(claim_id);

-- Independence analysis (from IndependenceAgent) — one row per investigation
CREATE TABLE IF NOT EXISTS independence_analysis (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  investigation_id UUID NOT NULL UNIQUE REFERENCES investigations(id) ON DELETE CASCADE,
  independent_source_count INTEGER DEFAULT 0,
  total_source_count INTEGER DEFAULT 0,
  independence_ratio FLOAT DEFAULT 0.0,
  source_groups JSONB DEFAULT '[]',
  relationships JSONB DEFAULT '[]',
  overall_independence VARCHAR(20) DEFAULT 'unknown',
  explanation TEXT DEFAULT '',
  llm_fallback BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_independence_analysis_investigation_id ON independence_analysis(investigation_id);
