import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
zip_table = dynamodb.Table("ZipCode")

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def lambda_handler(event, context):
    resp = zip_table.scan()
    items = resp.get("Items", [])

    zips = [
        {"zip": item.get("ZipCode"), "placeName": item.get("PlaceName")}
        for item in items
    ]
    zips.sort(key=lambda x: x["placeName"] or "")

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(zips, cls=DecimalEncoder)
    }