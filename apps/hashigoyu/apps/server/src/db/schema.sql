-- はしごゆ P2 schema
-- This file defines storage only. Sample bathhouse data is not included here.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS bathhouses (
  id TEXT PRIMARY KEY CHECK (id GLOB 'B[0-9][0-9][0-9]'),
  name TEXT NOT NULL,
  address TEXT NOT NULL,
  ward TEXT NOT NULL,
  lat REAL NOT NULL CHECK (lat BETWEEN -90 AND 90),
  lng REAL NOT NULL CHECK (lng BETWEEN -180 AND 180),
  has_sauna INTEGER NOT NULL CHECK (has_sauna IN (0, 1)),
  open_hour INTEGER NOT NULL CHECK (open_hour BETWEEN 0 AND 24),
  close_hour INTEGER NOT NULL CHECK (close_hour BETWEEN 0 AND 48),
  union_member INTEGER NOT NULL CHECK (union_member IN (0, 1)),
  active INTEGER NOT NULL CHECK (active IN (0, 1))
);

CREATE TABLE IF NOT EXISTS budgets (
  bathhouse_id TEXT NOT NULL,
  fiscal_year INTEGER NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('draft', 'confirmed')),
  confirmed_at TEXT,
  confirmed_by TEXT,
  operating_days INTEGER NOT NULL,
  price INTEGER NOT NULL,
  addon INTEGER NOT NULL,
  annual_visitors INTEGER NOT NULL,
  fuel INTEGER NOT NULL,
  labor INTEGER NOT NULL,
  other_fixed INTEGER NOT NULL,
  depreciation INTEGER NOT NULL,
  subsidy INTEGER NOT NULL,
  asset INTEGER NOT NULL,
  land INTEGER NOT NULL,
  cash INTEGER NOT NULL,
  target_cash INTEGER NOT NULL,
  years_to_cash_target INTEGER NOT NULL,
  debt INTEGER NOT NULL,
  years_to_renewal INTEGER NOT NULL,
  renewal_cost INTEGER NOT NULL,
  loan_repayment INTEGER NOT NULL,
  PRIMARY KEY (bathhouse_id, fiscal_year),
  FOREIGN KEY (bathhouse_id) REFERENCES bathhouses(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS visits (
  id TEXT PRIMARY KEY,
  bathhouse_id TEXT NOT NULL,
  at TEXT NOT NULL,
  source TEXT NOT NULL CHECK (source IN ('counter', 'qr', 'pos')),
  session_id TEXT,
  sequence INTEGER CHECK (sequence IS NULL OR sequence >= 1),
  FOREIGN KEY (bathhouse_id) REFERENCES bathhouses(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS daily_counts (
  bathhouse_id TEXT NOT NULL,
  date TEXT NOT NULL,
  total INTEGER NOT NULL,
  first INTEGER NOT NULL,
  hop INTEGER NOT NULL,
  unknown INTEGER NOT NULL,
  PRIMARY KEY (bathhouse_id, date),
  FOREIGN KEY (bathhouse_id) REFERENCES bathhouses(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS closures (
  bathhouse_id TEXT NOT NULL,
  date TEXT NOT NULL,
  reason TEXT,
  PRIMARY KEY (bathhouse_id, date),
  FOREIGN KEY (bathhouse_id) REFERENCES bathhouses(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_visits_bathhouse_at
  ON visits (bathhouse_id, at);

CREATE INDEX IF NOT EXISTS idx_visits_session_at
  ON visits (session_id, at);
