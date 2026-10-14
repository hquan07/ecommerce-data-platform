"""Daily report generation and CloudVault bookkeeping for the E-commerce DAG."""

from __future__ import annotations

import csv
import logging
import os
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Sequence

import psycopg2

from integrations.cloudvault import CloudVaultClient, CloudVaultConfig


logger = logging.getLogger(__name__)


DAILY_SALES_QUERY = """
SELECT
    o.order_purchase_timestamp::date AS sales_date,
    COALESCE(o.order_status, 'unknown') AS order_status,
    COUNT(DISTINCT o.order_id) AS order_count,
    COUNT(DISTINCT o.customer_id) AS customer_count,
    COALESCE(SUM(oi.price + oi.freight_value), 0)::numeric(14, 2) AS gross_sales
FROM dw.fact_orders AS o
JOIN dw.fact_order_items AS oi ON oi.order_id = o.order_id
WHERE o.order_purchase_timestamp >= %s
  AND o.order_purchase_timestamp < %s
GROUP BY o.order_purchase_timestamp::date, o.order_status
ORDER BY sales_date, order_status
"""


CREATE_REPORT_RUNS_SQL = """
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
)
"""


def postgres_connection():
    """Create a warehouse connection from the same variables used by Compose."""
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        user=os.getenv("POSTGRES_USER", "ecommerce"),
        password=os.getenv("POSTGRES_PASSWORD", "ecommerce"),
        dbname=os.getenv("POSTGRES_DB", "ecommerce"),
    )


def _logical_date(value: str | date | datetime) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(value[:10])


def export_daily_sales_report(
    output_dir: str | Path,
    logical_date: str | date | datetime,
    *,
    connection: Any | None = None,
) -> Path:
    """Export one deterministic, non-empty Daily Sales CSV from the warehouse."""
    report_date = _logical_date(logical_date)
    own_connection = connection is None
    connection = connection or postgres_connection()
    output_path = Path(output_dir) / f"daily-sales-{report_date.isoformat()}.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with connection.cursor() as cursor:
            cursor.execute(DAILY_SALES_QUERY, (report_date, report_date + timedelta(days=1)))
            rows: Sequence[Sequence[Any]] = cursor.fetchall()
        if not rows:
            raise ValueError(f"Daily Sales report has no rows for {report_date.isoformat()}")
        with output_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(("sales_date", "order_status", "order_count", "customer_count", "gross_sales"))
            writer.writerows(rows)
        if output_path.stat().st_size == 0:
            raise ValueError("Daily Sales report is empty")
        return output_path
    finally:
        if own_connection:
            connection.close()


def record_report_run(
    connection: Any,
    *,
    report_type: str,
    logical_date: str | date | datetime,
    source_run_id: str,
    local_path: str | Path,
    status: str,
    file_id: str | None = None,
    error_code: str | None = None,
) -> None:
    report_date = _logical_date(logical_date)
    with connection.cursor() as cursor:
        cursor.execute(CREATE_REPORT_RUNS_SQL)
        cursor.execute(
            """
            INSERT INTO dw.cloudvault_report_runs
                (report_type, logical_date, source_run_id, file_id, status, local_path, error_code)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (report_type, logical_date) DO UPDATE SET
                source_run_id = EXCLUDED.source_run_id,
                file_id = EXCLUDED.file_id,
                status = EXCLUDED.status,
                local_path = EXCLUDED.local_path,
                error_code = EXCLUDED.error_code,
                updated_at = NOW()
            """,
            (report_type, report_date, source_run_id, file_id, status, str(local_path), error_code),
        )
    connection.commit()


def upload_daily_sales_report(
    report_path: str | Path,
    *,
    logical_date: str | date | datetime,
    source_run_id: str,
    client: CloudVaultClient | None = None,
    connection: Any | None = None,
) -> dict[str, Any]:
    """Upload a report and persist its CloudVault identity/status.

    The source file is deliberately not removed here. It remains available for
    retry when CloudVault or the metadata database is unavailable.
    """
    path = Path(report_path)
    report_date = _logical_date(logical_date)
    own_connection = connection is None
    connection = connection or postgres_connection()
    client = client or CloudVaultClient(CloudVaultConfig.from_env())
    metadata = {
        "artifact_type": "daily_sales_report",
        "logical_date": report_date.isoformat(),
        "source_run_id": source_run_id,
        "format": "csv",
        "retention_class": "ecommerce-report",
    }
    idempotency_key = f"daily_sales_report:{report_date.isoformat()}"
    try:
        response = client.upload_file(
            path,
            metadata=metadata,
            idempotency_key=idempotency_key,
            content_type="text/csv",
        )
        file_id = response.get("file_id")
        if not file_id:
            raise ValueError("CloudVault upload response did not contain file_id")
        record_report_run(
            connection,
            report_type="daily_sales_report",
            logical_date=report_date,
            source_run_id=source_run_id,
            local_path=path,
            status="UPLOADED",
            file_id=str(file_id),
        )
        return response
    except Exception as exc:
        try:
            record_report_run(
                connection,
                report_type="daily_sales_report",
                logical_date=report_date,
                source_run_id=source_run_id,
                local_path=path,
                status="UPLOAD_FAILED",
                error_code=getattr(exc, "code", type(exc).__name__),
            )
        except Exception:
            logger.exception("Could not persist failed CloudVault report status")
        raise
    finally:
        if own_connection:
            connection.close()
