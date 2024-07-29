import os
import json
import struct
from datetime import datetime

from influxdb_client import InfluxDBClient
from influxdb_client.client.exceptions import InfluxDBError
from influxdb_client.client.write_api import SYNCHRONOUS
from wcpp import Packet, Entry

from .handle_packet import handle_packet
from .handle_name import handle_name

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
        return record

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

        return record


def send_packet(data: json):
    data = json.loads(data)
    for key, value in data.items():
        packet_id = handle_name("Grafana", "packet")
        component_id = handle_name("Environment", "component")
        origin_unit_id = handle_name("Ground station", "unit")
        dest_unit_id = handle_name("Tracker", "unit")
        entry_name = handle_name(key, "entry")
        if entry_name == key:
            raise ValueError("Invalid entry name")
        packet = Packet().telemetry(packet_id=ord("Z"), component_id=ord("A"), origin_unit_id=ord("A"), dest_unit_id=ord("A"))
        packet.entries = [
            Entry('Sp').set_float32(float(value))
        ]
        buf = packet.encode()
        return buf