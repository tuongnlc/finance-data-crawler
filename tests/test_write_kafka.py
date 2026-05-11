from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import MessageField, SerializationContext, StringSerializer
import os
import requests
import socket

# 1. Configuration
# 'bootstrap.servers' is the minimum required config
conf = {
    'bootstrap.servers': 'localhost:9094',
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

schema_str = """{
  "type": "record",
  "name": "Order",
  "namespace": "com.example",
  "fields": [
    {"name": "order_id", "type": "string"},
    {"name": "amount", "type": "double"}
  ]
}"""

key_serializer = StringSerializer("utf_8")
value_serializer = AvroSerializer(
    schema_registry_client,
    schema_str,
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
topic = "test-kafka-topic"
key = "user_123"
value = {"order_id": "order_002", "amount": "123.45"}

producer.produce(
    topic, 
    key=key_serializer(key, SerializationContext(topic, MessageField.KEY)),
    value=value_serializer(value, SerializationContext(topic, MessageField.VALUE)),
    callback=delivery_report
)

producer.flush()
