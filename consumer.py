import json
import boto3
from datetime import datetime, timezone
from decimal import Decimal
from kafka import KafkaConsumer

dynamodb = boto3.resource("dynamodb", region_name="us-west-2")
reading_table = dynamodb.Table("Reading")

consumer = KafkaConsumer(
    "weather-readings",
    bootstrap_servers=["kafka:9092"],
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="latest",
    group_id="weather-ingest",
)

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

for message in consumer:
    item = message.value
    try:
        reading_table.put_item(Item={
            "Zip_DateTime": item["Zip_DateTime"],
            "DateTime": item["DateTime"],
            "ZipCode": item["ZipCode"],
            "PlaceName": item["PlaceName"],
            "Temperature": Decimal(str(round(item["Temperature"]))),
            "Precipitation": Decimal(str(item["Precipitation"])),
            "Humidity": Decimal(str(round(item["Humidity"]))),
            "CloudCover": Decimal(str(round(item["CloudCover"]))),
            "InsertedAt": now_iso(),
        })
        print(f"Inserted {item['Zip_DateTime']}")
    except Exception as e:
        print(f"Consumer error: {e}")