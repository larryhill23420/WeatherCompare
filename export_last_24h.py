import boto3
import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal

dynamodb = boto3.resource("dynamodb", region_name="us-west-2")
table = dynamodb.Table("Reading")

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")

response = table.scan(
    FilterExpression="#dt >= :cutoff",
    ExpressionAttributeNames={"#dt": "DateTime"},
    ExpressionAttributeValues={":cutoff": cutoff},
)

items = response.get("Items", [])
items.sort(key=lambda x: (x.get("ZipCode", ""), x.get("DateTime", "")))

with open("last_24h.json", "w") as f:
    json.dump(items, f, indent=2, cls=DecimalEncoder)

print(f"Wrote {len(items)} readings to last_24h.json")