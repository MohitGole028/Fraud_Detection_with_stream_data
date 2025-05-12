from kafka import KafkaProducer
import json
import time
import random
from datetime import datetime

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_transaction():
    return {
        "transaction_id": random.randint(100000, 999999),
        "user_id": random.randint(1000, 9999),
        "amount": round(random.uniform(10.0, 1000.0), 2),
        "timestamp": datetime.utcnow().isoformat(),
        "location": random.choice(["New York", "London", "Mumbai", "Tokyo", "Sydney"]),
        "is_fraud": random.choice([0, 1, 0, 0, 0])  # Simulate rare fraud
    }

if __name__ == "__main__":
    while True:
        transaction = generate_transaction()
        print(f"Sending: {transaction}")
        producer.send('transactions', transaction)
        time.sleep(1)
