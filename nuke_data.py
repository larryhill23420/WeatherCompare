import boto3

dynamodb = boto3.resource("dynamodb", region_name="us-west-2")

def wipe_table(table_name):
    table = dynamodb.Table(table_name)
    key_names = [k["AttributeName"] for k in table.key_schema]

    # Build safe ProjectionExpression and ExpressionAttributeNames
    proj_parts = []
    expr_names = {}
    for i, name in enumerate(key_names):
        placeholder = f"#k{i}"
        proj_parts.append(placeholder)
        expr_names[placeholder] = name

    scan = table.scan(
        ProjectionExpression=",".join(proj_parts),
        ExpressionAttributeNames=expr_names
    )

    with table.batch_writer() as batch:
        for item in scan.get("Items", []):
            key = {k: item[k] for k in key_names}
            batch.delete_item(Key=key)
    print(f"Wiped {table_name}")

if __name__ == "__main__":
    # Comment out any table you want to keep
    wipe_table("Error")
    wipe_table("Reading")
    wipe_table("ZipCode")
    # wipe_table("WeatherReadings")