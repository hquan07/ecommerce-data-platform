CREATE SCHEMA IF NOT EXISTS dw;

CREATE TABLE IF NOT EXISTS dw.cloudvault_report_runs (
    report_type VARCHAR(100) NOT NULL,
    logical_date DATE NOT NULL,
    source_run_id VARCHAR(250) NOT NULL,
    file_id VARCHAR(250),
    status VARCHAR(30) NOT NULL,
    local_path TEXT NOT NULL,
    error_code VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (report_type, logical_date)
);
