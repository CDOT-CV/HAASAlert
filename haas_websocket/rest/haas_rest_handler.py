import os
import json
import requests
import logging
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
        self.r_token = "initialized"
        
        if (not self.username_key or not self.password_key or not self.bearer_key or not self.refresh_key or not self.api_endpoint or not self.id):
            logging.error("HAAS_REST_HANDLER.INIT Could not retrieve a required environmental variable. Please check the sample.env file and verify that all variables are assigned.")
            
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
        except Exception as e:
            logging.error(f"HAAS_REST_HANDLER.secretManagerGet Could not get a secret version for the secret ID: {secret_id} /n{str(e)}")
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
            logging.error(f"HAAS_REST_HANDLER.secretManagerSet Could not add a new secret version for the secret ID: {secret_id}")
            return None


    def signIn(self):
        self.api_username = self.secretManagerGet(self.username_key)
        self.api_password = self.secretManagerGet(self.password_key)

        r = requests.post(self.api_endpoint + "oauth/token",
                    json={"grant_type": "password",
                    "username":self.api_username,
                    "password":self.api_password})
        if (r.status_code == 200):
            json_response = json.loads(r.content)

            self.b_token = json_response.get("access_token")
            self.r_token = json_response.get("refresh_token")
            
            if not self.b_token or not self.r_token:
                logging.error("HAAS_REST_HANDLER.signIn failed to get a token from the Haas alert response message")
                return None
            
            self.secretManagerSet(self.bearer_key, self.b_token)
            self.secretManagerSet(self.refresh_key, self.r_token)

            logging.info("Successfully signed into the Haas Alert Rest Endpoint")
            return self.b_token
        else:
            logging.error(f"HAAS_REST_HANDLER.signIn FAILED TO CONNECT TO HAAS ALERT AND SIGN IN \nResponse message: {r.status_code}")
            return None


    def signOut(self):
        bearer = 'Bearer' + self.b_token
        r = requests.post(self.api_endpoint+'oauth/revoke', headers=
                          {'content-type': 'application/json', 
                           'ACCEPT':'application/vnd.haasalert.com; version=2',
                           'Authorization':bearer})

        if r.status_code == 200:
            logging.info("HAAS_REST_HANDLER.signOut Successfully signed out of the HAAS API")
            return True
        else:
            logging.error(f"HAAS_REST_HANDLER.signOut FAILED TO CONNECT TO HAAS ALERT AND SIGN OUT \nResponse message: {r.status_code}")
            return False

    def refreshToken(self):
        if (self.r_token == "initialized"):
            self.r_token = self.secretManagerGet(self.refresh_key)

        refresh_json = {"grant_type": "refresh_token",
                    "refresh_token":self.r_token}

        r = requests.post(self.api_endpoint + "oauth/token",
                            json = refresh_json)
        json_response = json.loads(r.content)

        if (r.status_code == 200):

            self.b_token = json_response.get("access_token")
            self.r_token = json_response.get("refresh_token")
            
            if not self.b_token or not self.r_token:
                logging.error("HAAS_REST_HANDLER.refreshToken failed to get a token from the Haas alert response message")
                return None

            self.secretManagerSet(self.bearer_key, self.b_token)
            self.secretManagerSet(self.refresh_key, self.r_token)

            logging.info("Token successfully refreshed.")

            return self.b_token
        else:
            logging.error(f"HAAS_REST_HANDLER.refreshToken Bad response code from Haas alert API \nResponse message: {r.status_code}")
            return None


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
    #         print(f"FAILED TO CONNECT TO GCP AND UPDATE SECRET REFRESHING PASSWORD")
    #         return False
    # jacobs idea: ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))

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
            logging.info("Updating password from GCP")
            return False

    def tokenUpdate(self):
        self.b_token = self.secretManagerGet(self.bearer_key)

        logging.info(f"Updated b_token from GCP")
        return self.b_token
    
    # TODO: same as above, fix password updating module
    # def passwordUpdate(self):
    #     self.api_password = self.secretManagerGet(self.password_key)

    #     print(f"(INFO) Updated api password from GCP")
    #     return self.api_password

    def getToken(self):
        return self.b_token