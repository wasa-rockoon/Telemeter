import os
import struct
from datetime import datetime

from influxdb_client import InfluxDBClient
from influxdb_client.client.exceptions import InfluxDBError
from influxdb_client.client.write_api import SYNCHRONOUS
from wcpp import Packet

from .binary_to_float import binary_to_float
from .handle_packet import handle_packet

URL = os.getenv("INFLUX_URL")
TOKEN = os.getenv("INFLUX_TOKEN")
ORG = os.getenv("INFLUX_ORG")

# Define InfluxDB client
influxdb_client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
bucket_api = influxdb_client.buckets_api()

# Find latest bucket created by user
buckets = bucket_api.find_buckets().buckets
buckets_created_by_user = [bucket for bucket in buckets if bucket.type == "user"]
bucket = max(buckets_created_by_user, key=lambda x: x.updated_at).name


def write_measurement(buf: bytes):

    # Extracting record from binary buffer
    try:
        packet = Packet.decode(buf)
    except Exception as e:
        return repr(e)

    # Creating records for InfluxDB from packets
    record = handle_packet(packet)

    global bucket
    try:
        write_api.write(bucket=bucket, record=record, org=ORG)
        return None

    except InfluxDBError as e:
        # Storing error log into existing bucket
        error_record = {
            "measurement": "error",
            "fields": {"error": repr(e)},
        }
        write_api.write(bucket=bucket, record=error_record, org=ORG)

        # Create new bucket for receiving record
        bucket = "rockoon" + str(datetime.utcnow())
        bucket_api.create_bucket(
            bucket_name="rockoon" + str(datetime.utcnow()),
            org_id=ORG,
            description="Bucket created at" + str(datetime.utcnow()),
        )
        write_api.write(bucket=bucket, record=record, org=ORG)

        return None
