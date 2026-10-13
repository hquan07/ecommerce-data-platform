import csv

import pytest

from integrations.ecommerce_reports import export_daily_sales_report, upload_daily_sales_report


class FakeCursor:
    def __init__(self, rows=()):
        self.rows = list(rows)
        self.executed = []

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute(self, query, params=None):
        self.executed.append((query, params))

    def fetchall(self):
        return self.rows


class FakeConnection:
    def __init__(self, rows=()):
        self.cursor_instance = FakeCursor(rows)
        self.commits = 0

    def cursor(self):
        return self.cursor_instance

    def commit(self):
        self.commits += 1


class FakeClient:
    def __init__(self, response=None, error=None):
        self.response = response or {"file_id": "file-123", "status": "AVAILABLE"}
        self.error = error
        self.calls = []

    def upload_file(self, path, **kwargs):
        self.calls.append((path, kwargs))
        if self.error:
            raise self.error
        return self.response


def test_export_daily_sales_report_writes_deterministic_csv(tmp_path):
    connection = FakeConnection([
        ("2026-10-14", "delivered", 3, 2, "125.50"),
    ])

    report = export_daily_sales_report(tmp_path, "2026-10-14", connection=connection)

    assert report.name == "daily-sales-2026-10-14.csv"
    with report.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    assert rows == [
        ["sales_date", "order_status", "order_count", "customer_count", "gross_sales"],
        ["2026-10-14", "delivered", "3", "2", "125.50"],
    ]


def test_export_rejects_empty_report(tmp_path):
    with pytest.raises(ValueError, match="no rows"):
        export_daily_sales_report(tmp_path, "2026-10-14", connection=FakeConnection())


def test_upload_records_file_id_and_keeps_source(tmp_path):
    report = tmp_path / "daily-sales-2026-10-14.csv"
    report.write_text("sales_date,order_status\n2026-10-14,delivered\n", encoding="utf-8")
    connection = FakeConnection()
    client = FakeClient()

    result = upload_daily_sales_report(
        report,
        logical_date="2026-10-14",
        source_run_id="scheduled__2026-10-14",
        client=client,
        connection=connection,
    )

    assert result["file_id"] == "file-123"
    assert report.exists()
    assert client.calls[0][1]["idempotency_key"] == "daily_sales_report:2026-10-14"
    assert connection.commits == 1


def test_upload_records_failure_and_keeps_source(tmp_path):
    report = tmp_path / "daily-sales-2026-10-14.csv"
    report.write_text("report", encoding="utf-8")
    connection = FakeConnection()
    client = FakeClient(error=RuntimeError("CloudVault unavailable"))

    with pytest.raises(RuntimeError, match="unavailable"):
        upload_daily_sales_report(
            report,
            logical_date="2026-10-14",
            source_run_id="scheduled__2026-10-14",
            client=client,
            connection=connection,
        )

    assert report.exists()
    assert connection.commits == 1
