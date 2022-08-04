import os

PROJECT = os.environ.get('GOOGLE_CLOUD_PROJECT', 'cdot-oim-cv-dev')

ENVIRONMENT = PROJECT.split('-')[-1] # ['cdot', 'rtdh', 'dev' <-- this one ]
      
REGION = os.environ.get('GOOGLE_CLOUD_REGION', 'us-central1')

HAAS_AUTH_USERNAME_KEY="cdot-haas-alert-user"
HAAS_AUTH_PASSWORD_KEY="cdot-haas-alert-password"
HAAS_BEARER_TOKEN_KEY="cdot-haas-bearer-token"
HAAS_REFRESH_TOKEN_KEY="cdot-haas-refresh-token"
HAAS_API_ID="e2fe6bf5-9325-450d-962b-dd926b2dd179"