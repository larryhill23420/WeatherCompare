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
    try:
        resp = zip_table.scan()
        items = resp.get("Items", [])

        # Return a clean list sorted by PlaceName
        zips = [
            {
                "zip": item.get("ZipCode"),
                "placeName": item.get("PlaceName")
            }
            for item in items
        ]
        zips.sort(key=lambda x: x["placeName"] or "")

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(zips, cls=DecimalEncoder)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)})
        }