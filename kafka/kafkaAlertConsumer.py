import json 
from kafka import KafkaConsumer
from datetime import datetime

if __name__ == '__main__':
    # Kafka Consumer 
    consumer = KafkaConsumer(
        'CNC-alert',
        bootstrap_servers="localhost:9092",
        #auto_offset_reset='earliest'
    )
    for msg in consumer:
        print("Alert Received: {}: {}".format( datetime.now(), msg.value))
