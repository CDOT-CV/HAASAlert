from haas_websocket.rest.haas_rest_handler import TokenAuth
import logging

# Will run on an interval in GCP as a cloud function to regenerate the bearer token each day

def refresh_token(request):
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    rest_agent = TokenAuth()
    rest_agent.refreshToken()
    rest_agent.signOut()