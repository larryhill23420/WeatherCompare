import boto3
import json
from datetime import datetime, timedelta, timezone

dynamodb = boto3.resource("dynamodb", region_name="us-west-2")
table = dynamodb.Table("WeatherReadings")

# Last 24 hours in UTC
cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")

response = table.scan(
    FilterExpression="#utc >= :cutoff",
    ExpressionAttributeNames={"#utc": "UTC"},
    ExpressionAttributeValues={":cutoff": cutoff},
)

items = response.get("Items", [])

# Clean up for readability (optional)
clean = []
for item in items:
    clean.append({
        "Zip_UTC": item.get("Zip_UTC"),
        "UTC": item.get("UTC"),
        "LocationName": item.get("LocationName"),
        "CurrentTemp": float(item.get("CurrentTemp", 0)),
        "RelativeHumidity": float(item.get("RelativeHumidity", 0)),
        "CloudCover": float(item.get("CloudCover", 0)),
        "Precipitation": float(item.get("Precipitation", 0)),
    })

# Sort by time
clean.sort(key=lambda x: x["UTC"])

with open("last_24h.json", "w") as f:
    json.dump(clean, f, indent=2)

print(f"Wrote {len(clean)} readings to last_24h.json")