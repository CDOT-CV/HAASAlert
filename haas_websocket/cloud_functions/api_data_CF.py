from haas_websocket.rest.haas_rest_handler import TokenAuth
from google.cloud import datastore
import logging

# Will run on an interval in GCP as a cloud function to regenerate the bearer token each day
client = datastore.Client()

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

def getAllLocations(list):
    if list:
        locations = []
        for id in list:
            newLocations = rest_agent.getLocations(id)
            if newLocations:
                for thing in newLocations['data']:
                    locations.append(thing)
        return locations
    else:
        return None

def createDatastoreTasks(list, kind):
    if list: 
        tasks = []
        appliedLocations = []
        for entry in list:
            if not entry["id"] in appliedLocations:
                newTask = datastore.Entity(client.key(kind, entry["id"]))
                newTask.update(entry)
                appliedLocations.append(entry["id"])
                tasks.append(newTask)
            else:
                logging.info(entry["id"] + " already in list")
        return tasks
    else:
        return None

# def refresh_token(request):
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
rest_agent = TokenAuth()
rest_agent.signIn()
organizations = rest_agent.getOrganizations()
logging.info (organizations)
listIds = parseIds(organizations)
allThings = getAllThings(listIds)
allLocations = getAllLocations(listIds)

thingTasks = createDatastoreTasks(allThings, "HaasAlertThings")
locationTasks = createDatastoreTasks(allLocations, "HaasAlertLocations")
client.put_multi(thingTasks)
client.put_multi(locationTasks)

rest_agent.signOut()