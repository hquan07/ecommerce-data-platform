import json
import logging
import os
import time
from kafka import KafkaProducer
from event_generator import EventGenerator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Use kafka:9092 inside docker network
KAFKA_BROKER = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
TOPIC = 'ecommerce.orders'

def create_producer():
    try:
        return KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8')
        )
    except Exception as e:
        logger.error(f"Failed to connect to Kafka broker at {KAFKA_BROKER}: {e}")
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
            
            producer.send(TOPIC, key=partition_key, value=event)
            logger.info(f"Sent event {event['event_id']} ({event['event_type']}) to Kafka.")
            
            time.sleep(1)
            
        # Ensure all messages are sent before exiting
        producer.flush()
        logger.info("Successfully sent 10 test events to Kafka.")
    except KeyboardInterrupt:
        logger.info("Stopping event generation...")
    finally:
        producer.close()

if __name__ == "__main__":
    main()
