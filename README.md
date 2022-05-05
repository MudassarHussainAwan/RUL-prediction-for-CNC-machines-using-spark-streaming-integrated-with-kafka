# Remianing Useful Life (RUL) prediction for CNC machines using spark streaming integrated with kafka
This project simulates RUL prediction for CNC machines in real time. The project is divided in two parts. First part is regarding preparing the data and training the model on the cloud. The second part makes prediction using spark streaming API integrated with kafka once the trained model is downloaded in the local file system.
![](images/spark_streaming.png)
# Software Description
Java 11 is recommmended as pyspark is not compatible with the more recent versions. More on this in [read_me](Softwares/java%2011/read_me.txt).
Spark version 3.1.3 can be downloaded from ![Link](https://spark.apache.org/downloads.html). Version pre-built with scala 2.12 is recommended.   

To run Kafka and zookeeper, download docker image from [Link](https://www.docker.com/products/docker-desktop/)   
Docker compose is not needed to be installed separatley for mac os. To verify the installation enter following command in the terminal:
```bash
$ docker --version
$ docker-compose --version

```

In order to create kafka and zookeeper containers, Run the [docker-compose.yml](Softwares/Docker/docker-compose.yml) file using following command. The script will create kafka topics as well namely : CNC-stream and CNC-alert.
```bash
$ docker-compose -f docker-compose.yml up -d

```
To open an interactive shell in the kafka container:
```bash
$ docker exec -it kafka /bin/sh

```
Existing kafka topics can be enlisted using the following command:
```bash
# kafka-topics.sh --list --zookeeper zookeeper:2181

```
We may also create new topic with:
```bash
# kafka-topics.sh --create --zookeeper zookeeper:2181 --replication-factor 1 --partitions 1 --topic <Topic_name> 

```


# Run Locally:
To run the simulations run the following commands in separate terminals simultaneously (Make sure you are in the [repository](/kafka) where .py files are located):

 ```bash
$ spark-submit --master local[2] --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.3,org.apache.spark:spark-streaming-kafka-0-10_2.12:3.1.3 kafkaStreamConsumer.py -r 110

$ python3 kafkaAlertConsumer.py
$ python3 KafkaProducer.py

```
