import json
import boto3
from kafka import KafkaConsumer

dynamodb = boto3.resource("dynamodb", region_name="us-west-2")
table = dynamodb.Table("WeatherReadings")

consumer = KafkaConsumer(
    "weather-readings",
    bootstrap_servers=["kafka:9092"],
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest",
    group_id="weather-ingest",
)

for message in consumer:
    item = message.value
    # DynamoDB wants numbers as strings in the low-level format, but boto3 resource accepts natives
    table.put_item(Item={
        "Zip_UTC": item["Zip_UTC"],
        "UTC": item["UTC"],
        "LocationName": item["LocationName"],
        "CurrentTemp": str(item["CurrentTemp"]),
        "RelativeHumidity": str(item["RelativeHumidity"]),
        "CloudCover": str(item["CloudCover"]),
        "Precipitation": str(item["Precipitation"]),
    })
    print(f"Inserted {item['Zip_UTC']}")