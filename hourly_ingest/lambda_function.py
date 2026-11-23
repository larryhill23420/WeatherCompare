import json
import boto3
import requests
from datetime import datetime, timezone
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
zip_table = dynamodb.Table("ZipCode")
reading_table = dynamodb.Table("Reading")
error_table = dynamodb.Table("Error")

def get_all_zips():
    items = []
    response = zip_table.scan()
    items.extend(response.get("Items", []))
    while "LastEvaluatedKey" in response:
        response = zip_table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response.get("Items", []))
    return items

def fetch_weather(lat, lon, zip_code):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&hourly=temperature_2m,relative_humidity_2m,cloud_cover,precipitation"
        "&temperature_unit=fahrenheit"
        "&forecast_days=1"
    )
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        error_table.put_item(Item={
            "Zip_DateTime": f"{zip_code}_{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:00:00Z')}",
            "Description": f"API error: {str(e)} | URL: {url}"
        })
        return None

def lambda_handler(event, context):
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    dt_str = now.strftime("%Y-%m-%dT%H:00:00Z")

    zips = get_all_zips()
    print(f"Processing {len(zips)} zip codes for {dt_str}")

    for z in zips:
        zip_code = z.get("Zip")
        lat = z.get("Latitude")
        lon = z.get("Longitude")
        place = z.get("PlaceName", "")

        if not lat or not lon:
            continue

        data = fetch_weather(lat, lon, zip_code)
        if not data or "hourly" not in data:
            continue

        hourly = data["hourly"]
        times = hourly.get("time", [])
        temps = hourly.get("temperature_2m", [])
        hums = hourly.get("relative_humidity_2m", [])
        clouds = hourly.get("cloud_cover", [])
        precips = hourly.get("precipitation", [])

        # Find the matching hour
        for i, t in enumerate(times):
            if t.startswith(dt_str[:13]):  # match YYYY-MM-DDTHH
                zip_dt = f"{zip_code}_{dt_str}"
                item = {
                    "Zip_DateTime": zip_dt,
                    "DateTime": dt_str,
                    "ZipCode": zip_code,
                    "PlaceName": place,
                    "Latitude": Decimal(str(lat)),
                    "Longitude": Decimal(str(lon)),
                    "Temperature": Decimal(str(temps[i])) if i < len(temps) else None,
                    "Humidity": Decimal(str(hums[i])) if i < len(hums) else None,
                    "CloudCover": Decimal(str(clouds[i])) if i < len(clouds) else None,
                    "Precipitation": Decimal(str(precips[i])) if i < len(precips) else None,
                }
                # Remove None values
                item = {k: v for k, v in item.items() if v is not None}
                reading_table.put_item(Item=item)
                print(f"Wrote {zip_dt}")
                break

    return {"statusCode": 200, "body": json.dumps(f"Processed {len(zips)} zips")}