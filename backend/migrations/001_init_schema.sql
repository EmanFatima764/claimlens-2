-- ClaimLens 2.0 Schema for Supabase PostgreSQL
-- Run this SQL to initialize the database

CREATE TABLE IF NOT EXISTS investigations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  description TEXT,
  input_text TEXT,
  source_type VARCHAR(50) DEFAULT 'text',
  status VARCHAR(50) DEFAULT 'draft',
  workflow_status VARCHAR(50),
  final_verdict JSONB,
  error TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS claims (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  investigation_id UUID NOT NULL REFERENCES investigations(id) ON DELETE CASCADE,
  text TEXT NOT NULL,
  normalized_text TEXT,
  claim_type VARCHAR(100),
  entities JSONB DEFAULT '[]',
  confidence FLOAT DEFAULT 0.5,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sources (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  investigation_id UUID NOT NULL REFERENCES investigations(id) ON DELETE CASCADE,
  title TEXT,
  url TEXT,
  publisher TEXT,
  source_type VARCHAR(50),
  quality_score FLOAT DEFAULT 0.5,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS evidence (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  investigation_id UUID NOT NULL REFERENCES investigations(id) ON DELETE CASCADE,
  claim_id UUID REFERENCES claims(id) ON DELETE CASCADE,
  source_id UUID REFERENCES sources(id) ON DELETE CASCADE,
  evidence_text TEXT NOT NULL,
  evidence_type VARCHAR(50),
  relevance_score FLOAT DEFAULT 0.5,
  confidence FLOAT DEFAULT 0.5,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS verdicts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  investigation_id UUID NOT NULL UNIQUE REFERENCES investigations(id) ON DELETE CASCADE,
  label VARCHAR(50),
  explanation TEXT,
  evidence_strength FLOAT DEFAULT 0.5,
  uncertainty FLOAT DEFAULT 0.5,
  review_required BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS conflicts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  investigation_id UUID NOT NULL REFERENCES investigations(id) ON DELETE CASCADE,
  evidence_a_id UUID REFERENCES evidence(id) ON DELETE CASCADE,
  evidence_b_id UUID REFERENCES evidence(id) ON DELETE CASCADE,
  conflict_type VARCHAR(100),
  severity FLOAT DEFAULT 0.5,
  explanation TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for common queries
CREATE INDEX idx_investigations_status ON investigations(status);
CREATE INDEX idx_investigations_created_at ON investigations(created_at DESC);
CREATE INDEX idx_claims_investigation_id ON claims(investigation_id);
CREATE INDEX idx_sources_investigation_id ON sources(investigation_id);
CREATE INDEX idx_evidence_investigation_id ON evidence(investigation_id);
CREATE INDEX idx_evidence_claim_id ON evidence(claim_id);
CREATE INDEX idx_verdicts_investigation_id ON verdicts(investigation_id);
CREATE INDEX idx_conflicts_investigation_id ON conflicts(investigation_id);
