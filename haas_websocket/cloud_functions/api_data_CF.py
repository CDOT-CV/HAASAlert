from haas_websocket.rest.haas_rest_handler import TokenAuth
from google.cloud import datastore
import logging
import os


def setClients():
    rest_agent = TokenAuth()
    datastore_client = datastore.Client()
    return rest_agent, datastore_client

def parseIds (organizations):
    if organizations:
        ids = []
        for item in organizations['managed_orgs']:
            ids.append(item['id'])
        return ids 
    else:
        return None

def getAllThings(rest_agent, list):
    if list:
        things = []
        for id in list:
            things += rest_agent.getThings(id)
        return things
    else:
        return None

def getAllLocations(rest_agent, list):
    if list:
        locations = []
        for id in list:
            locations += rest_agent.getLocations(id)
        return locations
    else:
        return None

def createDatastoreTasks(client, list, kind):
    if list: 
        tasks = []
        appliedTasks = []
        for entry in list:
            if not entry["id"] in appliedTasks:
                newTask = datastore.Entity(client.key(kind, entry["id"]))
                newTask.update(entry)
                appliedTasks.append(entry["id"])
                tasks.append(newTask)
            else:
                logging.info(entry["id"] + " already in " + kind + " list")
        return tasks
    else:
        return None

def parseApiData(rest_agent):
    rest_agent.signIn()
    organizations = rest_agent.getOrganizations()
    listIds = parseIds(organizations)
    allThings = getAllThings(rest_agent, listIds)
    allLocations = getAllLocations(rest_agent, listIds)
    return allLocations, allThings

def uploadApiData(datastore_client, allLocations, allThings):
    thingTasks = createDatastoreTasks(datastore_client, allThings, "HaasAlertThings")
    locationTasks = createDatastoreTasks(datastore_client, allLocations, "HaasAlertLocations")
    if thingTasks:
        datastore_client.put_multi(thingTasks)
        logging.info(f'Uploaded {len(thingTasks)} things to datastore.')
    else:
        logging.warning(f'No thing tasks to upload to datastore')
    if locationTasks:
        datastore_client.put_multi(locationTasks)
        logging.info(f'Uploaded {len(locationTasks)} locations to datastore.')
    else:
        logging.warning(f'No location tasks to upload to datastore')
    
    if locationTasks or thingTasks:
        return len(locationTasks), len(thingTasks)


# Entry point for cloud function
def entry(request,message):
    log_level = 'INFO' if "LOGGING_LEVEL" not in os.environ else os.environ['LOGGING_LEVEL'] 
    logging.basicConfig(format='%(levelname)s:%(message)s', level=log_level)

    rest_agent, datastore_client = setClients()
    allLocations, allThings = parseApiData(rest_agent)
    rest_agent.signOut()
    locationUploadLength, thingUploadLength = uploadApiData(datastore_client, allLocations, allThings)
    
    return locationUploadLength, thingUploadLength