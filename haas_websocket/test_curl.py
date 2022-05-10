from requests import get
from google.cloud import secretmanager


response = get('https://psrc-4rw99.us-central1.gcp.confluent.cloud/subjects', auth=('r6sg23ejweri3g4z', 'kafka'))
print (response)
print (response.content)
print (response.json)