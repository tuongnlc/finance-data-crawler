from confluent_kafka import Consumer, KafkaError, TopicPartition
from datetime import datetime

conf = {
        'bootstrap.servers': "localhost:9094",
        'group.id': 'gorup12',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False  # Không commit vì chúng ta đang query batch
    }

consumer = Consumer(conf)
topic = "test-kafka-topic"

meta = consumer.list_topics(topic, timeout=5)
partition_ids = meta.topics[topic].partitions.keys()
print(partition_ids) # có 1 partition thi ket qua la dict_keys([0])

tp_list = [TopicPartition(topic, p_id, 0) for p_id in partition_ids]
print(tp_list)

consumer.assign(tp_list)

try:
    while True:
        msg = consumer.poll(1.0) # Đợi 1 giây mỗi lần lấy tin

        if msg is None:
            print("--- Đã hết tin nhắn mới (hoặc hết dữ liệu) ---")
            break

        print(msg.timestamp()[1])
        print(msg.offset())
            
        if msg.error():
            print(f"Lỗi: {msg.error()}")
            break
finally:
    consumer.close()