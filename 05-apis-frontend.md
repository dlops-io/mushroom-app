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

## Create API for the leaderboard list [`api-service` Container]

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

## Create a leaderboard page [`frontend-simple` Container]

In this section we will consume our leaderboard API and display a table of results.

### First we add a new HTML page 
- In the `frontend-simple` folder add a new file called `leaderboard.html`
- Add the following code inside `leaderboard.html`

`leaderboard.html`
```
<!DOCTYPE html>
<html>

<head>
    <title>🍄 Mushroom Identifier: Leaderboard</title>
    <!-- Add reference to Google fonts -->
    <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">
    <!-- Google Material Design Styles -->
    <link href="https://unpkg.com/material-components-web@latest/dist/material-components-web.min.css" rel="stylesheet">
    <script src="https://unpkg.com/material-components-web@latest/dist/material-components-web.min.js"></script>
    <!-- Add javascript package axios for accesing APIs -->
    <script src="https://unpkg.com/axios/dist/axios.min.js"></script>

    <!-- Add Stylesheet -->
    <style>
        body {
            margin: 0;
            background-color: #efefef;
        }

        .mdc-top-app-bar {
            background-color: #1c4385;
        }

        .content {

            display: flex;
            flex-direction: column;
            width: 100%;
            align-items: center;
        }

        .container {
            max-width: 650px;
            width: 100%;
            box-sizing: border-box;
        }
    </style>
</head>

<body>
    <!-- Header -->
    <header class="mdc-top-app-bar" style="align-items: center;position: relative;">
        <div class="mdc-top-app-bar__row" style="max-width: 700px;">
            <section class="mdc-top-app-bar__section mdc-top-app-bar__section--align-start">
                <button class="material-icons mdc-top-app-bar__navigation-icon mdc-icon-button"
                    aria-label="Open navigation menu">menu</button>
                <span class="mdc-top-app-bar__title" style="font-weight: 900; font-size: 30px;">🍄 Mushroom
                    Identifier</span>
            </section>
        </div>
    </header>
    <!-- Header -->

    <!-- Content -->
    <div class="content">

    </div>
    <!-- Content -->
</body>
<!-- Add Javascript -->
<script>

</script>

</html>
```
