# Copyright 2020 Google LLC. This software is provided as is, without
# warranty or representation for any use or purpose. Your use of it is
# subject to your agreement with Google.
import os

ENVIRONMENT = 'dev' # ['cdot', 'rtdh', 'dev' <-- this one ]

RTDH_PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT', f'cdot-rtdh-{ENVIRONMENT}')
ADAP_PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT', f'cdot-adap-{ENVIRONMENT}')

HAAS_ALERT_RAW_TABLE_NAME = f'cdot-adap-{ENVIRONMENT}.haas_alert_raw'
HEARTBEAT_TABLE = "websocket_heartbeat"
LOCATION_TABLE = "websocket_location"
POINT_TABLE = "websocket_point"
THING_TABLE = "websocket_thing"

RTDH_STORAGE_BUCKET_NAME = f'cdot-rtdh-{ENVIRONMENT}-haas-alert-websocket-raw'
SCHEMA_VERSION = 1

# gs://cdot-rtdh-test-haas-alert-websocket-raw/point/1/year=2023/month=02/day=08/**