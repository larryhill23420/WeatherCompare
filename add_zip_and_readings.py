import boto3
import requests
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

dynamodb = boto3.resource("dynamodb", region_name="us-west-2")
zip_table = dynamodb.Table("ZipCode")
reading_table = dynamodb.Table("Reading")
error_table = dynamodb.Table("Error")

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def log_error(zip_dt: str, description: str):
    error_table.put_item(Item={
        "UUID": str(uuid.uuid4()),
        "Zip_DateTime": zip_dt,
        "Description": description,
        "InsertedAt": now_iso()
    })

def add_zip_and_backfill(zip_code: str):
    # 1. Look up zip
    zip_url = f"https://api.zippopotam.us/us/{zip_code}"
    try:
        resp = requests.get(zip_url, timeout=10)
        resp.raise_for_status()
        z = resp.json()
        place = z["places"][0]
        place_name = f"{place['place name']}, {place['state abbreviation']}"
        lat = place["latitude"]
        lon = place["longitude"]
    except Exception as e:
        log_error(f"{zip_code}_ZIP_LOOKUP", f"Zippopotam failed: {zip_url} | {str(e)}")
        print(f"Zip lookup failed for {zip_code}")
        return

    # 2. EXISTS check — skip everything if zip already present
    existing = zip_table.get_item(Key={"ZipCode": zip_code, "PlaceName": place_name})
    if "Item" in existing:
        print(f"Zip {zip_code} already exists — skipping ZipCode and Readings")
        return

    # 3. Insert into ZipCode
    zip_table.put_item(Item={
        "ZipCode": zip_code,
        "PlaceName": place_name,
        "Latitude": lat,
        "Longitude": lon,
        "InsertedAt": now_iso()
    })
    print(f"Inserted ZipCode: {zip_code} - {place_name}")

    # 4. Backfill readings from midnight 2026-11-21 through current hour
    now = datetime.now(timezone.utc)
    start = datetime(2026, 11, 21, 0, 0, 0, tzinfo=timezone.utc)
    current = start

    while current <= now:
        dt_str = current.strftime("%Y-%m-%dT%H:00:00Z")
        zip_dt = f"{zip_code}_{dt_str}"
        date_str = current.strftime("%Y-%m-%d")

        weather_url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            "&hourly=temperature_2m,relative_humidity_2m,cloud_cover,precipitation"
            "&temperature_unit=fahrenheit"
            f"&start_date={date_str}&end_date={date_str}"
            "&timezone=UTC"
        )

        try:
            wresp = requests.get(weather_url, timeout=10)
            wresp.raise_for_status()
            w = wresp.json()
            hourly = w.get("hourly", {})
            times = hourly.get("time", [])
            temps = hourly.get("temperature_2m", [])
            hums = hourly.get("relative_humidity_2m", [])
            clouds = hourly.get("cloud_cover", [])
            precips = hourly.get("precipitation", [])

            # Find the index that matches our target hour
            target = dt_str[:13]  # "2026-11-21T19"
            idx = next((i for i, t in enumerate(times) if t.startswith(target)), None)
            
            print(f"DEBUG {dt_str}  idx={idx}  times_sample={times[:2] if times else None}")
            if idx is None:
                print(f"DEBUG no match for {target}")

            if idx is None or not temps:
                raise ValueError(f"No data for hour {dt_str}")

            reading_table.put_item(Item={
                "Zip_DateTime": zip_dt,
                "DateTime": dt_str,
                "ZipCode": zip_code,
                "PlaceName": place_name,
                "Temperature": Decimal(str(round(temps[idx]))),
                "Precipitation": Decimal(str(precips[idx] if precips else 0)),
                "Humidity": Decimal(str(round(hums[idx]))) if hums else Decimal("0"),
                "CloudCover": Decimal(str(round(clouds[idx]))) if clouds else Decimal("0"),
                "InsertedAt": now_iso()
            })
            print(f"Inserted reading {zip_dt}")

        except Exception as e:
            log_error(zip_dt, f"Weather API failed: {weather_url} | {str(e)}")
            print(f"Error on {zip_dt}: {e}")

        current += timedelta(hours=1)

if __name__ == "__main__":
    add_zip_and_backfill("98593")   # Vader
    add_zip_and_backfill("19422")   # Blue Bell