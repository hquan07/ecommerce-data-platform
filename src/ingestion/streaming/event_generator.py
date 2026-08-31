import random
import time
import uuid
from datetime import datetime, timezone

class EventGenerator:
    def __init__(self):
        self.event_types = ['product_viewed', 'cart_added', 'order_created', 'payment_completed']
        self.products = [f"prod_{str(i).zfill(3)}" for i in range(1, 101)]
        
    def generate_event(self):
        event_type = random.choices(
            self.event_types, 
            weights=[0.6, 0.2, 0.1, 0.1]
        )[0]
        
        event = {
            "event_id": f"evt_{uuid.uuid4().hex[:8]}",
            "event_type": event_type,
            "customer_id": f"cust_{random.randint(1000, 9999)}",
            "product_id": random.choice(self.products),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if event_type in ['order_created', 'payment_completed']:
            event["order_id"] = f"ord_{uuid.uuid4().hex[:6]}"
            event["quantity"] = random.randint(1, 5)
            event["unit_price"] = round(random.uniform(10.0, 500.0), 2)
            
        return event
