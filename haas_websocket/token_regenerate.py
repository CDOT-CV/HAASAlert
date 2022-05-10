import os
from dotenv import load_dotenv
import logging
import signal
import sys
import time
from google.cloud import pubsub_v1
from haas_websocket.rest.haas_rest_handler import TokenAuth

load_dotenv()

def refresh_token(message):
    rest_agent = TokenAuth()
    rest_agent.refreshToken()
    rest_agent.signOut()
    message.ack()

def create_callback():
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(os.getenv('PROJECT_ID'), os.getenv('BEARER_REFRESH_TOPIC'))

    logging.info(f"Listening for messages on {subscription_path}..")
    future = subscriber.subscribe(subscription_path, callback=refresh_token)
    return future


if __name__ == '__main__':
    # signal.signal(signal.SIGINT, signal_handler)
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    future = create_callback()
    
    while True:
        time.sleep(15)
        if (future.running() != True):
            future = create_callback()
