import os
import websocket
from haas_websocket import main
from unittest.mock import MagicMock, patch

#--------------------------------------------------------------------------------unit tests for rest sign in module--------------------------------------------------------------------------------

@patch('google.cloud.pubsub_v1.PublisherClient')
@patch('haas_websocket.rest.haas_rest_handler.TokenAuth')
@patch.dict(os.environ, {
    'PROJECT_ID': 'PROJECT_ID',
    'POINT_TOPIC': 'POINT_TOPIC',
    'HAAS_WSS_ENDPOINT': 'wss.testwebsocket'
})
def test_main_rest_sign_in(pubsub, mTockenAuth):
    main.TokenAuth = MagicMock(return_value = mTockenAuth)
    main.restSignIn()
    mTockenAuth.signIn.assert_called_with()

#--------------------------------------------------------------------------------unit tests for filter module--------------------------------------------------------------------------------

@patch('google.cloud.pubsub_v1.PublisherClient')
@patch.dict(os.environ, {
    'PROJECT_ID': 'PROJECT_ID',
    'POINT_TOPIC': 'POINT_TOPIC'
})
def test_main_filter_point(pubsub):
    message = '{"type":"point"}'
    response,success = main.filterMessage(message,pubsub)
    encoded = message.encode("utf-8")
    pubsub.publish.assert_called_with(pubsub.topic_path('PROJECT_ID', 'POINT_TOPIC'),encoded)
    assert response == 'point'
    assert success == True

@patch('google.cloud.pubsub_v1.PublisherClient')
@patch.dict(os.environ, {
    'PROJECT_ID': 'PROJECT_ID',
    'HEARTBEAT_TOPIC': 'HEARTBEAT_TOPIC'
})
def test_main_filter_heartbeat(pubsub):
    message = '{"type":"heartbeat"}'
    response,success = main.filterMessage(message,pubsub)
    encoded = message.encode("utf-8")
    pubsub.publish.assert_called_with(pubsub.topic_path('PROJECT_ID', 'HEARTBEAT_TOPIC'),encoded)
    assert response == 'heartbeat'
    assert success == True

@patch('google.cloud.pubsub_v1.PublisherClient')
@patch.dict(os.environ, {
    'PROJECT_ID': 'PROJECT_ID',
    'THING_TOPIC': 'THING_TOPIC'
})
def test_main_filter_thing(pubsub):
    message = '{"type":"thing"}'
    response,success = main.filterMessage(message,pubsub)
    encoded = message.encode("utf-8")
    pubsub.publish.assert_called_with(pubsub.topic_path('PROJECT_ID', 'THING_TOPIC'),encoded)
    assert response == 'thing'
    assert success == True

@patch('google.cloud.pubsub_v1.PublisherClient')
@patch.dict(os.environ, {
    'PROJECT_ID': 'PROJECT_ID',
    'LOCATION_TOPIC': 'LOCATION_TOPIC'
})
def test_main_filter_location(pubsub):
    message = '{"type":"location"}'
    response,success = main.filterMessage(message,pubsub)
    encoded = message.encode("utf-8")
    pubsub.publish.assert_called_with(pubsub.topic_path('PROJECT_ID', 'LOCATION_TOPIC'),encoded)
    assert response == 'location'
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
    'POINT_TOPIC': 'POINT_TOPIC',
    'HAAS_WSS_ENDPOINT': 'wss.testwebsocket'
})
def test_main_ws_publish(pubsub, mTockenAuth, running, filterMessage, create_connection):
    mTockenAuth.signIn = MagicMock(return_value = 'token')
    mTockenAuth.checkPassword = MagicMock(return_value = True)
    mTockenAuth.checkToken = MagicMock(return_value = True)
    main.restSignIn = MagicMock(return_value = mTockenAuth)
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
    'POINT_TOPIC': 'POINT_TOPIC',
    'HAAS_WSS_ENDPOINT': 'wss.testwebsocket'
})
def test_main_ws_failed_publish(pubsub, mTockenAuth, running, filterMessage, create_connection):
    mTockenAuth.signIn = MagicMock(return_value = 'token')
    mTockenAuth.checkPassword = MagicMock(return_value = True)
    mTockenAuth.checkToken = MagicMock(return_value = True)
    main.restSignIn = MagicMock(return_value = mTockenAuth)
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
    'POINT_TOPIC': 'POINT_TOPIC',
    'HAAS_WSS_ENDPOINT': 'wss.testwebsocket'
})
def test_main_failed_token(pubsub, mTockenAuth, running, filterMessage, create_connection):
    mTockenAuth.signIn = MagicMock(return_value = 'token')
    mTockenAuth.checkPassword = MagicMock(return_value = True)
    mTockenAuth.checkToken = MagicMock(return_value = False)
    main.restSignIn = MagicMock(return_value = mTockenAuth)
    main.startWebsocket(pubsub)
    mTockenAuth.tokenUpdate.assert_called_with()

@patch('google.cloud.pubsub_v1.PublisherClient')
@patch('haas_websocket.rest.haas_rest_handler.TokenAuth')
@patch.object(main, 'running', side_effect = [True,False])
@patch.object(main, 'filterMessage')
@patch.object(websocket,'create_connection')
@patch.dict(os.environ, {
    'PROJECT_ID': 'PROJECT_ID',
    'POINT_TOPIC': 'POINT_TOPIC',
    'HAAS_WSS_ENDPOINT': 'wss.testwebsocket'
})
def test_main_failed_password(pubsub, mTockenAuth, running, filterMessage, create_connection):
    mTockenAuth.signIn = MagicMock(return_value = 'token')
    mTockenAuth.checkPassword = MagicMock(return_value = False)
    main.restSignIn = MagicMock(return_value = mTockenAuth)
    main.startWebsocket(pubsub)
    mTockenAuth.passwordUpdate.assert_called_with()

def test_main_running():
    response = main.running()
    assert response == True