import json
import urllib.parse

import boto3
import pandas as pd

import sqlalchemy

print("Loading function")

host = ""
port = 3306
user = "root"
passw = "rootroot"
database = "Sales"

s3 = boto3.client("s3")

url = f"mysql+mysqlconnector://{user}:{passw}@{host}:{port}/{database}"
engine = sqlalchemy.create_engine(url)


def lambda_handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(
        event["Records"][0]["s3"]["object"]["key"], encoding="utf-8"
    )
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        df = pd.read_csv(response.get("Body"))
        df.to_sql(key.split(".")[0].split("_")[1], engine, if_exists="fail")
    except Exception as e:
        print(e)
        print(
            "Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.".format(
                key, bucket
            )
        )
        raise e
