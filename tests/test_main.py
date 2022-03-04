import os
import pytest
import json
import websocket
from haas_websocket import main
from haas_websocket.haas_rest_handler import TokenAuth
from unittest.mock import MagicMock, patch, call, Mock
from google.cloud import secretmanager

#--------------------------------------------------------------------------------unit tests for rest sign in module--------------------------------------------------------------------------------

@patch('google.cloud.pubsub_v1.PublisherClient')
@patch('haas_websocket.haas_rest_handler.TokenAuth')
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
    main.filterMessage(message,pubsub)
    encoded = message.encode("utf-8")
    pubsub.publish.assert_called_with(pubsub.topic_path('PROJECT_ID', 'POINT_TOPIC'),encoded)

@patch('google.cloud.pubsub_v1.PublisherClient')
@patch.dict(os.environ, {
    'PROJECT_ID': 'PROJECT_ID',
    'HEARTBEAT_TOPIC': 'HEARTBEAT_TOPIC'
})
def test_main_filter_heartbeat(pubsub):
    message = '{"type":"heartbeat"}'
    main.filterMessage(message,pubsub)
    encoded = message.encode("utf-8")
    pubsub.publish.assert_called_with(pubsub.topic_path('PROJECT_ID', 'HEARTBEAT_TOPIC'),encoded)

@patch('google.cloud.pubsub_v1.PublisherClient')
@patch.dict(os.environ, {
    'PROJECT_ID': 'PROJECT_ID',
    'THING_TOPIC': 'THING_TOPIC'
})
def test_main_filter_thing(pubsub):
    message = '{"type":"thing"}'
    main.filterMessage(message,pubsub)
    encoded = message.encode("utf-8")
    pubsub.publish.assert_called_with(pubsub.topic_path('PROJECT_ID', 'THING_TOPIC'),encoded)

@patch('google.cloud.pubsub_v1.PublisherClient')
@patch.dict(os.environ, {
    'PROJECT_ID': 'PROJECT_ID',
    'LOCATION_TOPIC': 'LOCATION_TOPIC'
})
def test_main_filter_location(pubsub):
    message = '{"type":"location"}'
    main.filterMessage(message,pubsub)
    encoded = message.encode("utf-8")
    pubsub.publish.assert_called_with(pubsub.topic_path('PROJECT_ID', 'LOCATION_TOPIC'),encoded)
    
@patch('google.cloud.pubsub_v1.PublisherClient')
@patch.dict(os.environ, {})
def test_main_filter_none(pubsub):
    message = '{"type":"none"}'
    response = main.filterMessage(message,pubsub)
    assert response == False

@patch('google.cloud.pubsub_v1.PublisherClient')
@patch.dict(os.environ, {
    'PROJECT_ID': 'PROJECT_ID'
})
def test_main_filter_keep_alive(pubsub):
    message = '{"keepAlive":"True"}'
    response,success = main.filterMessage(message,pubsub)
    assert response == 'keepAlive'


#--------------------------------------------------------------------------------unit tests for websocket module--------------------------------------------------------------------------------

@patch('google.cloud.pubsub_v1.PublisherClient')
@patch('haas_websocket.haas_rest_handler.TokenAuth')
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
@patch('haas_websocket.haas_rest_handler.TokenAuth')
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
@patch('haas_websocket.haas_rest_handler.TokenAuth')
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
@patch('haas_websocket.haas_rest_handler.TokenAuth')
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