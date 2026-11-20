import json
import time
from datetime import datetime, timezone
import requests
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=["kafka:9092"],
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

locations = [
    {"zip": "98593", "name": "Vader, WA", "lat": 46.40, "lon": -122.96},
    {"zip": "19422", "name": "Blue Bell, PA", "lat": 40.15, "lon": -75.27},
]

def fetch_weather():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:00:00Z")
    for loc in locations:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={loc['lat']}&longitude={loc['lon']}"
            "&current=temperature_2m,relative_humidity_2m,cloud_cover,precipitation"
            "&temperature_unit=fahrenheit"
        )
        data = requests.get(url, timeout=10).json()["current"]
        message = {
            "Zip_UTC": f"{loc['zip']}_{now}",
            "UTC": now,
            "LocationName": loc["name"],
            "CurrentTemp": data["temperature_2m"],
            "RelativeHumidity": data["relative_humidity_2m"],
            "CloudCover": data["cloud_cover"],
            "Precipitation": data["precipitation"],
        }
        producer.send("weather-readings", message)
        print(f"Sent {message['Zip_UTC']}")
    producer.flush()

if __name__ == "__main__":
    while True:
        fetch_weather()
        # Sleep until the next top of the hour
        time.sleep(3600 - (time.time() % 3600))