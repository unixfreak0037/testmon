# testmon
Testing some CI/CD pipeline stuff

## Overview

This repo was built to test out docker and CI/CD pipelines.

Features of the test application:
- FastAPI app logic with Redis backend
- Designed to alert the client if their jobs took to long to run (ex: Cronjob)
    - HTTP POST body with `{"app_id": "abcd", "action": "start", "duration": 3600}` would:
        - Store the app_id as a key in the redis backend.
        - Start the monitor by taking the sum of the current time + duration, and saving it as
        the value in the redis backend. This is considered the `expiration` time.
    - HTTP POST body with `{"app_id": "abcd", "action": "stop"}` would:
        - Look for a key named `abcd` in the redis backend.
        - Take the value from the redis backend and see if the current time is before or after
        the value that was stored in the redis backend.
        - If the current time is later than the expiration time, then the respone to this HTTP POST
        will contain a message saying the job was late.


## Create your images for local testing via containers

#### Docker image with python dependencies
```bash
$ docker build -t krayzpipes/pylibraries -f pylibraries.Dockerfile .
```

#### Docker image for redis
```bash
$ docker build -t -f redis.Dockerfile krayzpipes/redis .
```

#### Docker image for the app
```bash
$ docker build -t krayzpipes/testmon .
```

#### Create docker network
```bash
# We'll use this to let the containers talk to each other.
$ docker network create testmon-net
```

#### Run the containers
```bash
# Make sure you name the redis container red1... otherwise change
# your dockerfile to reflect the actual name you designated.
$ docker run --network testmon-net --name red1 -d krayzpipes/redis
$ docker run --network testmon-net --name web1 -d -p 8080:80 krayzpipes/testmon
```

## Test it with requests
```python
import json

import requests

start = {"app_id": "abcdefg", "action": "start", "duration": 3600}
stop = {"app_id": "abcdefg", "action": "stop"}

start_request = requests.post('http://127.0.0.1:8080/testmon/monitor', json=start)
print(start_request)

stop_request = requests.post('http://127.0.0.1:8080/testmon/monitor', json=stop)
print(stop_request)
```
