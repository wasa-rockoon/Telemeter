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
delete_api = influxdb_client.delete_api()


def kill_rockoon():
    delete_api.delete(
        start="1970-01-01T00:00:00Z",
        stop=datetime.utcnow().isoformat() + "Z",
        predicate='',
        bucket="rockoon",
    )

def killEmAll():
    buckets = bucket_api.find_buckets().buckets
    buckets_created_by_user = [bucket for bucket in buckets if bucket.type == "user"]
    for bucket in buckets_created_by_user:
        try:
            if bucket.name == "rockoon":
                continue
            bucket_api.delete_bucket(bucket.id)
        except InfluxDBError as e:
            print(f"InfluxDBError: {e}")

    kill_rockoon()

killEmAll()