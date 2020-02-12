# (c) 2019 Microchip Technology Inc. and its subsidiaries.
#
#     Subject to your compliance with these terms,you may use this software and
#     any derivatives exclusively with Microchip products.It is your responsibility
#     to comply with third party license terms applicable to your use of third party
#     software (including open source software) that may accompany Microchip software.
#
#     THIS SOFTWARE IS SUPPLIED BY MICROCHIP "AS IS". NO WARRANTIES, WHETHER
#     EXPRESS, IMPLIED OR STATUTORY, APPLY TO THIS SOFTWARE, INCLUDING ANY IMPLIED
#     WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS FOR A
#     PARTICULAR PURPOSE.
#
#     IN NO EVENT WILL MICROCHIP BE LIABLE FOR ANY INDIRECT, SPECIAL, PUNITIVE,
#     INCIDENTAL OR CONSEQUENTIAL LOSS, DAMAGE, COST OR EXPENSE OF ANY KIND
#     WHATSOEVER RELATED TO THE SOFTWARE, HOWEVER CAUSED, EVEN IF MICROCHIP HAS
#     BEEN ADVISED OF THE POSSIBILITY OR THE DAMAGES ARE FORESEEABLE. TO THE
#     FULLEST EXTENT ALLOWED BY LAW, MICROCHIP'S TOTAL LIABILITY ON ALL CLAIMS IN
#     ANY WAY RELATED TO THIS SOFTWARE WILL NOT EXCEED THE AMOUNT OF FEES, IF ANY,
#     THAT YOU HAVE PAID DIRECTLY TO MICROCHIP FOR THIS SOFTWARE.


import xml.etree.ElementTree as ET
from google.cloud import storage
from datetime import datetime
import urllib.request
from googleapiclient import discovery
import base64
from config import PROJECT_ID, IOT_CORE_REGION, IOT_CORE_REGISTRY_ID, IOT_CORE_DEVICE_ID, TEMP_MAX, TEMP_MIN, \
    YR_LOCATION_URL, \
    CLOUD_STORAGE_BUCKET_ID, MOTOR_STEP_ANGLE, CLOCK_FACE_DEADZONE


# Code obtained at https://cloud.google.com
def get_gcloud_client():
    api_version = 'v1'
    discovery_api = 'https://cloudiot.googleapis.com/$discovery/rest'
    service_name = 'cloudiotcore'

    discovery_url = '{}?version={}'.format(
        discovery_api, api_version)

    return discovery.build(
        service_name,
        api_version,
        discoveryServiceUrl=discovery_url,
        credentials=None,
        cache_discovery=False)


# Code obtained at https://cloud.google.com
def send_message_to_device(project_id, cloud_region, registry_id, device_id, payload):
    """
    Sends a message to an IoT Device through the config pubsub topic. (Config pubsub is /devices/d_id/config)
    :param project_id: Google Cloud project ID
    :param cloud_region: Which region is the device located in. For instance us-central1
    :param registry_id: IoT Core Registry the device is loacted in
    :param device_id: The device ID
    :param payload:
    :return:
    """
    client = get_gcloud_client()
    device_path = 'projects/{}/locations/{}/registries/{}/devices/{}'.format(
        project_id, cloud_region, registry_id, device_id)

    config_body = {
        'binaryData': base64.urlsafe_b64encode(
            payload.encode('utf-8')).decode('ascii')
    }

    return client.projects(
    ).locations().registries(
    ).devices().modifyCloudToDeviceConfig(
        name=device_path, body=config_body).execute()


def symbol_to_circle_position(symbol, temperature):
    """
    Converts a YR.no symbol and temperature to a position on a circle (number between 0 and 360).
    :param symbol: Symbol from YR.no API. For instance Clear Sky, Fair, Fog etc
    :param temperature: The temperature from the YR.no API
    :return: A position on a circle. Number between 0 and 360 / MOTOR_STEP_ANGLE
    """
    print("Symbol = {}, T = {}".format(symbol, temperature))
    if temperature > TEMP_MAX:
        temperature = TEMP_MAX
    elif temperature < TEMP_MIN:
        temperature = TEMP_MIN
    temperature_offset = ((temperature - TEMP_MIN) / (TEMP_MAX - TEMP_MIN)) * (36 / MOTOR_STEP_ANGLE)

    category_clear_sky = [1, 2]
    category_partly_cloudy = [3]
    category_cloudy = [4, 15, 3]
    category_rain = [5, 46, 9, 40]
    category_heavy_rain = [41, 10]
    category_snow = [44, 8, 45, 13, 49, 50, 42, 7, 43, 12, 47, 48]
    category_thunder = [24, 6, 25, 26, 20, 27, 28, 21, 29, 11, 14, 22, 30, 31, 32, 33, 34, 23]

    position = 0
    if symbol in category_thunder:
        position = 270 / MOTOR_STEP_ANGLE
    elif symbol in category_clear_sky:
        position = 0
    elif symbol in category_partly_cloudy:
        position = 45 / MOTOR_STEP_ANGLE
    elif symbol in category_cloudy:
        position = 90 / MOTOR_STEP_ANGLE
    elif symbol in category_rain:
        position = 135 / MOTOR_STEP_ANGLE
    elif symbol in category_heavy_rain:
        position = 180 / MOTOR_STEP_ANGLE
    elif symbol in category_snow:
        position = 225 / MOTOR_STEP_ANGLE
    else:
        position = 315 / MOTOR_STEP_ANGLE

    return position + CLOCK_FACE_DEADZONE + temperature_offset


def get_new_yr_data(bucket):
    """
    Downloads new data from YR.no at location YR_LOCATION_URL. Uploads the data as 'forecast.xml' to the given
    cloud storage bucket
    :param bucket: A cloud storage bucket object.
    """
    print("Download new data from YR")
    # Download the data from YR.no
    fp = urllib.request.urlopen(YR_LOCATION_URL)
    bytes = fp.read()
    xml_string = bytes.decode('utf8')
    fp.close()

    # Create root and add the fetched-time node. This information tells us when we lastly downloaded the data.
    root = ET.fromstring(xml_string)
    time_str = datetime.now().strftime("%y:%m:%d %H:%M:%S")
    timestamp_node = ET.Element("timestamp")
    timestamp_node.set("fetched-time", time_str)
    root.append(timestamp_node)

    # Upload the data to the cloud
    xml_string = ET.tostring(root)
    blob = bucket.blob('forecast.xml')
    blob.upload_from_string(xml_string)


def get_forecast_xml():
    """
    Gets the latest weather data XML from YR.no at location YR_LOCATION_URL. Caches the data as 'forecast.xml' in the
    cloud storage bucket CLOUD_STORAGE_BUCKET_ID. If 'forecast.xml' is more than 30 minutes old, fetch a new one.
    :return: An ElementTree root object for the forecast.xml file.
    """
    # Create a connection to the weather-data-avriot bucket
    client = storage.Client()
    bucket = client.get_bucket(CLOUD_STORAGE_BUCKET_ID)

    # Download the forecast.xml
    blob = bucket.get_blob('forecast.xml')

    # Does it exist?
    if blob is None:
        get_new_yr_data(bucket)
        blob = bucket.get_blob('forecast.xml')

    # Extract the XML root
    root = ET.fromstring(blob.download_as_string())

    # Is the data up to date?
    timestamp_str = root.find('timestamp').get('fetched-time')
    timestamp = datetime.strptime(timestamp_str, "%y:%m:%d %H:%M:%S")
    time_delta = datetime.now() - timestamp

    # New data is required
    if time_delta.total_seconds() > 30 * 60:
        get_new_yr_data(bucket)
        blob = bucket.get_blob('forecast.xml')
        root = ET.fromstring(blob.download_as_string())

    return root


def fetch_process_send(request):
    """
    Fetches data from YR.no, processes it and sends a circle position to the device. This is the entry point
    :param topic: MQTT Topic
    :param payload: MQTT Payload
    """
    # Get the forecast xml root
    root = get_forecast_xml()
    times = root.find('forecast').find('tabular')

    # Extract the temperature
    temperature = int(times[1].find('temperature').get('value'))

    # Extract the symbol and convert to circle position
    symbol = int(times[1].find('symbol').get('numberEx'))
    circle_position = symbol_to_circle_position(symbol, temperature)

    # Send the circle position to the device
    payload = '{{"position":"{}"}}'.format(str(int(circle_position)))
    print(payload)
    send_message_to_device(PROJECT_ID, IOT_CORE_REGION, IOT_CORE_REGISTRY_ID, IOT_CORE_DEVICE_ID, payload)