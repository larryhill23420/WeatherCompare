import json
import boto3
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource("dynamodb")
reading_table = dynamodb.Table("Reading")
zip_table = dynamodb.Table("ZipCode")

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def get_zip_info(zip_code):
    resp = zip_table.scan(FilterExpression=Attr("ZipCode").eq(zip_code))
    items = resp.get("Items", [])
    if not items:
        return {"placeName": zip_code, "offset": 0}
    item = items[0]
    return {
        "placeName": item.get("PlaceName", zip_code),
        "offset": int(item.get("UtcOffsetSeconds", 0)) // 3600  # hours
    }

def to_local_hour(utc_str, offset_hours):
    dt = datetime.strptime(utc_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    local = dt + timedelta(hours=offset_hours)
    return local.strftime("%Y-%m-%dT%H:00:00")

def lambda_handler(event, context):
    params = event.get("queryStringParameters") or {}
    zip1 = params.get("zip1")
    zip2 = params.get("zip2")
    days = int(params.get("days", "1"))
    days = max(1, min(days, 7))

    if not zip1 or not zip2:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "zip1 and zip2 are required"})
        }

    info1 = get_zip_info(zip1)
    info2 = get_zip_info(zip2)

    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")

    def fetch(zip_code, offset):
        resp = reading_table.scan(
            FilterExpression=Attr("ZipCode").eq(zip_code) & Attr("DateTime").gte(cutoff)
        )
        result = {}
        for item in resp.get("Items", []):
            local_key = to_local_hour(item["DateTime"], offset)
            result[local_key] = item
        return result

    data1 = fetch(zip1, info1["offset"])
    data2 = fetch(zip2, info2["offset"])

    common_times = sorted(set(data1.keys()) & set(data2.keys()))

    rows = []
    for local_dt in common_times:
        r1 = data1[local_dt]
        r2 = data2[local_dt]

        t1 = float(r1.get("Temperature", 0))
        t2 = float(r2.get("Temperature", 0))
        p1 = float(r1.get("Precipitation", 0))
        p2 = float(r2.get("Precipitation", 0))
        h1 = float(r1.get("Humidity", 0))
        h2 = float(r2.get("Humidity", 0))
        c1 = float(r1.get("CloudCover", 0))
        c2 = float(r2.get("CloudCover", 0))

        rows.append({
            "LocalTime": local_dt,
            "ZipCode1": zip1, "PlaceName1": info1["placeName"],
            "Temp1": t1, "TempDiff": round(t1 - t2, 1),
            "Rain1": p1, "RainDiff": round(p1 - p2, 2),
            "Humid1": h1, "HumidDiff": round(h1 - h2, 1),
            "Cloud1": c1, "CloudDiff": round(c1 - c2, 1),
            "ZipCode2": zip2, "PlaceName2": info2["placeName"],
            "Temp2": t2, "Rain2": p2, "Humid2": h2, "Cloud2": c2,
        })

    # --- 7-day summary (always) ---
    summary_cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")

    def fetch_all(zip_code):
        resp = reading_table.scan(
            FilterExpression=Attr("ZipCode").eq(zip_code) & Attr("DateTime").gte(summary_cutoff)
        )
        return resp.get("Items", [])

    def summarize(items):
        if not items:
            return {"avg_temp": None, "high_temp": None, "low_temp": None, "total_precip": 0, "avg_cloud": None}
        temps = [float(i.get("Temperature", 0)) for i in items]
        precips = [float(i.get("Precipitation", 0)) for i in items]
        clouds = [float(i.get("CloudCover", 0)) for i in items]
        return {
            "avg_temp": round(sum(temps) / len(temps), 1),
            "high_temp": round(max(temps), 1),
            "low_temp": round(min(temps), 1),
            "total_precip": round(sum(precips), 2),
            "avg_cloud": round(sum(clouds) / len(clouds), 1)
        }

    summary = {
        "zip1": {"zip": zip1, "place": info1["placeName"], **summarize(fetch_all(zip1))},
        "zip2": {"zip": zip2, "place": info2["placeName"], **summarize(fetch_all(zip2))}
    }

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"summary": summary, "rows": rows}, cls=DecimalEncoder)
    }