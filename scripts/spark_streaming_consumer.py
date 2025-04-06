import os
import smtplib
import joblib
import numpy as np
from email.mime.text import MIMEText
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, udf
from pyspark.sql.types import StructType, StringType, DoubleType, IntegerType

# Load ML model
model = joblib.load("/scripts/isolation_forest_model.pkl")

def detect_fraud(amount, user_id):
    transaction = np.array([[amount, user_id]])
    prediction = model.predict(transaction)
    return "FRAUD" if prediction[0] == -1 else "LEGIT"

fraud_udf = udf(detect_fraud, StringType())

# Define schema
schema = StructType() \
    .add("transaction_id", StringType()) \
    .add("user_id", IntegerType()) \
    .add("amount", DoubleType()) \
    .add("timestamp", StringType()) \
    .add("merchant", StringType()) \
    .add("location", StringType()) \
    .add("payment_method", StringType()) \
    .add("status", StringType())

# Email alert function
def trigger_alert(df, epoch_id):
    rows = df.toPandas().to_dict(orient="records")
    if not rows:
        return

    body = "\n".join([f"{r['transaction_id']} - ${r['amount']} - {r['status']}" for r in rows])
    msg = MIMEText(f"🚨 FRAUD DETECTED 🚨\n\n{body}")
    msg['Subject'] = 'Fraud Alert'
    msg['From'] = os.getenv("SMTP_USER", "your@email.com")
    msg['To'] = os.getenv("ALERT_RECIPIENT", "alert@recipient.com")

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASS"))
            server.send_message(msg)
            print("✅ Alert email sent.")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

# Spark session
spark = SparkSession.builder \
    .appName("KafkaSparkMLFraudDetection") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", os.getenv("MINIO_ACCESS_KEY")) \
    .config("spark.hadoop.fs.s3a.secret.key", os.getenv("MINIO_SECRET_KEY")) \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .getOrCreate()

# Kafka config
KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC = "transactions_stream"
MINIO_PATH = "s3a://fintech-data/fraudulent_transactions_ml/"
CHECKPOINT_PATH = "s3a://fintech-data/checkpoints/"

# Read from Kafka
raw_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "latest") \
    .option("failOnDataLoss", "false") \
    .load()

# Deserialize and parse
transaction_stream = raw_stream.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

# Fraud detection
predicted_stream = transaction_stream.withColumn(
    "fraud_prediction", fraud_udf(col("amount"), col("user_id"))
)

fraudulent_transactions = predicted_stream.filter(
    col("fraud_prediction") == "FRAUD"
)

# Console sink for debugging
console_query = predicted_stream.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", False) \
    .trigger(processingTime="10 seconds") \
    .start()

# MinIO + alert email sink
minio_query = fraudulent_transactions.writeStream \
    .foreachBatch(trigger_alert) \
    .outputMode("append") \
    .format("parquet") \
    .option("path", MINIO_PATH) \
    .option("checkpointLocation", CHECKPOINT_PATH) \
    .option("mergeSchema", "true") \
    .trigger(processingTime="10 seconds") \
    .start()

console_query.awaitTermination()
minio_query.awaitTermination()
