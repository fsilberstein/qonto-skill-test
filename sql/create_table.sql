-- Creation of product table
CREATE TABLE IF NOT EXISTS companies_events (
  event_type varchar(10) NOT NULL,
  ingested_at TIMESTAMP,
  id uuid NOT NULL,
  name varchar(250) NOT NULL,
  organization_id uuid,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);