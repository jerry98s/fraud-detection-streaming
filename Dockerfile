# Start from Bitnami Spark base image
FROM bitnami/spark:latest

USER root

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl

# Install required Python packages
RUN pip3 install --no-cache-dir \
    joblib \
    numpy \
    pandas \
    scikit-learn

# Set environment variables
ENV SPARK_VERSION=3.5.0
ENV SPARK_SCALA_VERSION=2.12
ENV KAFKA_VERSION=3.5.0

# Download Kafka connectors and dependencies
RUN curl -L -o /opt/bitnami/spark/jars/spark-sql-kafka-0-10_${SPARK_SCALA_VERSION}-${SPARK_VERSION}.jar \
    https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_${SPARK_SCALA_VERSION}/${SPARK_VERSION}/spark-sql-kafka-0-10_${SPARK_SCALA_VERSION}-${SPARK_VERSION}.jar && \
    curl -L -o /opt/bitnami/spark/jars/kafka-clients-${KAFKA_VERSION}.jar \
    https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/${KAFKA_VERSION}/kafka-clients-${KAFKA_VERSION}.jar && \
    curl -L -o /opt/bitnami/spark/jars/spark-token-provider-kafka-0-10_${SPARK_SCALA_VERSION}-${SPARK_VERSION}.jar \
    https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_${SPARK_SCALA_VERSION}/${SPARK_VERSION}/spark-token-provider-kafka-0-10_${SPARK_SCALA_VERSION}-${SPARK_VERSION}.jar && \
    curl -L -o /opt/bitnami/spark/jars/commons-pool2-2.11.1.jar \
    https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.1/commons-pool2-2.11.1.jar

# Switch back to non-root user
USER 1001
