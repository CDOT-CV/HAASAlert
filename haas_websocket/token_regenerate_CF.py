import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from haas_rest_handler_class import TokenAuth

# Will run on an interval in GCP as a cloud function to regenerate the bearer token each day

rest_agent = TokenAuth()

rest_agent.refreshToken()