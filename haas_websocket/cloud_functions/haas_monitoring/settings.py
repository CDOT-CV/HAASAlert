# Copyright 2020 Google LLC. This software is provided as is, without
# warranty or representation for any use or purpose. Your use of it is
# subject to your agreement with Google.
import os

PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT', 'cdot-adap-dev')
ENVIRONMENT = PROJECT_ID.split('-')[-1] # ['cdot', 'rtdh', 'dev' <-- this one ]

HAAS_ALERT_RAW_TABLE_NAME = f'cdot-adap-{ENVIRONMENT}.haas_alert_raw'
HEARTBEAT_TABLE = "websocket_heartbeat"