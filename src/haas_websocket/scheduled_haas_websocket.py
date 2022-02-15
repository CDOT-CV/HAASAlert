import json
import time
import threading
import os
import requests
import schedule
import websocket
import atexit
from datetime import datetime
from haas_rest_handler_class import TokenAuth
from dotenv import load_dotenv
from google.cloud import secretmanager
from google.cloud import pubsub_v1

load_dotenv()

rest_agent = TokenAuth()

def publishMessage(jsonData):
    publisher = pubsub_v1.PublisherClient()

    all_types_path = publisher.topic_path(os.getenv('PROJECT_ID'), os.getenv('ALL_TYPES_TOPIC'))
    heartbeat_path = publisher.topic_path(os.getenv('PROJECT_ID'), os.getenv('HEARTBEAT_TOPIC'))
    location_path = publisher.topic_path(os.getenv('PROJECT_ID'), os.getenv('LOCATION_TOPIC'))
    point_path = publisher.topic_path(os.getenv('PROJECT_ID'), os.getenv('POINT_TOPIC'))
    thing_path = publisher.topic_path(os.getenv('PROJECT_ID'), os.getenv('THING_TOPIC'))
    
    encoded = jsonData.encode("utf-8")
    data = json.loads(jsonData)

    publisher.publish(all_types_path, encoded) # publishes messages to the testing topic for all types of messages

    # Filters the messages and publishes messages to specified topic
    if 'keepAlive' in data:
        return 'keepAlive'
    if 'type' in data:
        if data['type'] == 'point':
            publisher.publish(point_path, encoded)
            return 'point'
        if data['type'] == 'heartbeat':
            publisher.publish(heartbeat_path, encoded)
            return 'heartbeat'
        if data['type'] == 'thing':
            publisher.publish(thing_path, encoded)
            return 'thing'
        if data['type'] == 'location':
            publisher.publish(location_path, encoded)
            return 'location'

def start_websocket(rest):
    b_token = rest.getToken()
    project_id = os.environ['PROJECT_ID']
    ws_endpoint = os.environ['HAAS_WSS_ENDPOINT']

    ws = websocket.create_connection(ws_endpoint+b_token)
    
    publisher = pubsub_v1.PublisherClient()

    while 1:
    
        if rest.checkPassword():
            if rest.checkToken(): # checks if local bearer_token is the same as the gcp token
                try:
                    result = ws.recv() 
                    msg_type = publishMessage(result)
                    print(f"(INFO) Successfully pushed {msg_type} message pub/sub. \n Full Message: {result}")
                except KeyboardInterrupt:
                    break
            else:
                ws.close()
                b_token = rest.tokenUpdate() # updates local token from the secret manager
                ws = websocket.create_connection(ws_endpoint+b_token) # restarts the websocket
        else:
            ws.close()
            rest.passwordUpdate() # updates local token from the secret manager
            b_token = rest.signIn()
            ws = websocket.create_connection(ws_endpoint+b_token) # restarts the websocket

    ws.close()

rest_agent.signIn()
start_websocket(rest_agent)