from kafka import KafkaConsumer
import json
import pandas as pd
from sklearn.ensemble import IsolationForest
import numpy as np

# Set up Kafka consumer
consumer = KafkaConsumer(
    'transactions',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# Store transactions
txn_list = []

# Anomaly detection function
def detect_anomalies(df):
    model = IsolationForest(contamination=0.1, random_state=42)
    df['amount_scaled'] = (df['amount'] - df['amount'].mean()) / df['amount'].std()
    model.fit(df[['amount_scaled']])
    df['anomaly'] = model.predict(df[['amount_scaled']])
    return df[df['anomaly'] == -1]  # Only anomalies

# Alert function
def alert(transaction):
    if 'account_id' in transaction:
        print(f"🚨 ALERT! Fraud detected: {transaction['transaction_id']} of ${transaction['amount']} from {transaction['account_id']}")
    else:
        print(f"🚨 ALERT! Fraud detected: {transaction['transaction_id']} of ${transaction['amount']} — account_id missing!")

# Listen to Kafka
for message in consumer:
    txn = message.value
    txn_list.append(txn)

    if len(txn_list) % 5 == 0:
        df = pd.DataFrame(txn_list)
        print(f"\n📊 Total Txns: {len(df)}, Avg Amount: ${df['amount'].mean():.2f}")

        # Run anomaly detection
        anomalies = detect_anomalies(df)
        if not anomalies.empty:
            print(f"\n🚨 {len(anomalies)} anomalies detected:")
            for _, row in anomalies.iterrows():
                alert(row)
