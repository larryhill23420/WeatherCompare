import boto3
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource("dynamodb", region_name="us-west-2")
table = dynamodb.Table("Reading")

resp = table.scan(FilterExpression=Attr("ZipCode").eq("19422"))
items = sorted(resp["Items"], key=lambda x: x["Zip_DateTime"])
for i in items:
    print(i["Zip_DateTime"])
print(f"Total: {len(items)}")
