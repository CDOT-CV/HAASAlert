import os
import websocket
from haas_websocket import main
from unittest.mock import MagicMock, patch

#--------------------------------------------------------------------------------unit tests for rest sign in module--------------------------------------------------------------------------------

@patch('google.cloud.pubsub_v1.PublisherClient')
@patch('haas_websocket.rest.haas_rest_handler.TokenAuth')
@patch.dict(os.environ, {
    'PROJECT_ID': 'PROJECT_ID',
    'HAAS_WSS_ENDPOINT': 'wss.testwebsocket'
})
def test_main_rest_sign_in(pubsub, mTokenAuth):
    main.TokenAuth = MagicMock(return_value = mTokenAuth)
    main.restSignIn()
    mTokenAuth.signIn.assert_called_with()

#--------------------------------------------------------------------------------unit tests for filter module--------------------------------------------------------------------------------

@patch('google.cloud.pubsub_v1.PublisherClient')
@patch.dict(os.environ, {
    'PROJECT_ID': 'PROJECT_ID'
})
def test_main_filter(pubsub):
    message = '{"type":"point"}'
    response,success = main.filterMessage(message,pubsub)
    encoded = message.encode("utf-8")
    pubsub.publish.assert_called_with(pubsub.topic_path('PROJECT_ID', 'POINT_TOPIC'),encoded)
    assert response == 'point'
    assert success == True
    
@patch('google.cloud.pubsub_v1.PublisherClient')
@patch.dict(os.environ, {
    'PROJECT_ID': 'PROJECT_ID'
})
def test_main_filter_none(pubsub):
    message = '{}'
    response,success = main.filterMessage(message,pubsub)
    assert response == 'Unknown'
    assert success == False

@patch('google.cloud.pubsub_v1.PublisherClient')
@patch.dict(os.environ, {
    'PROJECT_ID': 'PROJECT_ID'
})
def test_main_filter_keep_alive(pubsub):
    message = '{"keepAlive":"True"}'
    response,success = main.filterMessage(message,pubsub)
    assert response == 'keepAlive'
    assert success == False


#--------------------------------------------------------------------------------unit tests for websocket module--------------------------------------------------------------------------------

@patch('google.cloud.pubsub_v1.PublisherClient')
@patch('haas_websocket.rest.haas_rest_handler.TokenAuth')
@patch.object(main, 'running', side_effect = [True,False])
@patch.object(main, 'filterMessage', return_value = ("value", True))
@patch.object(websocket,'create_connection')
@patch.dict(os.environ, {
    'PROJECT_ID': 'PROJECT_ID',
    'HAAS_WSS_ENDPOINT': 'wss.testwebsocket'
})
def test_main_ws_publish(pubsub, mTokenAuth, running, filterMessage, create_connection):
    mTokenAuth.signIn = MagicMock(return_value = 'token')
    mTokenAuth.checkPassword = MagicMock(return_value = True)
    mTokenAuth.checkToken = MagicMock(return_value = True)
    main.restSignIn = MagicMock(return_value = mTokenAuth)
    websocket.create_connection().recv = MagicMock(return_value = 'value')
    main.startWebsocket(pubsub)
    main.filterMessage.assert_called_with('value',pubsub)

@patch('google.cloud.pubsub_v1.PublisherClient')
@patch('haas_websocket.rest.haas_rest_handler.TokenAuth')
@patch.object(main, 'running', side_effect = [True,False])
@patch.object(main, 'filterMessage', return_value = ("", False))
@patch.object(websocket,'create_connection')
@patch.dict(os.environ, {
    'PROJECT_ID': 'PROJECT_ID',
    'HAAS_WSS_ENDPOINT': 'wss.testwebsocket'
})
def test_main_ws_failed_publish(pubsub, mTokenAuth, running, filterMessage, create_connection):
    mTokenAuth.signIn = MagicMock(return_value = 'token')
    mTokenAuth.checkPassword = MagicMock(return_value = True)
    mTokenAuth.checkToken = MagicMock(return_value = True)
    main.restSignIn = MagicMock(return_value = mTokenAuth)
    websocket.create_connection().recv = MagicMock(return_value = 'value')
    main.startWebsocket(pubsub)
    main.filterMessage.assert_called_with('value',pubsub)

@patch('google.cloud.pubsub_v1.PublisherClient')
@patch('haas_websocket.rest.haas_rest_handler.TokenAuth')
@patch.object(main, 'running', side_effect = [True,False])
@patch.object(main, 'filterMessage')
@patch.object(websocket,'create_connection')
@patch.dict(os.environ, {
    'PROJECT_ID': 'PROJECT_ID',
    'HAAS_WSS_ENDPOINT': 'wss.testwebsocket'
})
def test_main_failed_token(pubsub, mTokenAuth, running, filterMessage, create_connection):
    mTokenAuth.signIn = MagicMock(return_value = 'token')
    mTokenAuth.checkPassword = MagicMock(return_value = True)
    mTokenAuth.checkToken = MagicMock(return_value = False)
    main.restSignIn = MagicMock(return_value = mTokenAuth)
    main.startWebsocket(pubsub)
    mTokenAuth.refreshToken.assert_called_with()

def test_main_running():
    response = main.running()
    assert response == True