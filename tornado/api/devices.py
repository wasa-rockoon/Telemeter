from cgi import print_environ
import configparser
import json
import os
import struct
from datetime import datetime
from uuid import uuid4
from influxdb_client import Authorization, InfluxDBClient, Permission, PermissionResource, Point, WriteOptions
from influxdb_client.client.authorizations_api import AuthorizationsApi
from influxdb_client.client.bucket_api import BucketsApi
from influxdb_client.client.flux_table import FluxStructureEncoder
from influxdb_client.client.query_api import QueryApi
from influxdb_client.client.write_api import SYNCHRONOUS

from api.sensor import Sensor
from influxdb_client.domain.dialect import Dialect
from dotenv import load_dotenv  # Import load_dotenv from python-dotenv

from .binary_to_float import binary_to_float

URL = os.getenv("INFLUX_URL")
TOKEN = os.getenv("INFLUX_TOKEN")
ORG = os.getenv("INFLUX_ORG")
BUCKET = os.getenv("INFLUX_BUCKET")

def write_measurement(power_current):
    

    influxdb_client = InfluxDBClient(url=URL,
                                     token=TOKEN,
                                     org=ORG)
    write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
    virtual_device = Sensor()
    coord = virtual_device.geo()

    power_current = binary_to_float(power_current)


    point = Point("environment") \
        .tag("device", "esp32") \
        .tag("TemperatureSensor", "virtual_bme280") \
        .tag("HumiditySensor", "virtual_bme280") \
        .tag("PressureSensor", "virtual_bme280") \
        .tag("flightID", "2024-06-20") \
        .field("power_current", power_current) \
        .field("Lat", coord['latitude']) \
        .field("Lon", coord['latitude']) \
        .time(datetime.utcnow())

    print(f"Writing: {point.to_line_protocol()}")
    client_response = write_api.write(bucket=BUCKET, record=point, org=ORG)

    # write() returns None on success
    if client_response is None:
        # TODO Maybe also return the data that was written
        return power_current

    # Return None on failure
    return None




