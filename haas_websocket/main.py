import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import websocket
from haas_websocket.haas_rest_handler import TokenAuth
from dotenv import load_dotenv
from google.cloud import pubsub_v1

def restSignIn():
    rest_agent = TokenAuth()
    rest_agent.signIn()
    return rest_agent

def publishMessage(publisher, path, message):
    print (f"publishMessage module, publishing message. \npath: {path} \nmessage: {message}")
    future = publisher.publish(path, message)
    print(future.result())

def filterMessage(jsonData,publisher):
    project_id = os.getenv('PROJECT_ID')
    if not project_id:
        return False
    
    encoded = jsonData.encode("utf-8")
    data = json.loads(jsonData)
    
    returnMessage = None
    path = None
    published = False
    # Filters the messages and publishes messages to specified topic
    if 'keepAlive' in data:
        returnMessage = 'keepAlive'
    if 'type' in data:       
        if data['type'] == 'point':
            path = publisher.topic_path(os.getenv('PROJECT_ID'), os.getenv('POINT_TOPIC'))
            returnMessage = 'point'
        if data['type'] == 'heartbeat':
            path = publisher.topic_path(os.getenv('PROJECT_ID'), os.getenv('HEARTBEAT_TOPIC'))
            returnMessage = 'heartbeat'
        if data['type'] == 'thing':
            path = publisher.topic_path(os.getenv('PROJECT_ID'), os.getenv('THING_TOPIC'))
            returnMessage = 'thing'
        if data['type'] == 'location':
            path = publisher.topic_path(os.getenv('PROJECT_ID'), os.getenv('LOCATION_TOPIC'))
            returnMessage = 'location'
        if path and returnMessage:
            publishMessage(publisher,path,encoded)
            published = True
            
    return returnMessage, published

def startWebsocket(publisher):
    rest = restSignIn()
    b_token = rest.getToken()
    ws_endpoint = os.getenv('HAAS_WSS_ENDPOINT')

    ws = websocket.create_connection(ws_endpoint+b_token)

    while True:
        if rest.checkPassword():
            if rest.checkToken(): # checks if local bearer_token is the same as the gcp token
                try:
                    result = ws.recv() 
                    msg_type, published = filterMessage(result,publisher)
                    if published == True:
                        print(f"(INFO) Successfully pushed {msg_type} message pub/sub. \n Full Message: {result}")
                    else:
                        print(f"(INFO) Successfully recieved {msg_type} message, did not publish to pub/sub \n Full Message: {result}")
                except KeyboardInterrupt:
                    break
            else:
                ws.close()
                b_token = rest.tokenUpdate() # updates local token from the secret manager
                ws = websocket.create_connection(ws_endpoint+b_token) # restarts the websocket
        else:
            print("in checkPassword")
            ws.close()
            rest.passwordUpdate() # updates local token from the secret manager
            b_token = rest.signIn()
            ws = websocket.create_connection(ws_endpoint+b_token) # restarts the websocket
    rest.signOut()
    ws.close()
    return True
    


if __name__ == "__main__":
    publisher = pubsub_v1.PublisherClient()
    startWebsocket(publisher)