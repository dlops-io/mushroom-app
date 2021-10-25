# Mushroom App - Setup & Code Organization

In this tutorial we will continue to work with the three containers from the previous tutorial:
* api-service
* data-collector
* frontend-simple

The following container architecture is what we have implemented so far:

![Docker setup for Mushroom App](https://storage.googleapis.com/public_colab_images/docker/docker_containers_mushroom_app2.png)

## Download Models for App
Next step is to have the `api-service` monitor the GCP bucket for any new models and pull download the best model. We will also keep track of a leaderboard.

### Setup a Tracker
- Install Tensorflow
- Run this in `api-service` docker shell
```
pipenv install tensorflow
```

- Add a python file [api/tracker.py](https://github.com/dlops-io/mushroom-app/releases/download/v1.1/tracker.py)

- Update `service.py` to initiate `TrackerService` and call it on startup
- Add the following new imports
```
import asyncio
from api.tracker import TrackerService
```

- Add code to initialize the tracker, this can be right before "Setup FastAPI app"
```
# Initialize Tracker Service
tracker_service = TrackerService()
```

- Add startup and shutdown events, add this after "Enable CORSMiddleware"
```
@app.on_event("startup")
async def startup():
    # Startup tasks
    # Start the tracker service
    asyncio.create_task(tracker_service.track())


@app.on_event("shutdown")
async def shutdown():
    # Shutdown tasks
    ...
```

### Run the API Service and test
- Run `uvicorn_server` and wait for 60 seconds


