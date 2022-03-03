from haas_websocket.haas_rest_handler import TokenAuth

# Will run on an interval in GCP as a cloud function to regenerate the password every 3 months

rest_agent = TokenAuth()

rest_agent.passwordReset()