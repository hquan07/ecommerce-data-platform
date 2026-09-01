import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

def create_spark_session():
    print("Initializing Spark Session with S3 and PostgreSQL connectors...")
    minio_endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
    minio_access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    minio_secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    jars = "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262,org.postgresql:postgresql:42.6.0"
    spark = SparkSession.builder \
        .appName("Olist Batch Transformation") \
        .config("spark.jars.packages", jars) \
        .config("spark.hadoop.fs.s3a.endpoint", f"http://{minio_endpoint}") \
        .config("spark.hadoop.fs.s3a.access.key", minio_access_key) \
        .config("spark.hadoop.fs.s3a.secret.key", minio_secret_key) \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    return spark

def process_table(spark, dataset_name, db_table, subset_col, jdbc_url, pg_user, pg_password):
    print(f"\nProcessing {dataset_name} data...")
    bronze_path = f"s3a://ecommerce-data/bronze/olist/{dataset_name}/olist_{dataset_name}_dataset.csv"
    try:
        df = spark.read.csv(bronze_path, header=True, inferSchema=True)
        print(f"Read {df.count()} records from MinIO Bronze ({dataset_name}).")
    except Exception as e:
        print(f"Error reading bronze data for {dataset_name}: {e}")
        return

    # Basic cleaning
    df_clean = df.dropna(subset=[subset_col])

    # Handle schema mismatch for products
    if dataset_name == "products":
        df_clean = df_clean.select(
            col("product_id"),
            col("product_category_name").alias("product_category_name_english"),
            col("product_weight_g").cast("decimal(38,18)"),
            col("product_length_cm").cast("decimal(38,18)"),
            col("product_height_cm").cast("decimal(38,18)"),
            col("product_width_cm").cast("decimal(38,18)")
        )
    
    print(f"Writing cleaned data to PostgreSQL {db_table}...")
    try:
        df_clean.write \
            .format("jdbc") \
            .option("url", jdbc_url) \
            .option("dbtable", db_table) \
            .option("user", pg_user) \
            .option("password", pg_password) \
            .option("driver", "org.postgresql.Driver") \
            .mode("append") \
            .save()
        print(f"Successfully written {dataset_name} data to {db_table}.")
    except Exception as e:
        print(f"Error writing to Postgres: {e}")

def main():
    spark = create_spark_session()
    
    pg_host = os.getenv("POSTGRES_HOST", "postgres")
    pg_port = os.getenv("POSTGRES_PORT", "5432")
    pg_db = os.getenv("POSTGRES_DB", "ecommerce")
    pg_user = os.getenv("POSTGRES_USER", "ecommerce")
    pg_password = os.getenv("POSTGRES_PASSWORD", "ecommerce")
    jdbc_url = f"jdbc:postgresql://{pg_host}:{pg_port}/{pg_db}"

    # Ordered properly for foreign key dependencies
    datasets = [
        ("customers", "dw.dim_customer", "customer_id"),
        ("sellers", "dw.dim_seller", "seller_id"),
        ("products", "dw.dim_product", "product_id"),
        ("orders", "dw.fact_orders", "order_id"),
        ("order_items", "dw.fact_order_items", "order_id"),
        ("order_payments", "dw.fact_payments", "order_id"),
        ("order_reviews", "dw.fact_reviews", "review_id"),
    ]

    for ds_name, table_name, pk_col in datasets:
        process_table(spark, ds_name, table_name, pk_col, jdbc_url, pg_user, pg_password)

    spark.stop()
    print("\nBatch transformation completed successfully.")

if __name__ == "__main__":
    main()
