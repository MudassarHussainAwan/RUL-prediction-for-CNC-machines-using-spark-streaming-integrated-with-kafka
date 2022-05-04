import json 
import sys
import os
import argparse
from pyspark.sql.types import *
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml.regression import LinearRegressionModel
from pyspark.ml import PipelineModel
from pyspark.sql.functions import explode
from pyspark.sql.functions import split
from kafka import KafkaConsumer
from pyspark.sql.types import *

# define the schema to convert the json string from kafka-producer into orignal datatypes
def get_schema():

    features = ['voltage','current','contact_force','angular_velocity','linear_velocity','cutter_position','F1','F2','beta']
    settings = ['mass','resistance','radius','torque_const','voltage_const','censor']
    schema = StructType()
    for f in features:
            schema.add(f, FloatType())
    schema.add('CNC_id', IntegerType())
    schema.add('cycle', IntegerType())
    for s in settings:
            schema.add(s, FloatType())
    return schema

# Predictor class to perform inference.
# Loads models, transforms the mini batches through pipeline and performs prediction.
class Predictor:

    def __init__(self,config):

        self.config = config
        self.lr_model = LinearRegressionModel.load('/Users/macbook/Desktop/morePro/trained_models/model_lr')
        self.pipeline_model = PipelineModel.load('/Users/macbook/Desktop/morePro/trained_models/model_pipeline')
        

    def ds_predict(self, dataset):
        prepared_df = self.pipeline_model.transform(dataset)
        pred_df = self.lr_model.transform(prepared_df)
        alert_df = pred_df.select('CNC_id','cycle','prediction').filter(F.col('prediction') <= self.config['rulThreshold'])
     
        alert_df \
            .select(
                F.concat(
                    F.col('CNC_id'), F.lit(','), F.col('cycle'), F.lit(','), F.col('prediction')
                    ).alias('value')) \
            .selectExpr("CAST(value AS STRING)") \
            .writeStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "localhost:9092") \
            .option("topic", "CNC-alert")\
            .option("checkpointLocation", "/Users/macbook/Desktop/morePro/Kafka/checkpoint")\
            .start()

        return alert_df





if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--rulThreshold", help="The predicted RUL to alert on", default=100)
    args = parser.parse_args()
    # Kafka Consumer 
    consumer = KafkaConsumer('CNC-stream',bootstrap_servers='localhost:9092',auto_offset_reset='earliest')
    
    # configurations
    config = {"broker": "localhost:9092",
            "topic": "CNC-stream",
            "alertTopic": "CNC-alert",
            "rulThreshold": int(args.rulThreshold)}
    
    # Build a spark session
    spark = SparkSession.builder.appName("Stream-consumer").master("local[2]").getOrCreate()
    
    # read stream of data from the kafka server
    ds = spark.readStream.format("kafka").option("kafka.bootstrap.servers", config["broker"])\
    .option("subscribe", config["topic"]).option("startingOffsets", "latest").load().selectExpr("CAST(value AS STRING)")
    
    # instantiate the predictor class
    predictor = Predictor(config)
    
    # select only the value from the kafka message (corresponds to row of the test data)
    df2 = ds.select(F.split('value', ',').alias('value'))
    # values are 17 as the feature columns of dataset. 
    dataset = df2.select(*[df2['value'][i] for i in range(17)])
    
    schema = get_schema()
    #change column names
    for i, col in enumerate(dataset.columns):
        dataset = dataset.withColumnRenamed(col,schema[i].name)
        
    # Update column type
    for i, name in enumerate(dataset.columns):
        dataset = dataset.withColumn(name, dataset[name].cast(schema[i].dataType))
    
    # perform inference on the stream
    pred_ds = dataset.writeStream.foreachBatch(predictor.ds_predict(dataset)).start()
    
    trans = dataset.writeStream.format("console").start()

    trans.awaitTermination()

    spark.stop()
    print("Done.")
    
    
   