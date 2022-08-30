import os
import json
import websocket
import logging
from haas_websocket.rest.haas_rest_handler import TokenAuth
from google.cloud import pubsub_v1

def restSignIn():
    rest_agent = TokenAuth()
    rest_agent.signIn()
    return rest_agent

def publishMessage(publisher, path, message):
    future = publisher.publish(path, message)

def filterMessage(message,publisher):
    project_id = os.getenv('PROJECT_ID')
    if not project_id:
        return False
    
    encoded = message.encode("utf-8")
    data = json.loads(message)
    returnMessage = None
    path = None
    published = False
    
    data_type = data.get('type')
    # Filters the messages and publishes messages to specified topic
    if data_type == 'point' or data_type == 'heartbeat' or data_type == 'thing' or data_type == 'location':
        path = publisher.topic_path(project_id, 'haas-alert-raw')
        returnMessage = data_type
    elif data_type is None and data.get('keepAlive'):
        returnMessage = 'keepAlive'
    else:
        returnMessage = 'Unknown'
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
        check_token = rest.checkToken()
        if check_token == False:
            ws.close()
            b_token = rest.refreshToken() # updates local token from the secret manager
            ws = websocket.create_connection(ws_endpoint+b_token) # restarts the websocket
        if check_token == True:
            try:
                result = ws.recv() 
                msg_type, published = filterMessage(result,publisher)
                if published == True:
                    logging.info(f"Successfully pushed {msg_type} message pub/sub. \nFull Message: {result}")
                else:
                    logging.info(f"Successfully received {msg_type} message, did not publish to pub/sub \nFull Message: {result}")
            except KeyboardInterrupt:
                break
            
    rest.signOut()
    ws.close()


if __name__ == "__main__":
    log_level = 'INFO' if "LOGGING_LEVEL" not in os.environ else os.environ['LOGGING_LEVEL'] 
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=log_level, datefmt='%Y-%m-%d %H:%M:%S')

    publisher = pubsub_v1.PublisherClient()
    startWebsocket(publisher)