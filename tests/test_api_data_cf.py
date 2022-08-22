import os
import requests
import websocket
import json
import haas_websocket.cloud_functions.api_data_CF as api_data_CF
from unittest.mock import MagicMock, patch


def test_parseIds():
    with open('tests/support/sample_organizations.json', 'r') as f:
        organizations_json = json.load(f)

    api_data = api_data_CF
    ids = api_data.parseIds(organizations_json)
    
    assert ids == ['id_1', 'id_2']
    
def test_parseIds_none():
    with open('tests/support/sample_organizations.json', 'r') as f:
        organizations_json = None

    api_data = api_data_CF
    ids = api_data.parseIds(organizations_json)
    
    assert ids == None
    
@patch('haas_websocket.rest.haas_rest_handler.TokenAuth')
def test_getAllThings(mTokenAuth):
    with open('tests/support/sample_thing_list.json', 'r') as f:
        things_json = json.load(f)
        data = things_json['data']

    mTokenAuth.getThings = MagicMock(return_value = things_json)

    api_data = api_data_CF
    things = api_data.getAllThings(mTokenAuth, ['id'])
    
    assert things == data

@patch('haas_websocket.rest.haas_rest_handler.TokenAuth')
def test_getAllThings_none(mTokenAuth):

    mTokenAuth.getThings = MagicMock(return_value = None)

    api_data = api_data_CF
    things = api_data.getAllThings(mTokenAuth, [])
    
    assert things == None

@patch('haas_websocket.rest.haas_rest_handler.TokenAuth')
def test_getAllLocations(mTokenAuth):
    with open('tests/support/sample_locations_list.json', 'r') as f:
        locations_json = json.load(f)
        data = locations_json['data']

    mTokenAuth.getLocations = MagicMock(return_value = locations_json)

    api_data = api_data_CF
    locations = api_data.getAllLocations(mTokenAuth, ['id'])
    
    assert locations == data

@patch('haas_websocket.rest.haas_rest_handler.TokenAuth')
def test_getAllLocations_none(mTokenAuth):

    mTokenAuth.getThings = MagicMock(return_value = None)

    api_data = api_data_CF
    locations = api_data.getAllLocations(mTokenAuth, [])
    
    assert locations == None
    
@patch('google.cloud.datastore.Client')
def test_createDatastoreTasks(mDatastoreClient):
    with open('tests/support/sample_location.json', 'r') as f:
        location_json = json.load(f)
        id = location_json[0]['id']
    
    kind = "HaasAlertLocations"
    api_data = api_data_CF
    locations = api_data.createDatastoreTasks(mDatastoreClient, location_json, kind)
    
    mDatastoreClient.key.assert_called_with(kind, id)

@patch('google.cloud.datastore.Client')
def test_createDatastoreTasks_none(mDatastoreClient):
   
    kind = "HaasAlertLocations"
    api_data = api_data_CF
    locations = api_data.createDatastoreTasks(mDatastoreClient, [], kind)
    
    mDatastoreClient.key.assert_not_called()