import time 
import json 
import random 
from datetime import datetime
from kafka import KafkaProducer
from time import sleep
import argparse
from datetime import datetime
from collections import defaultdict
import queue
import random

# loader reads the test data set saved as a csv file in local file system, 
# returns a dictionary of queues for each CNC_id present in the test data and total number of samples available in the csv file.

def loader(filename):
    CNC_machines = defaultdict(queue.Queue)

    total_samples = 0
    with open(filename, "r") as file:
        next(file)
        for line in file:
            # Encode as bytes and strip trailing whitespaces
            CNC_data = line.split(',')
            CNC_id = CNC_data[9]
            CNC_machines[CNC_id].put(line)
            total_samples += 1

    return CNC_machines, total_samples

# randomly choose a CNC_id, choose that queue from the dictionary and get a row from the coresponding queue.
# next time the queue will return the successive row if that queue is chosen randomly.

def get_CNC_machine_cycle(CNC_machines):
    CNC_id = random.choice(list(CNC_machines))
    
    q = CNC_machines[CNC_id]
    c = q.get().strip('\n')
    if q.qsize() == 0:
        del CNC_machines[CNC_id]

    return c


# Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
#    value_serializer=serializer
)




if __name__ == '__main__':
    
    
    rate = 0.5
    
    source = '/Users/macbook/Desktop/morePro/data/test_df.csv'
    
    CNC_machines, num_samples = loader(source)
    count = num_samples
    CNC_machines_cycles = get_CNC_machine_cycle(CNC_machines)
    
    while count > 0 or CNC_machines_cycles is not None:
        # Post to the topic
        print("{}, Sending: {}".format(datetime.now(), CNC_machines_cycles))

        # Encode as bytes and strip trailing whitespaces
        msg = CNC_machines_cycles.rstrip().encode('utf-8')
        producer.send('CNC-stream', msg)
        count -= 1

        # Calculate the delay based on the rate.
        sleep(1.0 / rate)

        CNC_machines_cycles = get_CNC_machine_cycle(CNC_machines)

    # Push put any lingering messages then close
    producer.flush()
    producer.close()