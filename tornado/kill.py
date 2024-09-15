import json
import os
from datetime import datetime

from influxdb_client import InfluxDBClient
from influxdb_client.client.exceptions import InfluxDBError
from influxdb_client.client.write_api import SYNCHRONOUS

URL = os.getenv("INFLUX_URL")
TOKEN = os.getenv("INFLUX_TOKEN")
ORG = os.getenv("INFLUX_ORG")

# Check if environment variables are set
if not URL or not TOKEN or not ORG:
    raise ValueError("Environment variables INFLUX_URL, INFLUX_TOKEN, and INFLUX_ORG must be set")

# Define InfluxDB client
influxdb_client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
query_api = influxdb_client.query_api()
bucket_api = influxdb_client.buckets_api()

def killEmAll():
    buckets = bucket_api.find_buckets().buckets
    for bucket in buckets:
        try:
            bucket_api.delete_bucket(bucket.id)
        except InfluxDBError as e:
            print(f"InfluxDBError: {e}")

    bucket_api.create_bucket(
        bucket_name="rockoon",
        org_id=ORG,
        description="Bucket created at" + str(datetime.utcnow()),
    )

killEmAll()