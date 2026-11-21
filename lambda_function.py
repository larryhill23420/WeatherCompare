import json
import boto3
from datetime import datetime, timedelta, timezone
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("WeatherReadings")

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def lambda_handler(event, context):
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")

    response = table.scan(
        FilterExpression="#utc >= :cutoff",
        ExpressionAttributeNames={"#utc": "UTC"},
        ExpressionAttributeValues={":cutoff": cutoff},
    )

    items = response.get("Items", [])
    items.sort(key=lambda x: x.get("UTC", ""))

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(items, cls=DecimalEncoder)
    }