from haas_websocket.rest.haas_rest_handler import TokenAuth
from google.cloud import datastore
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

def getAllThings(rest_agent, list):
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

def getAllLocations(rest_agent, list):
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
                logging.info(entry["id"] + " added to datastore")
            else:
                logging.info(entry["id"] + " already in list")
        return tasks
    else:
        return None

# Entry point for cloud function
def entry(request):
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    rest_agent = TokenAuth()
    rest_agent.signIn()
    organizations = rest_agent.getOrganizations()
    logging.info (f'organizations: {organizations}')
    listIds = parseIds(organizations)
    logging.info (f'listIds: {listIds}')
    allThings = getAllThings(rest_agent, listIds)
    logging.info (f'allThings: {allThings}')
    allLocations = getAllLocations(rest_agent, listIds)
    logging.info (f'allLocations: {allLocations}')

    datastore_client = datastore.Client()
    thingTasks = createDatastoreTasks(datastore_client, allThings, "HaasAlertThings")
    locationTasks = createDatastoreTasks(datastore_client, allLocations, "HaasAlertLocations")
    datastore_client.put_multi(thingTasks)
    datastore_client.put_multi(locationTasks)

    rest_agent.signOut()