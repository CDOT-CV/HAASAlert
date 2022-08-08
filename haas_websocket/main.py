import os
import json
import websocket
import logging
import signal
import sys
import threading
from haas_websocket.rest.haas_rest_handler import TokenAuth
from google.cloud import pubsub_v1
from flask import Flask, request

app = Flask(__name__)
running = False

@app.get("/")
def hello():
    """Return a friendly HTTP greeting."""
    who = request.args.get("who", default="World")
    return f"Hello {who}!\n"

@app.get("/start_websocket")
def start_websocket():
    global running, thread
    if running == False:
        publisher = pubsub_v1.PublisherClient()
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
        thread = threading.Thread(target=startWebsocket, name="websocket thread", args=(publisher,))
        thread.start()
        return f"Successfully started websocket!\n"
    else:
        return f"Websocket is already started."
    
@app.get("/status")
def status():
    global thread
    state = thread.is_alive()
    if state == True:
        status = 'Alive'
    else:
        status = 'Failed'
        
    return f"Websocket status: {status}."
        
        
def signal_handler(sig, frame):
    global running, thread
    running = False
    print('You pressed Ctrl+C!')
    sys.exit(0)

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
    if data_type == 'point':
        path = publisher.topic_path(project_id, os.getenv('POINT_TOPIC'))
        returnMessage = 'point'
    elif data_type == 'heartbeat':
        path = publisher.topic_path(project_id, os.getenv('HEARTBEAT_TOPIC'))
        returnMessage = 'heartbeat'
    elif data_type == 'thing':
        path = publisher.topic_path(project_id, os.getenv('THING_TOPIC'))
        returnMessage = 'thing'
    elif data_type == 'location':
        path = publisher.topic_path(project_id, os.getenv('LOCATION_TOPIC'))
        returnMessage = 'location'
    elif data_type is None and data.get('keepAlive'):
        returnMessage = 'keepAlive'
    else:
        returnMessage = 'Unknown'
    if path and returnMessage:
        publishMessage(publisher,path,encoded)
        published = True
    
    return returnMessage, published

def startWebsocket(publisher):
    global running
    running = True
    rest = restSignIn()
    b_token = rest.getToken()
    ws_endpoint = os.getenv('HAAS_WSS_ENDPOINT')
    ws = websocket.create_connection(ws_endpoint+b_token)
    while running == True:
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
                    logging.info(f"Successfully pushed {msg_type} message to pub/sub: {result}")
                else:
                    logging.info(f"Successfully recieved {msg_type} message, did not publish to pub/sub.")
            except KeyboardInterrupt:
                break
            
    rest.signOut()
    ws.close()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    app.run(host="0.0.0.0", port=8080, debug=True)