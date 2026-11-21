import json
import time
from datetime import datetime, timezone
import requests
import boto3
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=["kafka:9092"],
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

dynamodb = boto3.resource("dynamodb", region_name="us-west-2")
zip_table = dynamodb.Table("ZipCode")

def get_locations():
    """Pull every zip from the ZipCode table."""
    resp = zip_table.scan()
    locations = []
    for item in resp.get("Items", []):
        locations.append({
            "zip": item["ZipCode"],
            "name": item["PlaceName"],
            "lat": float(item["Latitude"]),
            "lon": float(item["Longitude"]),
        })
    return locations

def fetch_and_send():
    locations = get_locations()
    if not locations:
        print("No zip codes found in ZipCode table")
        return

    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    dt_str = now.strftime("%Y-%m-%dT%H:00:00Z")

    for loc in locations:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={loc['lat']}&longitude={loc['lon']}"
            "&current=temperature_2m,relative_humidity_2m,cloud_cover,precipitation"
            "&temperature_unit=fahrenheit"
        )
        try:
            data = requests.get(url, timeout=10).json()["current"]
            message = {
                "Zip_DateTime": f"{loc['zip']}_{dt_str}",
                "DateTime": dt_str,
                "ZipCode": loc["zip"],
                "PlaceName": loc["name"],
                "Temperature": data["temperature_2m"],
                "Humidity": data["relative_humidity_2m"],
                "CloudCover": data["cloud_cover"],
                "Precipitation": data["precipitation"],
            }
            producer.send("weather-readings", message)
            print(f"Sent {message['Zip_DateTime']}")
        except Exception as e:
            print(f"Producer error for {loc['zip']}: {e}")
    producer.flush()

if __name__ == "__main__":
    while True:
        fetch_and_send()
        # Sleep until the next top of the hour
        time.sleep(3600 - (time.time() % 3600))