import json
import logging
import os
import time
from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import StringSerializer
from event_generator import EventGenerator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Use kafka:9092 inside docker network, or localhost:29092
KAFKA_BROKER = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:29092')
SCHEMA_REGISTRY_URL = os.getenv('SCHEMA_REGISTRY_URL', 'http://localhost:8081')
TOPIC = 'ecommerce.orders'

def create_producer():
    try:
        # Load Avro schema
        schema_path = os.path.join(os.path.dirname(__file__), 'avro/order_event.avsc')
        with open(schema_path, 'r') as f:
            schema_str = f.read()

        schema_registry_conf = {'url': SCHEMA_REGISTRY_URL}
        schema_registry_client = SchemaRegistryClient(schema_registry_conf)

        avro_serializer = AvroSerializer(
            schema_registry_client,
            schema_str,
            lambda event, ctx: event
        )

        producer_conf = {
            'bootstrap.servers': KAFKA_BROKER,
            'key.serializer': StringSerializer('utf_8'),
            'value.serializer': avro_serializer
        }
        
        return SerializingProducer(producer_conf)
    except Exception as e:
        logger.error(f"Failed to create Confluent Kafka Producer: {e}")
        return None

def main():
    producer = create_producer()
    if not producer:
        logger.error("Could not create Kafka Producer. Exiting.")
        return

    generator = EventGenerator()
    logger.info(f"Starting event generation for topic: {TOPIC}")

    try:
        # Generate 10 events for testing instead of infinite loop
        for _ in range(10):
            event = generator.generate_event()
            partition_key = event['customer_id']
            
            producer.produce(topic=TOPIC, key=partition_key, value=event)
            logger.info(f"Sent event {event['event_id']} ({event['event_type']}) to Kafka with Avro schema.")
            
            # Serve delivery callback queue
            producer.poll(0)
            time.sleep(1)
            
        # Ensure all messages are sent before exiting
        producer.flush()
        logger.info("Successfully sent 10 test events to Kafka.")
    except KeyboardInterrupt:
        logger.info("Stopping event generation...")
        # No close method on SerializingProducer, flush is sufficient

if __name__ == "__main__":
    main()
