# Mushroom App - APIs & Frontend App

In this tutorial add on more functionality to the following containers:
* api-service
* frontend-simple

The following container architecture is what we have built so far:

![Docker with Persistent Store](https://storage.googleapis.com/public_colab_images/docker/docker_with_network.png)


## Prerequisites

### Ensure containers are running
- Ensure `database-server` is running
- Ensure `api-service` is running and accessible at `http://localhost:9000/`. Run `uvicorn_server` to make sure API Service is running.
- Ensure `frontend-simple` is running and accessible at `http://localhost:8080/`. Run `http-server` to make sure web server is running.

## Create API for the leaderboard list

In this section we will query the database for the leaderboard and return it to the API as a list of json objects

### First we will create a data access method
- In the `api-service` folder under dataaccess create a new python file `leaderboard.py`
- Add the following code block

`leaderboard.py`
```
import os
from typing import Any, Dict, List
from dataaccess.session import database


async def browse(
    *,
    limit: int = -1
) -> List[Dict[str, Any]]:
    """
    Retrieve a list of rows based on filters
    """

    query = """
        select *
        from leaderboard
    """

    # limit
    if limit > 0:
        query += " limit " + str(limit)

    print("query", query)
    result = await database.fetch_all(query)

    return [prep_data(row) for row in result]


def prep_data(result) -> Dict[str, Any]:
    if result is None:
        raise ValueError("Tried to prepare null result")

    result = dict(result)
    return result
```

### Create an API route to expose return the leaderboard data
- Modify `service.py` to call this database method to get the leaderboard data
- Add the following import in `service.py`

`service.py`
```
from dataaccess import leaderboard
```

- At the bottom of `service.py` add the following new route

`service.py`
```
@app.get("/leaderboard")
async def get_leaderboard():
    return leaderboard.browse()
```

- You can access this new route from the browser at 'http://localhost:9000/leaderboard'

### 🎉 What did we just do? 
* We read some data from a table in a **PostgreSQL** container. 
* Converted the data to list of dictionary objects in **Python** 
* Exposed the results as a REST API using **FastAPI**
