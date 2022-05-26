from haas_websocket.rest.haas_rest_handler import TokenAuth
import logging

# Will run on an interval in GCP as a cloud function to regenerate the bearer token each day

def parseIds (organizations):
    if organizations:
        ids = []
        for item in organizations['managed_orgs']:
            ids.append(item['id'])
        return ids 
    else:
        return None

def getAllThings(list):
    if list:
        things = []
        for id in list:
            newThings = rest_agent.getThings(id)
            if newThings:
                for thing in newThings['data']:
                    things.append(thing)
        return things
    else:
        return None

# def refresh_token(request):
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
rest_agent = TokenAuth()
rest_agent.signIn()
organizations = rest_agent.getOrganizations()
listIds = parseIds(organizations)
allThings = getAllThings(listIds)
logging.info(allThings)
rest_agent.signOut()