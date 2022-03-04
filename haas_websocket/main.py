import os
import json
import websocket
import logging
from haas_websocket.haas_rest_handler import TokenAuth
from dotenv import load_dotenv
from google.cloud import pubsub_v1

def restSignIn():
    rest_agent = TokenAuth()
    rest_agent.signIn()
    return rest_agent

def publishMessage(publisher, path, message):
    future = publisher.publish(path, message)

def filterMessage(jsonData,publisher):
    project_id = os.getenv('PROJECT_ID')
    if not project_id:
        return False
    
    encoded = jsonData.encode("utf-8")
    data = json.loads(jsonData)
    returnMessage = None
    path = None
    published = False
    
    data_type = data.get('type')
    # Filters the messages and publishes messages to specified topic
    if data_type == 'point':
        path = publisher.topic_path(os.getenv('PROJECT_ID'), os.getenv('POINT_TOPIC'))
        returnMessage = 'point'
    elif data_type == 'heartbeat':
        path = publisher.topic_path(os.getenv('PROJECT_ID'), os.getenv('HEARTBEAT_TOPIC'))
        returnMessage = 'heartbeat'
    elif data_type == 'thing':
        path = publisher.topic_path(os.getenv('PROJECT_ID'), os.getenv('THING_TOPIC'))
        returnMessage = 'thing'
    elif data_type == 'location':
        path = publisher.topic_path(os.getenv('PROJECT_ID'), os.getenv('LOCATION_TOPIC'))
        returnMessage = 'location'
    elif data_type is None:
        returnMessage = 'keepAlive'
    if path and returnMessage:
        publishMessage(publisher,path,encoded)
        published = True

    
    return returnMessage, published

def running():
    return True

def startWebsocket(publisher):
    rest = restSignIn()
    b_token = rest.getToken()
    ws_endpoint = os.getenv('HAAS_WSS_ENDPOINT')
    ws = websocket.create_connection(ws_endpoint+b_token)
    while running() == True:
        check_pass = rest.checkPassword()
        check_token = rest.checkToken()
        if check_pass == False:
            ws.close()
            rest.passwordUpdate() # updates local token from the secret manager
            b_token = rest.signIn()
            ws = websocket.create_connection(ws_endpoint+b_token) # restarts the websocket
        if check_token == False:
            ws.close()
            b_token = rest.tokenUpdate() # updates local token from the secret manager
            ws = websocket.create_connection(ws_endpoint+b_token) # restarts the websocket
        if check_pass == True and check_token == True:
            try:
                result = ws.recv() 
                msg_type, published = filterMessage(result,publisher)
                if published == True:
                    logging.info(f"Successfully pushed {msg_type} message pub/sub. \nFull Message: {result}")
                else:
                    logging.info(f"Successfully recieved {msg_type} message, did not publish to pub/sub \nFull Message: {result}")
            except KeyboardInterrupt:
                break
            
    rest.signOut()
    ws.close()


if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    publisher = pubsub_v1.PublisherClient()
    startWebsocket(publisher)