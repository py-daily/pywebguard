import meilisearch

client = meilisearch.Client(
    "https://meilisearch.dev.ktechhub.com", "skn1qYHdGWYO7MsXKkDFKCcX3ap87O1a"
)

logs_index = client.index("pywebguard")

from datetime import datetime, timedelta
import time
import json

# Convert to UNIX timestamp (seconds)
start_time = int((datetime.now() - timedelta(hours=5)).timestamp())
end_time = int(datetime.now().timestamp())

# Perform the search
list_data = logs_index.get_documents()
print(list_data.results)
print([dict(data) for data in list_data.results])
