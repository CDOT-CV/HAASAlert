import os
import requests
import websocket
import json
from haas_websocket import main
from haas_websocket.rest.haas_rest_handler import TokenAuth
from unittest.mock import MagicMock, patch

@patch('google.cloud.pubsub_v1.PublisherClient')
@patch('haas_websocket.rest.haas_rest_handler.TokenAuth')
@patch.object(main, 'running', side_effect = [True,False])
@patch.object(main, 'filterMessage')
@patch.object(websocket,'create_connection')
@patch.dict(os.environ, {
    'PROJECT_ID': 'PROJECT_ID',
    'POINT_TOPIC': 'POINT_TOPIC',
    'HAAS_WSS_ENDPOINT': 'wss.testwebsocket',
    'HAAS_API_ENDPOINT': 'api.endpoint'
})
def test_main_failed_token(pubsub, mTokenAuth, running, filterMessage, create_connection):
    mTokenAuth.signIn = MagicMock(return_value = 'token')
    mTokenAuth.checkPassword = MagicMock(return_value = True)
    mTokenAuth.checkToken = MagicMock(return_value = False)
    main.restSignIn = MagicMock(return_value = mTokenAuth)
    main.startWebsocket(pubsub)
    mTokenAuth.tokenUpdate.assert_called_with()


@patch('google.cloud.secretmanager_v1.SecretManagerServiceClient')
@patch('google.cloud.secretmanager_v1.services.secret_manager_service.pagers.ListSecretVersionsPager')
@patch.dict(os.environ, {
    'PROJECT_ID': 'PROJECT_ID',
    'POINT_TOPIC': 'POINT_TOPIC',
    'HAAS_WSS_ENDPOINT': 'wss.testwebsocket',
    'HAAS_API_ENDPOINT': 'api.endpoint'
})
def test_rest_handler_get_secret_version(mock_smc, mock_lsvp):
    mock_smc.secret_path = MagicMock(return_value = 'path')
    mock_smc.list_secret_versions = MagicMock(return_value = mock_lsvp)
    mock_smc.access_secret_version.return_value.payload.data = MagicMock(return_value = b'super_secret_token')
    obj = TokenAuth()
    
    secret_string = obj.secretManagerGet('secret_key')

    # TODO FIX THIS UNIT TEST
    assert secret_string == None


@patch("google.cloud.secretmanager_v1.SecretManagerServiceClient")
@patch.dict(os.environ, {"PROJECT_ID":"random_id"},clear=True)
def test_rest_handler_set_secret(mock_smc):
    mock_smc.return_value.add_secret_version.return_value = 'success'
    obj = TokenAuth()
    response = obj.secretManagerSet('secret_name','payload')

    assert response == 'success'

@patch("google.cloud.secretmanager_v1.SecretManagerServiceClient")
@patch.dict(os.environ,{},clear=True)
def test_rest_handler_set_none(mock_smc):
    obj = TokenAuth()
    response = obj.secretManagerSet(None,None)

    assert not response

@patch.object(TokenAuth, 'secretManagerGet')
@patch.object(TokenAuth, 'secretManagerSet')
@patch.dict(os.environ, {
    "HAAS_AUTH_USERNAME_KEY":"key", 
    "HAAS_AUTH_PASSWORD_KEY":"key",
    "HAAS_BEARER_TOKEN_KEY": "key", 
    "HAAS_REFRESH_TOKEN_KEY": "key",
    "HAAS_AUTH_ENDPOINT": "auth_endpoint",
    "HAAS_API_ENDPOINT": "api_endpoint",
    "PROJECT_ID":"random_id"
})
def test_rest_handler_sign_in(mock_rest_smg, mock_rest_sms):
    obj = TokenAuth()

    mock_rest_smg.return_value = "value"
    haas_response = requests.Response
    haas_response.status_code = 200
    haas_response.content = '{"access_token":"b_token","token_type":"Bearer","expires_in":86400,"refresh_token":"refresh_token","scope":"read","created_at":1645737800}'
    requests.post = MagicMock(return_value = haas_response)
    
    response = obj.signIn()

    assert response == "b_token"

@patch.object(TokenAuth, 'secretManagerGet')
@patch.object(TokenAuth, 'secretManagerSet')
@patch.dict(os.environ, {
    "HAAS_AUTH_USERNAME_KEY":"key", 
    "HAAS_AUTH_PASSWORD_KEY":"key",
    "HAAS_BEARER_TOKEN_KEY": "key", 
    "HAAS_REFRESH_TOKEN_KEY": "key",
    "HAAS_AUTH_ENDPOINT": "auth_endpoint",
    "HAAS_API_ENDPOINT": "api_endpoint",
    "PROJECT_ID":"random_id"
})
def test_rest_handler_sign_in_no_data(mock_rest_smg, mock_rest_sms):
    obj = TokenAuth()

    mock_rest_smg.return_value = "value"
    haas_response = requests.Response
    haas_response.status_code = 200
    haas_response.content = '{}'
    requests.post = MagicMock(return_value = haas_response)
    
    response = obj.signIn()

    assert response is None

@patch.object(TokenAuth, 'secretManagerGet')
@patch.object(TokenAuth, 'secretManagerSet')
@patch.dict(os.environ, {
    "HAAS_AUTH_USERNAME_KEY":"key", 
    "HAAS_AUTH_PASSWORD_KEY":"key",
    "HAAS_BEARER_TOKEN_KEY": "key", 
    "HAAS_REFRESH_TOKEN_KEY": "key",
    "HAAS_AUTH_ENDPOINT": "auth_endpoint",
    "HAAS_API_ENDPOINT": "api_endpoint",
    "PROJECT_ID":"random_id"
})
def test_rest_handler_sign_in_failure(mock_rest_smg, mock_rest_sms):
    obj = TokenAuth()

    mock_rest_smg.return_value = "value"
    haas_response = requests.Response
    haas_response.status_code = 400
    requests.post = MagicMock(return_value = haas_response)
    
    response = obj.signIn()

    assert response is None

@patch.dict(os.environ, {
    "HAAS_AUTH_USERNAME_KEY":"key", 
    "HAAS_AUTH_PASSWORD_KEY":"key",
    "HAAS_BEARER_TOKEN_KEY": "key", 
    "HAAS_REFRESH_TOKEN_KEY": "key",
    "HAAS_AUTH_ENDPOINT": "auth_endpoint",
    "HAAS_API_ENDPOINT": "api_endpoint",
    "PROJECT_ID":"random_id"
})
def test_rest_handler_sign_out_success():
    
    obj = TokenAuth()
    obj.b_token = "b_token"
    haas_response = requests.Response
    haas_response.status_code = 200
    requests.post = MagicMock(return_value = haas_response)
    
    response = obj.signOut()

    assert response == True

@patch.dict(os.environ, {
    "HAAS_AUTH_USERNAME_KEY":"key", 
    "HAAS_AUTH_PASSWORD_KEY":"key",
    "HAAS_BEARER_TOKEN_KEY": "key", 
    "HAAS_REFRESH_TOKEN_KEY": "key",
    "HAAS_AUTH_ENDPOINT": "auth_endpoint",
    "HAAS_API_ENDPOINT": "api_endpoint",
    "PROJECT_ID":"random_id"
})
def test_rest_handler_sign_out_failure():
    
    obj = TokenAuth()
    obj.b_token = "b_token"
    haas_response = requests.Response
    haas_response.status_code = 400
    requests.post = MagicMock(return_value = haas_response)
    
    response = obj.signOut()

    assert response == False

@patch.object(TokenAuth, 'secretManagerGet', return_value = 'refresh_token')
@patch.object(TokenAuth, 'secretManagerSet')
@patch.dict(os.environ, {
    "HAAS_AUTH_USERNAME_KEY":"key", 
    "HAAS_AUTH_PASSWORD_KEY":"key",
    "HAAS_BEARER_TOKEN_KEY": "key", 
    "HAAS_REFRESH_TOKEN_KEY": "key",
    "HAAS_AUTH_ENDPOINT": "auth_endpoint",
    "HAAS_API_ENDPOINT": "api_endpoint",
    "PROJECT_ID":"random_id"
})
def test_rest_handler_refresh_token(mock_rest_smg, mock_rest_sms):

    haas_response = requests.Response
    haas_response.status_code = 200
    haas_response.content = '{"access_token":"b_token","token_type":"Bearer","expires_in":86400,"refresh_token":"refresh_token","scope":"read","created_at":1645737800}'
    requests.post = MagicMock(return_value = haas_response)
    
    obj = TokenAuth()
    response = obj.refreshToken()

    assert response == 'b_token'

@patch.object(TokenAuth, 'secretManagerGet', return_value = 'refresh_token')
@patch.object(TokenAuth, 'secretManagerSet')
@patch.dict(os.environ, {
    "HAAS_AUTH_USERNAME_KEY":"key", 
    "HAAS_AUTH_PASSWORD_KEY":"key",
    "HAAS_BEARER_TOKEN_KEY": "key", 
    "HAAS_REFRESH_TOKEN_KEY": "key",
    "HAAS_AUTH_ENDPOINT": "auth_endpoint",
    "HAAS_API_ENDPOINT": "api_endpoint",
    "PROJECT_ID":"random_id"
})
def test_rest_handler_refresh_token_no_data(mock_rest_smg, mock_rest_sms):

    haas_response = requests.Response
    haas_response.status_code = 200
    haas_response.content = '{}'
    requests.post = MagicMock(return_value = haas_response)
    
    obj = TokenAuth()
    response = obj.refreshToken()

    assert response is None

@patch.object(TokenAuth, 'secretManagerGet', return_value = 'refresh_token')
@patch.object(TokenAuth, 'secretManagerSet')
@patch.dict(os.environ, {
    "HAAS_AUTH_USERNAME_KEY":"key", 
    "HAAS_AUTH_PASSWORD_KEY":"key",
    "HAAS_BEARER_TOKEN_KEY": "key", 
    "HAAS_REFRESH_TOKEN_KEY": "key",
    "HAAS_AUTH_ENDPOINT": "auth_endpoint",
    "HAAS_API_ENDPOINT": "api_endpoint",
    "PROJECT_ID":"random_id"
})
def test_rest_handler_refresh_token_failure(mock_rest_smg, mock_rest_sms):

    haas_response = requests.Response
    haas_response.status_code = 400
    haas_response.content = '{"access_token":"b_token","token_type":"Bearer","expires_in":86400,"refresh_token":"refresh_token","scope":"read","created_at":1645737800}'
    requests.post = MagicMock(return_value = haas_response)
    
    obj = TokenAuth()
    response = obj.refreshToken()

    assert response is None

@patch.object(TokenAuth, 'secretManagerGet', return_value = 'bearer_token')
@patch.dict(os.environ, {
    "HAAS_AUTH_USERNAME_KEY":"key", 
    "HAAS_AUTH_PASSWORD_KEY":"key",
    "HAAS_BEARER_TOKEN_KEY": "key", 
    "HAAS_REFRESH_TOKEN_KEY": "key",
    "HAAS_AUTH_ENDPOINT": "auth_endpoint",
    "HAAS_API_ENDPOINT": "api_endpoint",
    "PROJECT_ID":"random_id"
})
def test_rest_handler_check_token_true(mock_rest_sms):
    
    obj = TokenAuth()
    obj.b_token = 'bearer_token'
    response = obj.checkToken()

    assert response == True
    
@patch.object(TokenAuth, 'secretManagerGet', return_value = 'bearer_token')
@patch.dict(os.environ, {
    "HAAS_AUTH_USERNAME_KEY":"key", 
    "HAAS_AUTH_PASSWORD_KEY":"key",
    "HAAS_BEARER_TOKEN_KEY": "key", 
    "HAAS_REFRESH_TOKEN_KEY": "key",
    "HAAS_AUTH_ENDPOINT": "auth_endpoint",
    "HAAS_API_ENDPOINT": "api_endpoint",
    "PROJECT_ID":"random_id"
})
def test_rest_handler_check_token_false(mock_rest_sms):
    
    obj = TokenAuth()
    obj.b_token = 'different_token'
    response = obj.checkToken()

    assert response == False

@patch.object(TokenAuth, 'secretManagerGet', return_value = 'bearer_token')
@patch.dict(os.environ, {
    "HAAS_AUTH_USERNAME_KEY":"key", 
    "HAAS_AUTH_PASSWORD_KEY":"key",
    "HAAS_BEARER_TOKEN_KEY": "key", 
    "HAAS_REFRESH_TOKEN_KEY": "key",
    "HAAS_AUTH_ENDPOINT": "auth_endpoint",
    "HAAS_API_ENDPOINT": "api_endpoint",
    "PROJECT_ID":"random_id"
})
def test_rest_handler_token_update(mock_rest_sms):
    
    obj = TokenAuth()
    response = obj.tokenUpdate()

    assert response == 'bearer_token'

@patch.object(TokenAuth, 'secretManagerGet', return_value = 'bearer_token')
@patch.dict(os.environ, {
    "HAAS_AUTH_USERNAME_KEY":"key", 
    "HAAS_AUTH_PASSWORD_KEY":"key",
    "HAAS_BEARER_TOKEN_KEY": "key", 
    "HAAS_REFRESH_TOKEN_KEY": "key",
    "HAAS_AUTH_ENDPOINT": "auth_endpoint",
    "HAAS_API_ENDPOINT": "api_endpoint",
    "PROJECT_ID":"random_id"
})
def test_rest_handler_get_token(mock_rest_sms):
    
    obj = TokenAuth()
    obj.b_token = 'bearer_token'
    response = obj.getToken()

    assert response == 'bearer_token'




@patch.object(TokenAuth, 'secretManagerGet', return_value = 'bearer_token')
@patch.object(TokenAuth, 'secretManagerSet')
@patch.dict(os.environ,{"HAAS_AUTH_USERNAME_KEY":"key", "HAAS_AUTH_PASSWORD_KEY":"key", 
"HAAS_BEARER_TOKEN_KEY": "key", "HAAS_REFRESH_TOKEN_KEY": "key", "HAAS_API_ENDPOINT":"endpoint"},clear=True)
def test_rest_handler_getOrganizations(mock_rest_smg, mock_rest_sms):
    with open('tests/support/sample_organizations.json', 'r') as f:
        organizations_json = json.load(f)

    haas_response = requests.Response
    haas_response.status_code = 200
    haas_response.content = json.dumps(organizations_json)
    requests.get = MagicMock(return_value = haas_response)

    obj = TokenAuth()
    obj.b_token= 'bearer_token'
    response = obj.getOrganizations()

    assert response == organizations_json

@patch.object(TokenAuth, 'secretManagerGet', return_value = None)
@patch.object(TokenAuth, 'signIn', return_value = "bearer_token")
@patch.object(TokenAuth, 'secretManagerSet')
@patch.dict(os.environ,{"HAAS_AUTH_USERNAME_KEY":"key", "HAAS_AUTH_PASSWORD_KEY":"key", 
"HAAS_BEARER_TOKEN_KEY": "key", "HAAS_REFRESH_TOKEN_KEY": "key", "HAAS_API_ENDPOINT":"endpoint"},clear=True)
def test_rest_handler_getOrganizations_fail(mock_rest_smg, mock_signIn, mock_rest_sms):
    with open('tests/support/sample_organizations.json', 'r') as f:
        organizations_json = json.load(f)

    haas_response = requests.Response
    haas_response.status_code = 200
    haas_response.content = json.dumps(organizations_json)
    requests.get = MagicMock(return_value = haas_response)

    obj = TokenAuth()
    obj.b_token= 'bearer_token'
    response = obj.getOrganizations()

    assert response == organizations_json

@patch.object(TokenAuth, 'secretManagerGet', return_value = 'bearer_token')
@patch.object(TokenAuth, 'secretManagerSet')
@patch.dict(os.environ,{"HAAS_AUTH_USERNAME_KEY":"key", "HAAS_AUTH_PASSWORD_KEY":"key", 
"HAAS_BEARER_TOKEN_KEY": "key", "HAAS_REFRESH_TOKEN_KEY": "key", "HAAS_API_ENDPOINT":"endpoint"},clear=True)
def test_rest_handler_getLocations(mock_rest_smg, mock_rest_sms):
    with open('tests/support/sample_location.json', 'r') as f:
        locations_json = json.load(f)

    haas_response = requests.Response
    haas_response.status_code = 200
    haas_response.content = json.dumps(locations_json)
    requests.get = MagicMock(return_value = haas_response)

    obj = TokenAuth()
    obj.b_token = 'bearer_token'
    response = obj.getLocations("id")

    assert response == locations_json

@patch.object(TokenAuth, 'secretManagerGet', return_value = 'bearer_token')
@patch.object(TokenAuth, 'secretManagerSet')
@patch.dict(os.environ,{"HAAS_AUTH_USERNAME_KEY":"key", "HAAS_AUTH_PASSWORD_KEY":"key", 
"HAAS_BEARER_TOKEN_KEY": "key", "HAAS_REFRESH_TOKEN_KEY": "key", "HAAS_API_ENDPOINT":"endpoint"},clear=True)
def test_rest_handler_getThings(mock_rest_smg, mock_rest_sms):
    with open('tests/support/sample_things.json', 'r') as f:
        things_json = json.load(f)

    haas_response = requests.Response
    haas_response.status_code = 200
    haas_response.content = json.dumps(things_json)
    requests.get = MagicMock(return_value = haas_response)

    obj = TokenAuth()
    obj.b_token = 'bearer_token'
    response = obj.getThings("id")

    assert response == things_json 