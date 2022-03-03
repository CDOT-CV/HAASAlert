import os
import json
import requests
import random
import logging
import haas_websocket.haas_password_generator
from dotenv import load_dotenv
from google.cloud import secretmanager
from google.cloud.secretmanager_v1 import types
from google.api_core.exceptions import FailedPrecondition

class TokenAuth():

    def __init__(self):
        # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp_credentials.json"
        load_dotenv()
        self.username_key = os.getenv('HAAS_AUTH_USERNAME_KEY')
        self.password_key = os.getenv('HAAS_AUTH_PASSWORD_KEY')
        self.bearer_key = os.getenv('HAAS_BEARER_TOKEN_KEY')
        self.refresh_key = os.getenv('HAAS_REFRESH_TOKEN_KEY')
        self.api_endpoint = os.getenv('HAAS_API_ENDPOINT')
        self.id = os.getenv('PROJECT_ID')
        self.r_token = "initialized"

    def secretManagerGet(self,secret_id):
        if not self.id or not secret_id:
            return None
        try:
            client = secretmanager.SecretManagerServiceClient()
            parent = client.secret_path(self.id, secret_id)
            sv_list = client.list_secret_versions
            parent_list = sv_list(request={"parent": parent})
            for version in parent_list:
                if (version.state == 1):
                    response = client.access_secret_version(request={"name": version.name})
                    decoded = response.payload.data.decode("UTF-8")
                    return decoded
        except Exception:
            return None

    def secretManagerSet(self,secret_id,payload):
        if not self.id or not secret_id or not payload:
            return None
        try:
            client = secretmanager.SecretManagerServiceClient()
            encoded_payload = payload.encode("UTF-8")
            parent = f"projects/{self.id}/secrets/{secret_id}"
            response = client.add_secret_version(
                request={"parent": parent, "payload": {"data": encoded_payload}}
            )
            return response
        except Exception:
            print(f"(ERROR) Could not add a new secret version for the secret ID: {secret_id}")
            return None


    def signIn(self):
        self.api_username = self.secretManagerGet(self.username_key)
        self.api_password = self.secretManagerGet(self.password_key)

        r = requests.post(self.api_endpoint + "oauth/token",
                    json={"grant_type": "password",
                    "username":self.api_username,
                    "password":self.api_password})
        json_response = json.loads(r.content)

        self.b_token = json_response["access_token"]
        self.r_token = json_response["refresh_token"]
        
        self.secretManagerSet(self.bearer_key, self.b_token)
        self.secretManagerSet(self.refresh_key, self.r_token)

        print("Successfully signed into the Haas Alert Rest Endpoint")
        return self.b_token


    def signOut(self):
        r = requests.post(self.api_endpoint+'oauth/revoke')

        if r.status_code == 200:
            return True
        else:
            print("(ERROR) FAILED TO CONNECT TO HAAS ALERT AND SIGN OUT")
            return False

    def refreshToken(self):
        if (self.r_token == "initialized"):
            self.r_token = self.secretManagerGet(self.refresh_key)

        refresh_json = {"grant_type": "refresh_token",
                    "refresh_token":self.r_token}

        r = requests.post(self.api_endpoint + "oauth/token",
                            json = refresh_json)
        json_response = json.loads(r.content)

        self.b_token = json_response["access_token"]
        self.r_token = json_response["refresh_token"]

        self.secretManagerSet(self.bearer_key, self.b_token)
        self.secretManagerSet(self.refresh_key, self.r_token)

        print("Token successfully refreshed.")

        return self.b_token


    def setPassword(self, new_password):
        self.api_password = new_password
        self.secretManagerSet(self.password_key, new_password)

    # TODO: Figure out why tha api does not update when setting a new password.
    # def passwordReset(self):
    #     new_password = haas_password_generator.gen_password (10)
    #     request_json = {"password": new_password}
    #     r = requests.patch(self.api_endpoint + "users/password", json=request_json)
    #     print(f"passwordReset patch response {r}")

    #     print(f"passwordReset new_password: {new_password}")

    #     if r.status_code == 200:
    #         x = self.setPassword(new_password)
    #         return True
    #     else:
    #         print(f"(ERROR) FAILED TO CONNECT TO GCP AND UPDATE SECRET REFRESHING PASSWORD")
    #         return False

    def checkToken(self):
        gcp_btoken = self.secretManagerGet(self.bearer_key)

        if (self.b_token == gcp_btoken):
            return True
        else:
            return False

    def checkPassword(self):
        api_password = self.secretManagerGet(self.password_key)

        if (self.api_password == api_password):
            return True
        else:
            print (api_password)
            return False

    def tokenUpdate(self):
        self.b_token = self.secretManagerGet(self.bearer_key)

        print(f"(INFO) Updated b_token from GCP")
        return self.b_token
    
    # TODO: same as above, fix password updating module
    # def passwordUpdate(self):
    #     self.api_password = self.secretManagerGet(self.password_key)

    #     print(f"(INFO) Updated api password from GCP")
    #     return self.api_password

    def getToken(self):
        return self.b_token