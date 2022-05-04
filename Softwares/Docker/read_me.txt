Download docker from the website: 
https://www.docker.com/get-started/

# Youtube link
https://www.youtube.com/watch?v=4xFZ_iTZLTs&list=LL&index=4&t=216s

$ docker --version
$ docker-compose --version

# Images required: zookeeper, kafka from Docker hub

$ docker-compose -f docker-compose.yml up -d
$ docker ps


$ docker exec -it kafka /bin/sh
# ls

# Kafka shells are located in:
# cd /opt/kafka_2.13-2.8.1/bin

# To create a new topic
# kafka-topics.sh --create --zookeeper zookeeper:2181 --replication-factor 1 --partitions 1 --topic <Topic_name> 
# kafka-topics.sh --list --zookeeper zookeeper:2181

# kafka-console-producer.sh --broker-list kafka:9092 --topic message
# kafka-console-consumer.sh --bootstrap-server kafka:9092 --topic message
