# 🚨 Real-Time Fraud Detection Data Pipeline

## 🧠 Overview
A real-time fraud detection system using Apache Kafka, Apache Spark (Structured Streaming), and a machine learning model (Isolation Forest). The system ingests transaction data, detects fraudulent activities in real-time, sends email alerts for detected frauds, and stores the results in MinIO (S3-compatible storage).

## ⚙️ Architecture
```
               ┌─────────────┐
               │ Kafka Topic │
               └─────┬───────┘
                     │
     ┌───────────────▼────────────────────────┐
     │    Spark Structured Streaming          │
     │ + ML Prediction (Isolation Forest)     │
     └──────┬────────────┬────────────┬───────┘
            │            │            │
     ┌──────▼──────┐  ┌──▼────────┐ ┌─▼────────┐
     │ Console Sink│  │  MinIO    │ │ Email    │
     └─────────────┘  │  Storage  │ │ Alerts   │
                      └───────────┘ └──────────┘
```

## 🗂️ Project Structure
```
fraud-detection-pipeline/
│
├── scripts/
│   ├── kafka_transaction_producer.py      # Sends fake transactions to Kafka
│   ├── train_isolation_forest.py          # Trains the ML model (Isolation Forest)
│   ├── isolation_forest_model.pkl         # Trained ML model
│   └── spark_streaming_consumer.py        # Spark consumer with ML + email alert
│
├── docker-compose.yml                     # Defines all services (Kafka, Spark, MinIO)
├── Dockerfile                             # Builds Spark image with required JARs & libs
├── requirements.txt                       # Python dependencies
├── minio-entrypoint.sh                    # MinIO bucket setup
└── README.md                              # You're here
```

## 🚀 Features
- ✅ Real-time transaction ingestion via Kafka
- ✅ Real-time ML inference (Isolation Forest) in Spark
- ✅ Email alerts for fraud detection
- ✅ Storage of fraudulent transactions in MinIO (Parquet format)
- ✅ Dockerized deployment for easy setup

## 🔧 Setup
### 1. 🧱 Prerequisites
- Docker & Docker Compose
- Python 3.8+
- SMTP credentials for sending emails

### 2. 🐳 Run Services
```bash
git clone https://github.com/your-username/fraud-detection-pipeline.git
cd fraud-detection-pipeline
docker-compose up --build
```

### 3. 🧪 Train ML Model (Optional)
```bash
python scripts/train_isolation_forest.py
```

## ▶️ Running the Pipeline
### Kafka Producer (Simulates transactions)
```bash
python scripts/kafka_transaction_producer.py
```

### Spark Streaming Consumer with ML + Email Alerts
```bash
docker run -it --rm \
  --name spark-consumer \
  --network fintech-fraud_detection-data-pipeline_fintech-network \
  -v ${PWD}/scripts:/scripts \
  -e MINIO_ACCESS_KEY=minio \
  -e MINIO_SECRET_KEY=minio123 \
  -e SMTP_USER=your@email.com \
  -e SMTP_PASS=yourpassword \
  spark-consumer-img \
  spark-submit /scripts/spark_streaming_consumer.py
```

## 💡 Technologies Used
| Component       | Purpose                          |
|----------------|----------------------------------|
| Apache Kafka   | Real-time message streaming      |
| Apache Spark   | Stream processing + ML inference |
| scikit-learn   | Isolation Forest anomaly model   |
| MinIO          | S3-compatible object storage      |
| Python         | Data generation, ML, alerting    |
| Docker         | Container orchestration          |

## 📩 Real-Time Alerts
Fraudulent transactions are detected and emailed using logic embedded inside the Spark Streaming Consumer. Email credentials are loaded from environment variables.

**Example Email:**
```
Subject: 🚨 Fraud Alert

🚨 FRAUD DETECTED 🚨

3b63cb4a-402b - $4500.0 - Declined
```

## 🛠 Future Work
- Add Slack or Telegram alert integration
- Integrate PostgreSQL for audit logging
- Develop a dashboard with Apache Superset or Grafana
- Improve model using temporal patterns or user profiling

## 📜 License
MIT License – feel free to use, modify, and contribute.

