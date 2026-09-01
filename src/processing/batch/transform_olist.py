import os
import sys
from pyspark.sql import SparkSession

def create_spark_session():
    print("Initializing Spark Session with S3 and PostgreSQL connectors...")
    # MinIO credentials
    minio_endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
    minio_access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    minio_secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")

    # Jars needed: hadoop-aws, aws-java-sdk-bundle for S3A; postgresql for JDBC
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
    
    # Reduce logging for cleaner output
    spark.sparkContext.setLogLevel("WARN")
    return spark

def process_customers(spark):
    print("Processing customers data...")
    # Read from Bronze MinIO
    bronze_path = "s3a://ecommerce-data/bronze/olist/customers/olist_customers_dataset.csv"
    try:
        df = spark.read.csv(bronze_path, header=True, inferSchema=True)
        print(f"Read {df.count()} customer records from MinIO Bronze.")
    except Exception as e:
        print(f"Error reading bronze data: {e}. Are you sure you ran load_olist.py?")
        return

    # Basic cleaning: drop nulls
    df_clean = df.dropna(subset=['customer_id'])
    
    # We could also write to a Silver layer in S3 here, but for now we write directly to Postgres DW
    
    # PostgreSQL connection
    pg_host = os.getenv("POSTGRES_HOST", "postgres")
    pg_port = os.getenv("POSTGRES_PORT", "5432")
    pg_db = os.getenv("POSTGRES_DB", "ecommerce")
    pg_user = os.getenv("POSTGRES_USER", "ecommerce")
    pg_password = os.getenv("POSTGRES_PASSWORD", "ecommerce")

    jdbc_url = f"jdbc:postgresql://{pg_host}:{pg_port}/{pg_db}"
    
    print("Writing cleaned data to PostgreSQL dw.dim_customer...")
    try:
        df_clean.write \
            .format("jdbc") \
            .option("url", jdbc_url) \
            .option("dbtable", "dw.dim_customer") \
            .option("user", pg_user) \
            .option("password", pg_password) \
            .option("driver", "org.postgresql.Driver") \
            .mode("append") \
            .save()
        print("Successfully written customers data to dw.dim_customer.")
    except Exception as e:
        print(f"Error writing to Postgres: {e}")

def main():
    spark = create_spark_session()
    process_customers(spark)
    spark.stop()
    print("Batch transformation completed successfully.")

if __name__ == "__main__":
    main()
