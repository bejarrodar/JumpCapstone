import json
import urllib.parse
from io import StringIO

import boto3
import pandas as pd

import sqlalchemy

print("Loading function")

s3 = boto3.client("s3")
bucket_name = s3.list_buckets()["Buckets"][1]["Name"]


def lambda_handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(
        event["Records"][0]["s3"]["object"]["key"], encoding="utf-8"
    )
    try:
        print(f"Loading File {key}")
        response = s3.get_object(Bucket=bucket, Key=key)
        df = pd.read_csv(response.get("Body"))
        df = df.dropna()
        filter = df["Quantity Ordered"] != "Quantity Ordered"
        df = df[filter]
        df["Quantity Ordered"] = pd.to_numeric(df["Quantity Ordered"])
        df["month"] = df["Order Date"].str[0:2]
        df["time"] = df["Order Date"].str[-6:-3]
        df["Price Each"] = pd.to_numeric(df["Price Each"])
        df["Order Date"] = pd.to_datetime(df["Order Date"])
        df["Cost"] = df["Price Each"] * df["Quantity Ordered"]
        df["Cost"] = df["Cost"].round(2)
        df["month"] = pd.to_numeric(df["month"])
        df["time"] = pd.to_numeric(df["time"])
        df["city"] = df["Purchase Address"].str.split(", ", expand=True)[1]
        df["Order ID"] = pd.to_numeric(df["Order ID"])
        df = df.astype(
            {"Quantity Ordered": "int8", "Price Each": "float32", "Cost": "float32"}
        )
        csv_buffer = StringIO()
        df.to_csv(csv_buffer)
        s3_object_name = key
        boto3.resource("s3").Object(bucket_name, s3_object_name).put(
            Body=csv_buffer.getvalue()
        )
    except Exception as e:
        print(e)
        print(
            "Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.".format(
                key, bucket
            )
        )
        raise e
