# E-commerce Data Platform

End-to-end Data Engineering portfolio project for building a hybrid **batch + real-time streaming e-commerce data platform**.

The project demonstrates a production-oriented data pipeline using:

- Python
- Apache Kafka
- Apache Spark / PySpark Structured Streaming
- Apache Airflow
- PostgreSQL
- MinIO (S3-compatible object storage)
- Docker / Docker Compose
- Pytest
- Plotly Dash
- Prometheus + Grafana

> **Important:** The project does not use dbt. Transformations are implemented with PySpark, SQL, and Python.

---

## 1. Project Overview

The platform combines historical e-commerce data with continuously generated real-time events.

### Main goals

1. Ingest historical e-commerce data.
2. Generate realistic real-time e-commerce events.
3. Stream events through Kafka.
4. Process streaming events using PySpark Structured Streaming.
5. Store raw and processed data in a data lake.
6. Build a relational analytical warehouse in PostgreSQL.
7. Orchestrate batch pipelines with Airflow.
8. Apply data quality validation and deduplication.
9. Provide analytics through a dashboard.
10. Monitor the platform with Prometheus and Grafana.
11. Provide automated tests with Pytest.
12. Make the entire environment reproducible with Docker Compose.

---

# 2. Architecture

```text
                           DATA SOURCES
                                |
                 +--------------+--------------+
                 |                             |
                 v                             v
        Olist Historical Data        Realtime Event Generator
                 |                             |
                 v                             v
              Python                         Kafka
                 |                    +---------+---------+
                 v                    |         |         |
              MinIO                orders    clicks   payments
                 |                    |         |         |
                 |                    +---------+---------+
                 |                              |
                 |                              v
                 |                    PySpark Structured
                 |                         Streaming
                 |                              |
                 +------------------------------+
                                |
                          Processing Layer
                                |
                  +-------------+-------------+
                  |             |             |
                  v             v             v
               Bronze        Silver         Gold
                  |             |             |
                  +-------------+-------------+
                                |
                                v
                            PostgreSQL
                         Analytical Warehouse
                                |
                    +-----------+-----------+
                    |                       |
                    v                       v
                Dashboard              ML/Analytics
                    |
                    v
              Plotly Dash

                 Orchestration: Airflow
                 Monitoring: Prometheus + Grafana
                 Tests: Pytest
                 Packaging: Docker Compose
```

---

# 3. Data Sources

## 3.1 Historical batch source

The primary historical dataset is the **Brazilian E-Commerce Public Dataset by Olist**.

It contains entities such as:

- customers
- orders
- order items
- products
- payments
- reviews
- sellers
- geolocation

The historical dataset is used for:

- customer/product master data
- historical sales
- warehouse initialization
- batch ETL
- analytical reporting

Download the dataset from its official Kaggle page and place the CSV files under:

```text
data/raw/olist/
```

Example:

```text
data/
└── raw/
    └── olist/
        ├── olist_customers_dataset.csv
        ├── olist_geolocation_dataset.csv
        ├── olist_order_items_dataset.csv
        ├── olist_order_payments_dataset.csv
        ├── olist_order_reviews_dataset.csv
        ├── olist_orders_dataset.csv
        ├── olist_products_dataset.csv
        ├── olist_sellers_dataset.csv
        └── product_category_name_translation.csv
```

## 3.2 Real-time source

The streaming source is a Python event generator.

It continuously creates realistic e-commerce events such as:

- `product_viewed`
- `cart_added`
- `order_created`
- `payment_completed`
- `order_shipped`
- `order_delivered`
- `order_cancelled`

This is a **real-time synthetic event source**. It is not historical data replay.

Example event:

```json
{
  "event_id": "evt_8f31",
  "event_type": "order_created",
  "customer_id": 18342,
  "product_id": 921,
  "order_id": "ORD_20260831_001",
  "quantity": 2,
  "unit_price": 49.99,
  "timestamp": "2026-08-31T19:31:24Z"
}
```

---

# 4. Project Structure

```text
ecommerce-data-platform/
│
├── airflow/
│   ├── dags/
│   │   ├── ecommerce_batch_pipeline.py
│   │   ├── ecommerce_streaming_pipeline.py
│   │   └── data_quality_dag.py
│   ├── logs/
│   └── plugins/
│
├── configs/
│   ├── kafka_config.py
│   ├── spark_config.py
│   └── app_config.py
│
├── data/
│   ├── raw/
│   │   └── olist/
│   ├── bronze/
│   ├── silver/
│   └── gold/
│
├── dashboard/
│   ├── app.py
│   ├── queries.py
│   └── requirements.txt
│
├── docker/
│   ├── airflow/
│   │   └── Dockerfile
│   ├── spark/
│   │   └── Dockerfile
│   └── app/
│       └── Dockerfile
│
├── sql/
│   ├── 01_warehouse_schema.sql
│   ├── 02_indexes.sql
│   ├── 03_views.sql
│   └── 04_seed.sql
│
├── src/
│   ├── ingestion/
│   │   ├── batch/
│   │   └── streaming/
│   │       ├── event_generator.py
│   │       └── kafka_producer.py
│   │
│   ├── processing/
│   │   ├── batch/
│   │   └── streaming/
│   │       ├── stream_processor.py
│   │       ├── schemas.py
│   │       └── aggregations.py
│   │
│   ├── quality/
│   │   ├── validators.py
│   │   └── rules.py
│   │
│   └── utils/
│       ├── logging.py
│       └── config.py
│
├── tests/
│   ├── test_event_generator.py
│   ├── test_kafka_producer.py
│   ├── test_transformations.py
│   ├── test_data_quality.py
│   └── test_schemas.py
│
├── notebooks/
│   ├── 01_eda.ipynb
│   └── 02_analytics.ipynb
│
├── monitoring/
│   ├── prometheus/
│   └── grafana/
│
├── docker-compose.yml
├── .env.example
├── requirements.txt
├── Makefile
└── README.md
```

---

# 5. Technology Stack

| Layer | Technology |
|---|---|
| Programming | Python 3.11+ |
| Batch Processing | Apache Spark |
| Streaming | Apache Kafka |
| Stream Processing | PySpark Structured Streaming |
| Orchestration | Apache Airflow |
| Data Lake | MinIO / S3 |
| Warehouse | PostgreSQL |
| Dashboard | Plotly Dash |
| Testing | Pytest |
| Monitoring | Prometheus + Grafana |
| Containerization | Docker / Docker Compose |
| Version Control | Git / GitHub |

The exact image/package versions should be pinned in `docker-compose.yml`, Dockerfiles, and `requirements.txt` to keep the project reproducible.

---

# 6. Prerequisites

Install:

- Docker
- Docker Compose
- Git
- Python 3.11+ (recommended for local development)
- At least 8 GB RAM
- At least 20 GB free disk space

Verify:

```bash
docker --version
docker compose version
git --version
python3 --version
```

Optional local virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Most services run inside Docker, so a local Python installation is primarily useful for development and testing.

---

# 7. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd ecommerce-data-platform
```

Create environment configuration:

```bash
cp .env.example .env
```

Review `.env` before starting the platform.

Example variables:

```env
POSTGRES_DB=ecommerce
POSTGRES_USER=ecommerce
POSTGRES_PASSWORD=ecommerce

KAFKA_BROKER=broker:29092

MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin

AIRFLOW_UID=50000
```

Do not commit real passwords or secrets.

---

# 8. Start the Infrastructure

Build images:

```bash
docker compose build
```

Start all services:

```bash
docker compose up -d
```

Check service status:

```bash
docker compose ps
```

Check logs:

```bash
docker compose logs -f
```

Check one service:

```bash
docker compose logs -f kafka
docker compose logs -f spark
docker compose logs -f airflow
docker compose logs -f postgres
```

Stop the platform:

```bash
docker compose down
```

Stop and remove volumes as well:

```bash
docker compose down -v
```

> `docker compose down -v` deletes persistent database/object-storage volumes. Use it only when you intentionally want a clean environment.

---

# 9. Initialize PostgreSQL Warehouse

The PostgreSQL schema contains the analytical warehouse.

Core tables:

```text
dim_date
dim_customer
dim_product
dim_seller
dim_location

fact_orders
fact_order_items
fact_payments
fact_reviews
```

Depending on the implementation, operational/streaming tables can also include:

```text
stream_events
realtime_order_metrics
realtime_product_metrics
realtime_customer_metrics
```

Apply SQL scripts:

```bash
docker compose exec postgres psql \
  -U "$POSTGRES_USER" \
  -d "$POSTGRES_DB" \
  -f /docker-entrypoint-initdb.d/01_warehouse_schema.sql
```

If the SQL files are executed automatically by the PostgreSQL image on first initialization, no manual execution is required.

Verify:

```bash
docker compose exec postgres psql \
  -U ecommerce \
  -d ecommerce \
  -c "\dt"
```

---

# 10. Initialize MinIO

Open the MinIO console in your browser:

```text
http://localhost:9001
```

Create a bucket:

```text
ecommerce-data
```

Recommended logical folders:

```text
ecommerce-data/
├── bronze/
├── silver/
└── gold/
```

The lake layout is:

```text
Bronze
  raw ingested data
      ↓
Silver
  cleaned / validated / deduplicated data
      ↓
Gold
  business-ready analytical datasets
```

---

# 11. Load Historical Olist Data

Download the Olist CSV dataset and copy it into:

```text
data/raw/olist/
```

Run the batch ingestion module:

```bash
docker compose run --rm app \
  python -m src.ingestion.batch.load_olist
```

The ingestion process should:

1. Read the source CSV files.
2. Validate file presence and schema.
3. Store raw files in the Bronze layer.
4. Normalize data types.
5. Clean nulls and invalid records.
6. Deduplicate records where necessary.
7. Create Silver datasets.
8. Load dimensions and facts into PostgreSQL.

Example flow:

```text
Olist CSV
   ↓
Raw/Bronze
   ↓
Validation
   ↓
Spark Transformation
   ↓
Silver
   ↓
Gold
   ↓
PostgreSQL
```

---

# 12. Start Kafka

Kafka should be started through Docker Compose.

Verify the broker:

```bash
docker compose ps kafka
```

List topics:

```bash
docker compose exec kafka kafka-topics \
  --bootstrap-server broker:29092 \
  --list
```

Create topics:

```bash
docker compose exec kafka kafka-topics \
  --bootstrap-server broker:29092 \
  --create \
  --if-not-exists \
  --topic ecommerce.orders \
  --partitions 3 \
  --replication-factor 1
```

Additional topics:

```text
ecommerce.orders
ecommerce.clicks
ecommerce.payments
ecommerce.shipments
```

Recommended event partition key:

```text
customer_id
```

or:

```text
order_id
```

The key should be chosen according to the ordering requirement of each event stream.

---

# 13. Run the Real-Time Event Generator

Start the synthetic event generator:

```bash
docker compose run --rm app \
  python -m src.ingestion.streaming.event_generator
```

The generator continuously produces events.

Example:

```text
19:30:01 order_created
19:30:02 product_viewed
19:30:04 payment_completed
19:30:05 product_viewed
19:30:07 order_created
```

The producer publishes them to Kafka:

```text
Python Event Generator
        ↓
Kafka Producer
        ↓
ecommerce.orders
```

To inspect messages:

```bash
docker compose exec kafka kafka-console-consumer \
  --bootstrap-server broker:29092 \
  --topic ecommerce.orders \
  --from-beginning
```

---

# 14. Run PySpark Structured Streaming

Start the streaming processor:

```bash
docker compose run --rm spark \
  spark-submit \
  /opt/spark-apps/src/processing/streaming/stream_processor.py
```

The processor should implement:

### 14.1 Schema validation

```text
event_id
event_type
customer_id
product_id
order_id
quantity
unit_price
timestamp
```

### 14.2 Deduplication

Use:

```text
event_id
```

as the unique event identifier.

Duplicate example:

```text
evt_123
evt_123
```

Only one event should reach the downstream analytical dataset.

### 14.3 Watermarking

Events can arrive later than their event timestamp.

Example:

```text
event time: 19:30:05
arrival:    19:30:15
```

Use event-time processing and watermarking so late data can be handled without keeping state forever.

### 14.4 Windowed aggregation

Example five-minute metrics:

```text
orders_per_5min
revenue_per_5min
unique_customers_per_5min
average_order_value
```

Conceptually:

```text
Kafka
  ↓
Parse event
  ↓
Validate
  ↓
Deduplicate
  ↓
Watermark
  ↓
5-minute window
  ↓
Aggregation
  ↓
PostgreSQL / Gold
```

---

# 15. Real-Time Processing Outputs

Example Gold-level realtime metrics:

```text
realtime_sales_metrics

window_start
window_end
orders_count
revenue
unique_customers
average_order_value
```

Example:

```text
2026-08-31 19:30:00
2026-08-31 19:35:00
127
8421.35
932
66.31
```

Other useful aggregations:

```text
top_products_realtime
top_categories_realtime
orders_by_city_realtime
payments_by_method_realtime
cart_conversion_realtime
```

---

# 16. Airflow Orchestration

Open Airflow:

```text
http://localhost:8080
```

Use the configured Airflow credentials from `.env`.

Recommended DAGs:

```text
ecommerce_batch_pipeline
ecommerce_streaming_pipeline
data_quality_pipeline
daily_warehouse_refresh
```

## Batch DAG

Example dependency graph:

```text
check_source
     ↓
ingest_olist
     ↓
validate_raw
     ↓
spark_transform
     ↓
load_dimensions
     ↓
load_facts
     ↓
data_quality
     ↓
success
```

## Streaming DAG

Airflow should orchestrate long-running jobs and operational checks rather than replace Kafka or Spark.

Example:

```text
check_kafka
     ↓
check_schema
     ↓
start_stream_processor
     ↓
health_check
     ↓
monitor_stream
```

For a long-running Spark streaming job, use an appropriate deployment strategy rather than repeatedly starting duplicate streaming queries.

---

# 17. Data Quality

Data quality is part of the core pipeline.

Recommended rules:

### Completeness

```text
order_id IS NOT NULL
customer_id IS NOT NULL
product_id IS NOT NULL
timestamp IS NOT NULL
```

### Validity

```text
quantity > 0
unit_price >= 0
timestamp is valid
event_type is supported
```

### Uniqueness

```text
event_id must be unique
order_id must be unique where applicable
```

### Referential integrity

```text
customer_id exists in dim_customer
product_id exists in dim_product
```

### Freshness

Check that streaming data is not older than the configured freshness threshold.

Bad records should be isolated into a quarantine location:

```text
data/
└── quarantine/
    ├── invalid_schema/
    ├── invalid_values/
    └── duplicates/
```

---

# 18. Dashboard

Start the dashboard:

```bash
docker compose up -d dashboard
```

Open:

```text
http://localhost:8050
```

Recommended dashboard sections.

## Overview

```text
Total Orders
Total Revenue
Average Order Value
Unique Customers
```

## Real-Time

```text
Orders/min
Revenue/min
Active Customers
Top Products
Latest Events
```

## Sales Analytics

```text
Revenue by Date
Revenue by Category
Revenue by State
Order Status
Payment Method
```

## Customer Analytics

```text
Customers by State
Repeat Customers
Average Order Value
Customer Order Frequency
```

---

# 19. Monitoring

Prometheus and Grafana are used to demonstrate operational monitoring.

Open Grafana:

```text
http://localhost:3000
```

Useful metrics:

```text
Kafka messages/sec
Spark processing latency
Streaming input rate
Streaming processed rate
Consumer lag
Failed records
Data quality failures
Airflow DAG failures
PostgreSQL connection usage
```

Recommended Grafana dashboards:

1. Kafka overview
2. Spark streaming health
3. Airflow pipeline health
4. PostgreSQL health
5. Data quality

---

# 20. Testing

Run all tests:

```bash
pytest -v
```

Run a specific test:

```bash
pytest -v tests/test_event_generator.py
```

Recommended test categories:

### Unit tests

```text
event generation
schema validation
transformations
data quality rules
```

### Integration tests

```text
Kafka producer → Kafka broker
Spark → PostgreSQL
Airflow task dependencies
```

### Data tests

```text
null checks
unique checks
range checks
referential integrity
```

---

# 21. End-to-End Deployment

A clean deployment can be performed in the following order.

## Step 1 — Clone

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd ecommerce-data-platform
```

## Step 2 — Configure environment

```bash
cp .env.example .env
```

## Step 3 — Place Olist dataset

```text
data/raw/olist/
```

## Step 4 — Build images

```bash
docker compose build
```

## Step 5 — Start infrastructure

```bash
docker compose up -d
```

## Step 6 — Check containers

```bash
docker compose ps
```

## Step 7 — Initialize MinIO bucket

Create:

```text
ecommerce-data
```

## Step 8 — Initialize PostgreSQL

Verify:

```bash
docker compose exec postgres psql \
  -U ecommerce \
  -d ecommerce \
  -c "\dt"
```

## Step 9 — Run batch ingestion

```bash
docker compose run --rm app \
  python -m src.ingestion.batch.load_olist
```

## Step 10 — Create Kafka topics

```bash
docker compose exec kafka kafka-topics \
  --bootstrap-server broker:29092 \
  --create \
  --if-not-exists \
  --topic ecommerce.orders \
  --partitions 3 \
  --replication-factor 1
```

Repeat for other event topics.

## Step 11 — Start the realtime producer

```bash
docker compose run --rm app \
  python -m src.ingestion.streaming.event_generator
```

## Step 12 — Start Spark streaming

```bash
docker compose run --rm spark \
  spark-submit \
  /opt/spark-apps/src/processing/streaming/stream_processor.py
```

## Step 13 — Enable Airflow DAGs

Open:

```text
http://localhost:8080
```

Enable the required DAGs.

## Step 14 — Open dashboards

```text
Airflow       http://localhost:8080
MinIO         http://localhost:9001
Grafana       http://localhost:3000
Dashboard     http://localhost:8050
```

---

# 22. Useful Docker Commands

Start:

```bash
docker compose up -d
```

Stop:

```bash
docker compose down
```

Rebuild one service:

```bash
docker compose build app
docker compose up -d app
```

Restart:

```bash
docker compose restart
```

View running services:

```bash
docker compose ps
```

Follow logs:

```bash
docker compose logs -f app
```

Open a shell:

```bash
docker compose exec app bash
```

Inspect resource usage:

```bash
docker stats
```

Clean unused Docker resources:

```bash
docker system prune
```

Use the last command carefully because it removes unused Docker objects.

---

# 23. Common Troubleshooting

## Kafka is not ready

Check:

```bash
docker compose logs kafka
```

Check the broker from inside the Kafka container:

```bash
docker compose exec kafka \
  kafka-topics --bootstrap-server broker:29092 --list
```

Make sure application containers use:

```text
broker:29092
```

and not:

```text
localhost:9092
```

`localhost` inside a container refers to that container itself.

---

## PostgreSQL connection refused

Check:

```bash
docker compose ps postgres
docker compose logs postgres
```

Verify the host used by other containers is:

```text
postgres
```

not:

```text
localhost
```

---

## Spark cannot connect to Kafka

Verify:

1. Kafka container is running.
2. The Kafka bootstrap server is reachable from the Spark container.
3. The Kafka topic exists.
4. Spark Kafka dependencies match the Spark version.
5. The application is using the container network hostname.

---

## Airflow DAG does not appear

Check:

```bash
docker compose logs airflow-scheduler
docker compose logs airflow-dag-processor
```

Confirm the DAG file is mounted to the Airflow DAG directory.

---

## Dashboard cannot connect to PostgreSQL

Inside Docker, use:

```text
postgres
```

as the hostname.

Do not use:

```text
localhost
```

unless the dashboard is running directly on the host machine.

---

# 24. Data Engineering Design Decisions

## Why Kafka?

Kafka provides:

- durable event streaming
- partitioning
- consumer groups
- scalable ingestion
- decoupling between producers and consumers

## Why Spark Structured Streaming?

Spark provides:

- distributed processing
- event-time processing
- window operations
- watermarking
- stateful processing
- scalable transformations

## Why MinIO?

MinIO provides an S3-compatible object-storage layer that is easy to run locally with Docker.

It acts as the project's data lake storage.

## Why PostgreSQL?

PostgreSQL is used as the analytical serving layer because it is:

- easy to run locally
- SQL-friendly
- suitable for analytical queries at portfolio scale
- easy to connect to dashboards

## Why Airflow?

Airflow is responsible for:

- scheduling
- dependency management
- retries
- monitoring
- batch workflow orchestration

Kafka and Spark remain responsible for streaming.

---

# 25. Bronze / Silver / Gold Model

## Bronze

Raw, minimally changed data.

```text
Raw CSV
Raw events
Original schema
Ingestion metadata
```

## Silver

Cleaned and standardized data.

```text
Validated schemas
Standardized types
Deduplicated records
Normalized fields
```

## Gold

Business-ready analytical data.

```text
Fact tables
Dimension tables
Aggregated metrics
Realtime KPI tables
```

This separation makes the project easier to debug and demonstrates modern data-platform design.

---

# 26. Performance Considerations

For a stronger portfolio implementation, benchmark:

### Kafka

- throughput
- partition count
- consumer lag

### Spark

- input rows/sec
- processing latency
- batch duration
- state-store size

### PostgreSQL

- query execution time
- index effectiveness
- insert throughput

### Pipeline

Track:

```text
source → Kafka latency
Kafka → Spark latency
Spark → PostgreSQL latency
end-to-end event latency
```

A useful portfolio metric is:

```text
P95 end-to-end latency
```

measured from event creation until the record is queryable in the serving layer.

---

# 27. CI/CD

A GitHub Actions pipeline can run:

```text
git push
   ↓
Lint
   ↓
Unit Tests
   ↓
Integration Tests
   ↓
Docker Build
   ↓
Success
```

Recommended checks:

```bash
pytest -v
python -m compileall src
docker compose config
```

---

# 28. Portfolio Deliverables

The final GitHub repository should contain:

- architecture diagram
- README
- Docker Compose deployment
- source code
- Airflow DAGs
- Spark jobs
- Kafka producer
- event schemas
- SQL warehouse schema
- tests
- dashboard screenshots
- Grafana screenshots
- sample data
- benchmark results
- troubleshooting guide

Avoid committing:

- `.env`
- passwords
- API keys
- huge raw datasets
- generated logs
- database volumes

Use `.gitignore` for local artifacts.

---

# 29. Suggested GitHub README Demo

The top of the GitHub README should quickly show:

```text
E-commerce Data Platform
========================

Batch + Real-Time Data Engineering Platform

Python | Kafka | Spark | Airflow | PostgreSQL | MinIO | Docker

Features
--------
✓ Batch ETL
✓ Real-time Kafka streaming
✓ Spark Structured Streaming
✓ Data Lake Bronze/Silver/Gold
✓ Star Schema Data Warehouse
✓ Data Quality
✓ Airflow orchestration
✓ Real-time Dashboard
✓ Monitoring
✓ Automated Testing
```

Then add:

1. Architecture diagram
2. Tech stack
3. Quick Start
4. Pipeline walkthrough
5. Screenshots
6. Performance metrics
7. Engineering decisions
8. Future improvements

---

# 30. Future Improvements

Possible extensions:

- Schema Registry + Avro
- Kafka Connect
- CDC with Debezium
- Redis for low-latency serving
- Kubernetes deployment
- Spark cluster instead of local mode
- S3 instead of MinIO in production
- PostgreSQL read replicas
- CI/CD deployment to cloud
- Feature Store
- ML recommendation system
- anomaly detection on streaming events

---

# 31. Project Success Criteria

The project is considered complete when:

- [ ] Docker Compose starts the complete stack.
- [ ] PostgreSQL warehouse is initialized successfully.
- [ ] Olist historical data is ingested.
- [ ] Bronze/Silver/Gold layers are populated.
- [ ] Kafka topics are created automatically or through a documented command.
- [ ] Real-time events are continuously produced.
- [ ] Spark Structured Streaming consumes Kafka events.
- [ ] Duplicate events are removed.
- [ ] Late events are handled with event-time semantics and watermarking.
- [ ] Realtime window metrics are computed.
- [ ] Gold/realtime tables are queryable in PostgreSQL.
- [ ] Airflow orchestrates batch workflows.
- [ ] Data quality checks run automatically.
- [ ] Dashboard displays historical and realtime KPIs.
- [ ] Prometheus/Grafana provide operational metrics.
- [ ] Pytest passes.
- [ ] The full setup is reproducible from a clean clone.

---

# 32. License

This project is intended as a personal Data Engineering portfolio project.

Check the license terms of any external dataset or third-party data source before redistributing the raw data.
