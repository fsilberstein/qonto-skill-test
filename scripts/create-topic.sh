#!/bin/bash

KAFKA_HOME=/opt/kafka/bin
TOPIC_NAME="companies"

# Wait for Kafka to be ready
$KAFKA_HOME/kafka-topics.sh --bootstrap-server kafka:19092 --list

if $KAFKA_HOME/kafka-topics.sh --bootstrap-server kafka:19092 --list | grep -q "$TOPIC_NAME"; then
  echo "Topic already exists."
else
  # Create Kafka topic
  $KAFKA_HOME/kafka-topics.sh --bootstrap-server kafka:19092 --create --topic "$TOPIC_NAME"

  # Fill it with some events
  $KAFKA_HOME/kafka-console-producer.sh --bootstrap-server kafka:19092 --topic "$TOPIC_NAME" < events.json
fi