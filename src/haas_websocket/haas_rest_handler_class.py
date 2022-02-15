import json
import requests
import os
import random
import haas_password_generator
from dotenv import load_dotenv
from google.cloud import secretmanager

class TokenAuth():

    def __init__(self):
        load_dotenv()
        self.username_key = os.getenv('HAAS_AUTH_USERNAME_KEY')
        self.password_key = os.getenv('HAAS_AUTH_PASSWORD_KEY')
        self.bearer_key = os.getenv('HAAS_BEARER_TOKEN_KEY')
        self.refresh_key = os.getenv('HAAS_REFRESH_TOKEN_KEY')
        self.api_endpoint = os.getenv('HAAS_API_ENDPOINT')
        self.id = os.getenv('PROJECT_ID')
        self.client = secretmanager.SecretManagerServiceClient()
        self.r_token = "initialized"

    def secretManagerGet(self,secret_id):
        try:
            name = f"projects/{self.id}/secrets/{secret_id}/versions/latest"
            response = self.client.access_secret_version(request={"name": name})
            return response
        except Exception: # handler for disabled/destroyed versions
            parent = self.client.secret_path(self.id, secret_id)
            sv_list = self.client.list_secret_versions
            for version in sv_list(request={"parent": parent}):
                if (version.state == 1):
                    version_number = version.name.split("/")[-1]
                    print(f"(WARN) Could not access the latest version for {secret_id}, reverting to version: {version_number}")
                    response = self.client.access_secret_version(request={"name": version.name})
                    return response

    def secretManagerSet(self,secret_id,payload):
        try:
            encoded_payload = payload.encode("UTF-8")
            parent = f"projects/{self.id}/secrets/{secret_id}"
            response = self.client.add_secret_version(
                request={"parent": parent, "payload": {"data": payload}}
            )
        except Exception:
            print(f"(ERROR) Could not add a new secret version for the secret ID: {secret_id}")


    def signIn(self):
        self.api_password = self.secretManagerGet(self.password_key).payload.data.decode("UTF-8")
        self.api_username = self.secretManagerGet(self.username_key).payload.data.decode("UTF-8")

        r = requests.post(self.api_endpoint + "oauth/token",
                    json={"grant_type": "password",
                    "username":self.api_username,
                    "password":self.api_password})
        json_response = json.loads(r.content)

        self.b_token = json_response["access_token"]
        self.r_token = json_response["refresh_token"]
        
        secretManagerSet(self.b_token)
        secretManagerSet(self.r_token)        

        print("Successfully signed into the Haas Alert Rest Endpoint")
        return self.b_token


    def signOut(self):
        r = requests.post(HAAS_API_ENDPOINT+'oauth/revoke')

        if r.status_code == 200:
            return True
        else:
            print(f"(ERROR) FAILED TO CONNECT TO HAAS ALERT AND SIGN OUT")
            return False

    def refreshToken(self):
        if (self.r_token == "initialized"):
            request_name = f"projects/{self.id}/secrets/{self.refresh_key}/versions/latest"
            r_response = self.client.access_secret_version(request={"name": request_name})
            self.r_token = r_response.payload.data.decode("UTF-8")

        refresh_json = {"grant_type": "refresh_token",
                    "refresh_token":self.r_token}

        r = requests.post(self.api_endpoint + "oauth/token",
                            json = refresh_json)
        json_response = json.loads(r.content)

        self.b_token = json_response["access_token"]
        self.r_token = json_response["refresh_token"]

        encoded_btoken = self.b_token.encode('UTF-8')
        btoken_parent = f"projects/{self.id}/secrets/{self.bearer_key}"
        btoken_response = self.client.add_secret_version(parent=btoken_parent, payload={'data':encoded_btoken})
        
        encoded_rtoken = self.r_token.encode('UTF-8')
        rtoken_parent = f"projects/{self.id}/secrets/{self.refresh_key}"
        rtoken_response = self.client.add_secret_version(parent=rtoken_parent, payload={'data':encoded_rtoken})

        return self.b_token


    def setPassword(self, new_password):
        parent = f"projects/{self.id}/secrets/{self.password_key}"
        payload = new_password.encode('UTF-8')
        response = self.client.add_secret_version(parent=parent, payload={'data':payload})

        print (f"setPassword gcp response: {response}")
        self.api_password = new_password


    def passwordReset(self):
        new_password = haas_password_generator.gen_password (10)
        request_json = {"password": new_password}
        r = requests.patch(self.api_endpoint + "users/password", request_json)
        print(f"passwordReset patch response {r}")

        print(f"passwordReset new_password: {new_password}")

        if r.status_code == 200:
            x = self.setPassword(new_password)
            return True
        else:
            print(f"(ERROR) FAILED TO CONNECT TO GCP AND UPDATE SECRET REFRESHING PASSWORD")
            return False

    def checkToken(self):
        request_name = f"projects/{self.id}/secrets/{self.bearer_key}/versions/latest"
        b_response = self.client.access_secret_version(request={"name": request_name})
        gcp_btoken = b_response.payload.data.decode("UTF-8")

        if (self.b_token == gcp_btoken):
            return True
        else:
            return False

    def checkPassword(self):
        request_name = f"projects/{self.id}/secrets/{self.password_key}/versions/latest"
        password_response = self.client.access_secret_version(request={"name": request_name})
        api_password = password_response.payload.data.decode("UTF-8")

        if (self.api_password == api_password):
            return True
        else:
            print (api_password)
            return False

    def tokenUpdate(self):
        request_name = f"projects/{self.id}/secrets/{self.bearer_key}/versions/latest"
        b_response = self.client.access_secret_version(request={"name": request_name})
        self.b_token = b_response.payload.data.decode("UTF-8")

        print(f"(INFO) Updated b_token from GCP")
        return self.b_token
    
    def passwordUpdate(self):
        request_name = f"projects/{self.id}/secrets/{self.password_key}/versions/latest"
        password_response = self.client.access_secret_version(request={"name": request_name})
        self.api_password = password_response.payload.data.decode("UTF-8")
        print(request_name)
        print(f"(INFO) Updated api password from GCP")
        return self.api_password

    def getToken(self):
        return self.b_token
    
