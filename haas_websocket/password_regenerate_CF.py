import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from haas_rest_handler_class import TokenAuth

# Will run on an interval in GCP as a cloud function to regenerate the password every 3 months

rest_agent = TokenAuth()

rest_agent.passwordReset()