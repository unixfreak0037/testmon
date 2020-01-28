# testmon
Testing some CI/CD pipeline stuff

## Overview

This repo was built to test out docker and CI/CD pipelines.

The application is a python FastAPI application that uses a Redis backend.

The application is designed to report if long running jobs have run for too long.

The application takes an HTTP POST and saves the app_id (key) and expiration (datetime value in ctime)
to a Redis service. The expiration is the sum of the time of the 'start' request and the number of seconds passed
in the 'duration' field within the request json body. The 'duration' is the maximum time the job (think cron job or
backup) should run before being considered 'slow' or 'late'.

When an HTTP POST request containing the 'action': 'stop' key/value pair in the json body, the app
will compare the 'stop' time with the redis content for the app_id to determine if the job was on-time or late.

## Create your images for local testing

#### Docker image with python dependencies
```bash
$ docker build -t -f pylibraries.Dockerfile krayzpipes/pylibraries .
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
