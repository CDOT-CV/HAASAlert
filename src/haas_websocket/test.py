from haas_rest_handler_class import TokenAuth
from dotenv import load_dotenv
import os

# Will run on an interval in GCP as a cloud function to regenerate the bearer token each day

rest_agent = TokenAuth()
load_dotenv()
rest_agent.secretManagerSet("wrong","data")
