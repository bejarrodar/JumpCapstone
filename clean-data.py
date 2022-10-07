import os

import boto3
import pandas as pd

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN,
)
bucket = s3_client.list_buckets()["Buckets"]
while True:
    print("Which bucket would you like to pull from:")
    for i in range(len(bucket)):
        print(f"[{i}] {bucket[i]['Name']}")
    sel = input()
    try:
        sel = int(sel)
    except ValueError:
        print("Please Enter a number")
    if sel in range(len(bucket)):
        sel_bucket = bucket[sel]["Name"]
        print(f"Bucket selected {sel_bucket}")
        break
    else:
        print("Please enter a valid number")

files = s3_client.list_objects(Bucket=sel_bucket)["Contents"]
while True:
    print("Which File Would you like: ")
    for i in range(len(files)):
        print(f"[{i}] {files[i]['Key']}")
    file = input()
    try:
        file = int(file)
    except ValueError:
        print("Please enter a number")
    if file in range(len(files)):
        sel_file = files[file]["Key"]
        print(f"File Selected {sel_file}")
        break
    else:
        print("Please enter a valid number")
response = s3_client.get_object(Bucket=sel_bucket, Key=sel_file)
status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

if status == 200:
    print(f"Successful S3 get_object response. Status - {status}")
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
    df.to_csv(sel_file)

else:
    print(f"Unsuccessful S3 get_object response. Status - {status}")
