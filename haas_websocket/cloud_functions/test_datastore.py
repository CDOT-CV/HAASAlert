from google.cloud import datastore
import logging

# Will run on an interval in GCP as a cloud function to regenerate the bearer token each day
client = datastore.Client()

# task1 = datastore.Entity(client.key("Task", 1))

# task1.update(
#     {
#         "category": "Personal",
#         "done": False,
#         "priority": 4,
#         "description": "Learn Cloud Datastore",
#     }
# )

# task2 = datastore.Entity(client.key("Task", 2))

# task2.update(
#     {
#         "category": "Work",
#         "done": False,
#         "priority": 8,
#         "description": "Integrate Cloud Datastore",
#     }
# )

# client.put_multi([task1, task2])

keys = [client.key("Task", 1), client.key("Task", 2)]
tasks = client.get_multi(keys)
print(tasks)