from confluent_kafka import Consumer, TopicPartition
import time
from datetime import datetime, timedelta
import os

def query_kafka_by_date(bootstrap_servers, topic, target_date_str):
    """
    target_date_str: "2026-05-01"
    """
    conf = {
        'bootstrap.servers': bootstrap_servers,
        'group.id': 'batch-query-group',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False  # Không commit vì chúng ta đang query batch
    }
    consumer = Consumer(conf)

    # 1. Xác định mốc thời gian Start và End (miliseconds)
    start_dt = datetime.strptime(target_date_str, "%Y-%m-%d")
    end_dt = start_dt + timedelta(days=1)
    
    start_ts = int(time.mktime(start_dt.timetuple()) * 1000)
    end_ts = int(time.mktime(end_dt.timetuple()) * 1000)

    # 2. Lấy danh sách partition
    meta = consumer.list_topics(topic, timeout=10)
    partitions = [TopicPartition(topic, p) for p in meta.topics[topic].partitions.keys()]

    # 3. Tìm Start Offsets và End Offsets
    start_offsets = consumer.offsets_for_times([TopicPartition(topic, p.partition, start_ts) for p in partitions])
    end_offsets = consumer.offsets_for_times([TopicPartition(topic, p.partition, end_ts) for p in partitions])

    print(start_offsets)
    print(end_offsets)

    # Chuyển end_offsets thành dict để tra cứu cho nhanh
    end_offset_dict = {tp.partition: tp.offset for tp in end_offsets}
    

    # 4. Thiết lập Consumer để đọc
    consumer.assign(start_offsets)
    
    records = []
    finished_partitions = set()

    print(f"Bắt đầu đọc dữ liệu ngày {target_date_str}...")
    
    try:
        msg = consumer.poll(timeout=1.0)
        
        if msg.error():
            print(f"Lỗi: {msg.error()}")

        p = msg.partition()
        offset = msg.offset()
        
        # KIỂM TRA ĐIỀU KIỆN DỪNG: 
        # Nếu offset hiện tại >= end_offset của partition đó, ngừng đọc partition này
        limit = end_offset_dict.get(p)
        
        # Nếu limit = -1 nghĩa là từ mốc End_TS tới nay chưa có thêm data, 
        # chúng ta sẽ đọc tới cuối cùng hiện có
        if limit != -1 and offset >= limit:
            finished_partitions.add(p)

        print(finished_partitions)

        if p not in finished_partitions:
            # XỬ LÝ DỮ LIỆU TẠI ĐÂY
            try:
                data = msg.value().decode('utf-8')
            except:
                from confluent_kafka.schema_registry import SchemaRegistryClient

                schema_registry_url = os.getenv("SCHEMA_REGISTRY_URL", "http://localhost:8082").rstrip("/")
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
                
                from confluent_kafka.schema_registry.avro import AvroDeserializer
                avro_deserializer = AvroDeserializer(schema_registry_client, schema_str)
                decoded_data_data = avro_deserializer(msg.value(), None)
                # continue
                data = decoded_data_data

            records.append(data)
    finally:
        consumer.close()
    
    return records

# --- SỬ DỤNG ---
data = query_kafka_by_date("localhost:9094", "test-kafka-topic", "2026-05-09")
print(data)
# print(len(data))