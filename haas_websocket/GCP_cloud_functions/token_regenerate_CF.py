from haas_websocket.haas_rest_handler import TokenAuth

# Will run on an interval in GCP as a cloud function to regenerate the bearer token each day

rest_agent = TokenAuth()

rest_agent.refreshToken()