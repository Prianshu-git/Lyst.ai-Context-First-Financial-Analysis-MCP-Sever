-- Core entities
CREATE TABLE IF NOT EXISTS company (
  company_id uuid PRIMARY KEY,
  tenant_id uuid NOT NULL,
  name text NOT NULL,
  ticker text,
  industry text
);

CREATE TABLE IF NOT EXISTS source_document (
  document_id uuid PRIMARY KEY,
  company_id uuid NOT NULL REFERENCES company(company_id),
  name text,
  doc_type text,
  quarter int,
  year int,
  source_uri text,
  checksum text,
  status text,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS financial_statement (
  statement_id uuid PRIMARY KEY,
  document_id uuid NOT NULL REFERENCES source_document(document_id),
  type text NOT NULL,
  period text,
  period_end date,
  currency text
);

CREATE TABLE IF NOT EXISTS statement_line_item (
  line_id uuid PRIMARY KEY,
  statement_id uuid NOT NULL REFERENCES financial_statement(statement_id),
  gaap_key text,
  label text,
  amount numeric,
  year int,
  quarter int
);

CREATE TABLE IF NOT EXISTS question (
  question_id uuid PRIMARY KEY,
  company_id uuid NOT NULL REFERENCES company(company_id),
  text text NOT NULL,
  tool_suggested text,
  asked_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS answer (
  answer_id uuid PRIMARY KEY,
  question_id uuid NOT NULL REFERENCES question(question_id),
  company_id uuid NOT NULL REFERENCES company(company_id),
  response_text text,
  format text,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS artifact (
  artifact_id uuid PRIMARY KEY,
  answer_id uuid NOT NULL REFERENCES answer(answer_id),
  type text,
  uri text
);

-- Context-first citations
CREATE TABLE IF NOT EXISTS citation (
  citation_id uuid PRIMARY KEY,
  answer_id uuid NOT NULL REFERENCES answer(answer_id),
  document_id uuid NOT NULL REFERENCES source_document(document_id),
  doc_name text,
  source_uri text,
  page int,
  line_start int,
  line_end int,
  sheet text,
  cell_range text,
  quote text,
  chunk_id text,
  score float,
  created_at timestamptz DEFAULT now()
);

-- Optional KPI observations and benchmarks
CREATE TABLE IF NOT EXISTS kpi_observation (
  kpi_id uuid PRIMARY KEY,
  company_id uuid NOT NULL REFERENCES company(company_id),
  metric text,
  value numeric,
  year int,
  quarter int,
  source_ref text
);

CREATE TABLE IF NOT EXISTS benchmark (
  benchmark_id uuid PRIMARY KEY,
  industry text,
  metric text,
  p25 numeric,
  p50 numeric,
  p75 numeric,
  year int
);
