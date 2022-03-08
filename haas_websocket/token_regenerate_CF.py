from haas_rest_handler import TokenAuth

# Will run on an interval in GCP as a cloud function to regenerate the bearer token each day

def refresh_token(request):
    rest_agent = TokenAuth()
    rest_agent.refreshToken()