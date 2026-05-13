from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import MessageField, SerializationContext
import os
import requests
import socket
import time
import uuid

# 1. Configuration
# 'bootstrap.servers' is the minimum required config
conf = {
    'bootstrap.servers': ['localhost:9094', 'localhost:9095'],
    'client.id': socket.gethostname()
}

schema_registry_url = os.getenv("SCHEMA_REGISTRY_URL", "http://localhost:8082").rstrip("/")

def assert_schema_registry_running(url: str) -> None:
    resp = requests.get(f"{url}/subjects", timeout=5)
    if resp.status_code == 404:
        raise RuntimeError(
            f"Schema Registry endpoint not found at {url} (GET /subjects returned 404). "
            f"Make sure SCHEMA_REGISTRY_URL points to Confluent Schema Registry, not Kafka UI."
        )
    resp.raise_for_status()


assert_schema_registry_running(schema_registry_url)

schema_registry_conf = {
    'url': schema_registry_url,
}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

key_schema_str = """{
  "type": "record",
  "name": "CrawlErrorLogKey",
  "namespace": "com.finance_ai.market_data",
  "fields": [
    {"name": "partition_key", "type": "string"}
  ]
}"""

value_schema_str = """{
  "type": "record",
  "name": "CrawlErrorLog",
  "namespace": "com.finance_ai.market_data",
  "fields": [
    {"name": "event_id", "type": "string"},
    {"name": "event_time", "type": {"type": "long", "logicalType": "timestamp-millis"}},
    {"name": "service", "type": "string"},
    {"name": "crawler_name", "type": "string"},
    {"name": "job_name", "type": "string"},
    {"name": "error_type", "type": "string"},
    {"name": "error_message", "type": "string"},
    {"name": "stage", "type": "string"},
    {"name": "partition_key", "type": "string"}
  ]
}"""

key_serializer = AvroSerializer(
    schema_registry_client,
    key_schema_str,
    to_dict=lambda obj, ctx: obj,
)
value_serializer = AvroSerializer(
    schema_registry_client,
    value_schema_str,
    to_dict=lambda obj, ctx: obj,
)

# 2. Create Producer instance
producer = Producer(conf)


def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

# 4. Produce a message (Asynchronous)
topic = "crawl-error-log"
partition_key = "CrawlStockIndex"
key = {"partition_key": partition_key}
value = {
    "event_id": str(uuid.uuid4()),
    "event_time": int(time.time() * 1000),
    "service": "finance-data-crawler",
    "crawler_name": "CrawlStockIndex",
    "job_name": "crawl_stock_index",
    "error_type": "TimeoutError",
    "error_message": "Page.goto: Timeout 30000ms exceeded",
    "stage": "goto",
    "partition_key": partition_key,
}

producer.produce(
    topic, 
    key=key_serializer(key, SerializationContext(topic, MessageField.KEY)),
    value=value_serializer(value, SerializationContext(topic, MessageField.VALUE)),
    callback=delivery_report
)

producer.flush()
