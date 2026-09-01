import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, expr
from pyspark.sql.avro.functions import from_avro

def main():
    KAFKA_BROKER = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
    TOPIC = 'ecommerce.orders'
    
    # Read local schema for from_avro
    schema_path = os.path.join(os.path.dirname(__file__), '../../ingestion/streaming/avro/order_event.avsc')
    with open(schema_path, 'r') as f:
        avro_schema = f.read()

    spark = SparkSession.builder \
        .appName("Ecommerce Order Streaming Consumer") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.spark:spark-avro_2.12:3.5.0") \
        .getOrCreate()
        
    spark.sparkContext.setLogLevel("WARN")
    
    print(f"Connecting to Kafka at {KAFKA_BROKER}, topic: {TOPIC}")

    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BROKER) \
        .option("subscribe", TOPIC) \
        .option("startingOffsets", "earliest") \
        .load()

    # Confluent Avro encoding: 1 byte magic number (0x00) + 4 bytes schema ID + Avro payload
    # We strip the first 5 bytes using substring
    avro_df = df.withColumn("fixed_value", expr("substring(value, 6, length(value)-5)"))
    
    # Parse Avro payload using the provided schema
    parsed_df = avro_df.select(
        from_avro(col("fixed_value"), avro_schema).alias("data")
    ).select("data.*")
    
    print("Starting streaming query...")
    
    # Write to console for debugging/demo purposes
    query = parsed_df.writeStream \
        .outputMode("append") \
        .format("console") \
        .start()
        
    query.awaitTermination()

if __name__ == "__main__":
    main()
