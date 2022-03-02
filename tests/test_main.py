# import sys
# sys.path.append('./src/haas_websocket')
import pytest
import os
import json
import websocket
from haas_websocket import main
from haas_websocket.haas_rest_handler import TokenAuth
# import haas_websocket.haas_password_generator
# import unittest
from unittest.mock import MagicMock, patch, call, Mock
from google.cloud import secretmanager
# from google.api_core.exceptions import FailedPrecondition


#--------------------------------------------------------------------------------System test for websocket connection--------------------------------------------------------------------------------

# def test_main_integration():
#     obj = Haas_Websocket()

#     # when
#     response = obj.startWebsocket(False)

#     # then assert that state is maintained
#     assert response == True

# @patch("main.TokenAuth.checkPassword",side_effect=Exception)
# def test_main_exceptions(mock):
#     obj = Haas_Websocket()

#     # when
#     response = obj.startWebsocket(False)

    # then assert that state is maintained
    # assert



# def test_api_refresh_token():
#     obj = TokenAuth()
    
#     # when
#     response = obj.refreshToken()

#     # then assert that state is maintained
#     assert response

#--------------------------------------------------------------------------------unit test for pub/sub publisher--------------------------------------------------------------------------------
@patch('google.cloud.pubsub_v1')
@patch.dict(os.environ, {
    'PROJECT_ID': 'PROJECT_ID',
    'POINT_TOPIC': 'POINT_TOPIC'
})
def test_main_filter_point(pubsub):
    message = '{"type":"point"}'
    main.filterMessage(message,pubsub)
    encoded = message.encode("utf-8")
    pubsub.publish.assert_called_with(pubsub.topic_path('PROJECT_ID', 'POINT_TOPIC'),encoded)

#--------------------------------------------------------------------------------unit tests for filter module--------------------------------------------------------------------------------
@patch('google.cloud.pubsub_v1')
@patch.dict(os.environ, {
    'PROJECT_ID': 'PROJECT_ID',
    'HEARTBEAT_TOPIC': 'HEARTBEAT_TOPIC'
})
def test_main_filter_heartbeat(pubsub):
    message = '{"type":"heartbeat"}'
    main.filterMessage(message,pubsub)
    encoded = message.encode("utf-8")
    pubsub.publish.assert_called_with(pubsub.topic_path('PROJECT_ID', 'HEARTBEAT_TOPIC'),encoded)

@patch('google.cloud.pubsub_v1')
@patch.dict(os.environ, {
    'PROJECT_ID': 'PROJECT_ID',
    'THING_TOPIC': 'THING_TOPIC'
})
def test_main_filter_thing(pubsub):
    message = '{"type":"thing"}'
    main.filterMessage(message,pubsub)
    encoded = message.encode("utf-8")
    pubsub.publish.assert_called_with(pubsub.topic_path('PROJECT_ID', 'THING_TOPIC'),encoded)

@patch('google.cloud.pubsub_v1')
@patch.dict(os.environ, {
    'PROJECT_ID': 'PROJECT_ID',
    'LOCATION_TOPIC': 'LOCATION_TOPIC'
})
def test_main_filter_location(pubsub):
    message = '{"type":"location"}'
    main.filterMessage(message,pubsub)
    encoded = message.encode("utf-8")
    pubsub.publish.assert_called_with(pubsub.topic_path('PROJECT_ID', 'LOCATION_TOPIC'),encoded)
    
@patch('google.cloud.pubsub_v1')
@patch.dict(os.environ, {})
def test_main_filter_none(pubsub):
    message = '{"type":"none"}'
    response = main.filterMessage(message,pubsub)
    assert response == False

@patch('google.cloud.pubsub_v1')
@patch.dict(os.environ, {
    'PROJECT_ID': 'PROJECT_ID'
})
def test_main_filter_keep_alive(pubsub):
    message = '{"keepAlive":"True"}'
    response,success = main.filterMessage(message,pubsub)
    assert response == 'keepAlive'


@patch('google.cloud.pubsub_v1')
# @patch.object(main, 'filterMessage')
# @patch.object(main, 'restSignIn')
# @patch.object(TokenAuth, 'mock_ta')
# @patch('websocket')
@patch.dict(os.environ, {
    'PROJECT_ID': 'PROJECT_ID',
    'POINT_TOPIC': 'POINT_TOPIC',
    'HAAS_WSS_ENDPOINT': 'wss.testwebsocket'
})
def test_main_ws(pubsub):
    main.filterMessage = MagicMock(return_value = ("value", True))
        
    TokenAuth.getToken = MagicMock(return_value = "btoken")
    TokenAuth.checkPassword = MagicMock(return_value = True)
    TokenAuth.checkToken = MagicMock(return_value = True)
    
    websocket.recv = MagicMock(return_value = "message")
    
    main.startWebsocket(pubsub)
    assert True == False
    

#     mock_smc.return_value.add_secret_version.return_value = 'success'

# @patch("haas_rest_handler_class.secretmanager.SecretManagerServiceClient")
# @patch.dict(os.environ, {"PROJECT_ID":"random_id"},clear=True)
# def test_gcp_get_secret_version(mock_smc):
#     mock_smc.client.secret_path.return_value("parent")

#     mock_smc.return_value.access_secret_version.return_value.payload.data = b'super_secret_token'
#     obj = TokenAuth()
#     secret_string = obj.secretManagerGet('secret_name')

#     assert secret_string == 'super_secret_token'

# @patch("haas_rest_handler_class.secretmanager.SecretManagerServiceClient")
# @patch.dict(os.environ, {},clear=True)
# def test_gcp_get_none(mock_smc):
#     obj = TokenAuth()
#     response = obj.secretManagerGet(None)

#     assert not response

# class MyTestCase(unittest.TestCase):
#     @patch("haas_rest_handler_class.secretmanager.SecretManagerServiceClient")
#     @patch("haas_rest_handler_class.secretmanager.SecretManagerServiceClient.access_secret_version", side_effect=FailedPrecondition)
#     @patch.dict(os.environ, {"PROJECT_ID":"random_id"},clear=True)
#     def test_gcp_get_none(self,mock_smc, mock_smc_asc):
#         obj = TokenAuth()
#         assert
#         # self.assertRaises(FailedPrecondition, obj.secretManagerGet('secret_name'))



# @patch("haas_rest_handler_class.secretmanager.SecretManagerServiceClient")
# @patch.dict(os.environ, {"PROJECT_ID":"random_id"},clear=True)
# def test_gcp_set_secret(mock_smc):
#     mock_smc.return_value.add_secret_version.return_value = 'success'
#     obj = TokenAuth()
#     response = obj.secretManagerSet('secret_name','payload')

#     assert response == 'success'

# @patch("haas_rest_handler_class.secretmanager.SecretManagerServiceClient")
# @patch.dict(os.environ,{},clear=True)
# def test_gcp_set_none(mock_smc):
#     obj = TokenAuth()
#     response = obj.secretManagerSet(None,None)

#     assert not response

# @patch("haas_rest_handler_class.secretManagerGet")
# @patch("haas_rest_handler_class.requests")
# @patch.dict(os.environ,{"HAAS_AUTH_USERNAME_KEY":"key", "HAAS_AUTH_PASSWORD_KEY":"key", 
# "HAAS_BEARER_TOKEN_KEY": "key", "HAAS_REFRESH_TOKEN_KEY": "key", "HAAS_API_ENDPOINT":"endpoint"},clear=True)
# def test_gcp_set_none(mock_rest_smg,mock_request):
#     obj = TokenAuth()

#     mock_rest_smg.return_value = "value"

#     haas_response = '{"access_token":"b_token","token_type":"Bearer","expires_in":86400,"refresh_token":"refresh_token","scope":"read","created_at":1645737800}'
#     mock_request.post.return_value(haas_response)

#     response = obj.signIn()

#     assert not response

# def test_password_generation():
#     password = haas_password_generator.gen_password(5)
#     assert len(password) == 5
