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

# GCloud specific config
PROJECT_ID = "iot-weather-clock"
IOT_CORE_REGION = "europe-west1"
IOT_CORE_REGISTRY_ID = "weather-devices"
IOT_CORE_DEVICE_ID = "d0123710B94CEB0ECFE"

# Location to fetch data from. See yr.no for more information
YR_LOCATION_URL = "https://www.yr.no/place/Norway/Tr%C3%B8ndelag/Trondheim/Trondheim/forecast.xml"

# The cloud storage bucket to store the cached data. See https://console.cloud.google.com/storage for more information
CLOUD_STORAGE_BUCKET_ID = "weather-clock-cache"

# Temperature range for the clock in celsius.
TEMP_MAX = 15
TEMP_MIN = -5

MOTOR_STEP_ANGLE = 1.8
CLOCK_FACE_DEADZONE = 2
