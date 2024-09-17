import urllib.request
import urllib.parse

import os

from influxdb_client import InfluxDBClient

URL = os.getenv("INFLUX_URL")
TOKEN = os.getenv("INFLUX_TOKEN")
ORG = os.getenv("INFLUX_ORG")

# Define InfluxDB client
influxdb_client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
query_api = influxdb_client.query_api()
# write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
# delete_api = influxdb_client.delete_api()
bucket_api = influxdb_client.buckets_api()

# Find latest bucket created by user
buckets = bucket_api.find_buckets().buckets
buckets_created_by_user = [bucket for bucket in buckets if bucket.type == "user"]
bucket = max(buckets_created_by_user, key=lambda x: x.updated_at).name

# def get_jst_rfc3339():

#     # Get current time in UTC
#     utc_now = datetime.utcnow()

#     # Define the JST timezone using pytz
#     jst_timezone = pytz.timezone('Asia/Tokyo')

#     # Convert UTC time to JST
#     jst_time = pytz.utc.localize(utc_now).astimezone(jst_timezone)

#     # Return the time formatted as RFC3339 (isoformat handles this automatically)
#     return jst_time.isoformat()

# async def make_prediction_request(lat, lon, launch_datetime, launch_altitude, ascent_rate, burst_altitude, descent_rate):
#     # Constructing query parameters
#     query_params = {
#         'launch_latitude': lat,
#         'launch_longitude': lon,
#         'launch_datetime': launch_datetime,
#         'launch altitude': launch_altitude,
#         'ascent_rate': ascent_rate,
#         'burst_altitude': burst_altitude,
#         'descent_rate': descent_rate
#     }

#     # Properly encode the query parameters
#     encoded_params = urllib.parse.urlencode(query_params)

#     # Constructing the full URL
#     url = f'https://api.v2.sondehub.org/tawhiri?{encoded_params}'

#     http_client = AsyncHTTPClient()
#     response = await http_client.fetch(url)
#     response_body = response.body.decode('utf-8')
#     response_json = json.loads(response_body)
#     return response_json
    

# def print_json_fragments(response_json):
#     # Check if the response contains an error fragment
#     if 'error' in response_json:
#         print("\nError Fragment:")
#         print(json.dumps(response_json['error'], indent=4))
#     else:
#         # Print metadata fragment
#         if 'metadata' in response_json:
#             print("\nMetadata Fragment:")
#             print(json.dumps(response_json['metadata'], indent=4))

#         # Print prediction fragment
#         if 'prediction' in response_json:
#             print("\nPrediction Fragment:")
#             for stage in response_json['prediction']:
#                 print(f"Stage: {stage['stage']}")
#                 for point in stage['trajectory']:
#                     print(f"  Altitude: {point['altitude']}m, Latitude: {point['latitude']}, Longitude: {point['longitude']}, Datetime: {point['datetime']}")
#             return response_json['prediction']

#         # Print request fragment
#         if 'request' in response_json:
#             print("\nRequest Fragment:")
#             print(json.dumps(response_json['request'], indent=4))

def get_values():
    query = 'from(bucket: "rockoon") |> range(start: -1m)\
        |> filter(fn: (r) => r._measurement == "tracker")\
        |> filter(fn: (r) => r._field == "latitude" or r._field == "longitude" or r._field == "pressure altitude")\
        |> last()'
    
    result = query_api.query(query=query, org=ORG)
    results = {}
    for table in result:
        for record in table.records:
            results[record.get_field()] = record.get_value()
    results["time"] = record.get_time().isoformat()

    query_params = {
        'launch_latitude': results["latitude"],
        'launch_longitude': results["longitude"],
        'launch_datetime': results["time"],
        'launch altitude': results["pressure altitude"],
        'ascent_rate': 5.0,
        'burst_altitude': 20000,
        'descent_rate': 5.0,
        'profile': 'standard_profile',
        'prediction_type': "Gaussian_distribution"
    }
    encoded_params = urllib.parse.urlencode(query_params)
    url = f'https://wasa-rockoon.github.io/Falling-position-simulator/?{encoded_params}'

    print(url)
    return url
    
    

# async def predict():
#     # Define the launch site coordinates
#     lat = -36.848461
#     lon = 174.763336

#     # Get the current time in JST
#     launch_datetime = get_jst_rfc3339()

#     data = get_values()
#     launch_latitude = data["latitude"]
#     launch_longitude = data["longitude"]
#     launch_altitude = data["pressure altitude"]
#     launch_datetime = data["time"]


#     # Define the ascent rate, burst altitude, and descent rate
#     ascent_rate = 5.0
#     burst_altitude = 30000.0
#     descent_rate = 5.0

#     # Make the prediction request
#     response_json = await make_prediction_request(lat=launch_latitude, lon=launch_longitude, launch_datetime=launch_datetime, launch_altitude=launch_altitude, ascent_rate=ascent_rate, burst_altitude=burst_altitude, descent_rate=descent_rate)

#     # Print the JSON fragments
#     plots = print_json_fragments(response_json)

#     for stage in plots:
#         for point in stage['trajectory']:
#             record = {
#                 'measurement': "prediction",
#                 'tags': {},
#                 'fields': {
#                     'altitude': point['altitude'],
#                     'latitude': point['latitude'],
#                     'longitude': point['longitude'],
#                 }
#             }
#             write_api.write(bucket=bucket, record=record, org=ORG)

# get_values()