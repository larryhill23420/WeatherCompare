import boto3
from datetime import datetime, timezone
import requests

dynamodb = boto3.resource("dynamodb", region_name="us-west-2")
table = dynamodb.Table("WeatherReadings")

locations = [
    {"zip": "98593", "name": "Vader, WA", "lat": 46.40, "lon": -122.96},
    {"zip": "19422", "name": "Blue Bell, PA", "lat": 40.15, "lon": -75.27},
]

def fetch_and_insert():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:00:00Z")

    for loc in locations:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={loc['lat']}&longitude={loc['lon']}"
            "&current=temperature_2m,relative_humidity_2m,cloud_cover,precipitation"
            "&temperature_unit=fahrenheit"
        )
        data = requests.get(url, timeout=10).json()["current"]

        item = {
            "Zip_UTC": f"{loc['zip']}_{now}",
            "UTC": now,
            "LocationName": loc["name"],
            "CurrentTemp": str(data["temperature_2m"]),
            "RelativeHumidity": str(data["relative_humidity_2m"]),
            "CloudCover": str(data["cloud_cover"]),
            "Precipitation": str(data["precipitation"]),
        }
        table.put_item(Item=item)
        print(f"Inserted {item['Zip_UTC']}")

if __name__ == "__main__":
    fetch_and_insert()