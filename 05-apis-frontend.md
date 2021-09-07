# Mushroom App - APIs & Frontend App

In this tutorial add on more functionality to the following containers:
* api-service
* frontend-simple

The following container architecture is what we have built so far:

![Docker with Persistent Store](https://storage.googleapis.com/public_colab_images/docker/docker_with_network.png)


## Prerequisites

### Ensure containers are running
- Ensure you have already run `sh docker-shell.sh` or `docker-shell.bat` in each container folder.
- Ensure `database-server` is running and you have run `dbmate up` if you have not already done in the previous tutorial
- Ensure `api-service` is running and accessible at `http://localhost:9000/`. Run `uvicorn_server` to make sure API Service is running.
- Ensure `frontend-simple` is running and accessible at `http://localhost:8080/`. Run `http-server` to make sure web server is running.

## Create API for the leaderboard list [`api-service` Container]

In this section we will query the database for the leaderboard and return it to the API as a list of json objects

### First we will create a data access method
- In the `api-service` folder under `dataaccess` create a new python file `leaderboard.py`
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
        .MuiTable-root {
            width: 100%;
            display: table;
            border-spacing: 0;
            border-collapse: collapse;
        }

        .MuiTableRow-root {
            color: inherit;
            display: table-row;
            outline: 0;
            vertical-align: middle;
        }

        .MuiTableCell-head {
            color: rgba(0, 0, 0, 0.87);
            font-weight: 500;
            line-height: 1.5rem;
        }

        .MuiTableCell-root {
            display: table-cell;
            padding: 16px;
            font-size: 0.875rem;
            text-align: left;
            font-family: "Roboto", "Helvetica", "Arial", sans-serif;
            font-weight: 400;
            line-height: 1.43;
            border-bottom: 1px solid rgba(224, 224, 224, 1);
            letter-spacing: 0.01071em;
            vertical-align: inherit;
        }
        .MuiTableCell-body {
            color: rgba(0, 0, 0, 0.87);
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
        <table class="MuiTable-root">
            <thead class="MuiTableHead-root">
                <tr class="MuiTableRow-root MuiTableRow-head">
                    <th class="MuiTableCell-root MuiTableCell-head" scope="col"></th>
                    <th class="MuiTableCell-root MuiTableCell-head" scope="col">User</th>
                    <th class="MuiTableCell-root MuiTableCell-head" scope="col">Model</th>
                    <th class="MuiTableCell-root MuiTableCell-head" scope="col">Trainable Parameters</th>
                    <th class="MuiTableCell-root MuiTableCell-head" scope="col">Training Time (mins)</th>
                    <th class="MuiTableCell-root MuiTableCell-head" scope="col">Loss</th>
                    <th class="MuiTableCell-root MuiTableCell-head" scope="col">Accuracy</th>
                    <th class="MuiTableCell-root MuiTableCell-head" scope="col">Model Size (Mb)</th>
                    <th class="MuiTableCell-root MuiTableCell-head" scope="col">Learning Rate</th>
                    <th class="MuiTableCell-root MuiTableCell-head" scope="col">Batch Size</th>
                    <th class="MuiTableCell-root MuiTableCell-head" scope="col">Epochs</th>
                    <th class="MuiTableCell-root MuiTableCell-head" scope="col">Optimizer</th>
                </tr>
            </thead>
            <tbody class="MuiTableBody-root" id="table_rows">

            </tbody>
        </table>
    </div>
    <!-- Content -->
</body>
<!-- Add Javascript -->
<script>

</script>

</html>
```

- Go to `http://localhost:8080/leaderboard.html` and what do you see?

### Get data from API  
- Next let's add some code to call the API and get the leaderboard list from the backend `api-service`
- Open `leaderboard.html` file and add this code block in the `<script></script>` section:

```
<script>
    // API URL
    axios.defaults.baseURL = 'http://localhost:9000/';

    // Our leaderboard list
    var leaderboard = [];

    // Call the API
    axios.get('/leaderboard')
        .then((response) => {
            console.log(response.data);
            // Save the response to a list
            leaderboard = response.data;

            // Build the table
            // ...
        });
</script>
```

- Refresh the page `http://localhost:8080/leaderboard.html` and check the Chrome Developer tools console
- What do you see?
- There should be an array with the leaderboard data

### First we add a new HTML page 
- Build the HTML table with the leaderboard data
- Open `leaderboard.html` file and add this code to the end of the `<script>...</script>` block:

```
// Add a function to build the leaderboard table
function buildLeaderboardTable(leaderboard) {
    // Get a reference to the UI element table_rows
    var table_rows = document.getElementById("table_rows");

    // build rows
    let rows = "";
    leaderboard.forEach(function (item, index) {
        rows += "<tr class='MuiTableRow-root'>";
        rows += "<td class='MuiTableCell-root MuiTableCell-body'>" + item["id"] + "</td>";
        rows += "<td class='MuiTableCell-root MuiTableCell-body'>" + item["email"] + "</td>";
        rows += "<td class='MuiTableCell-root MuiTableCell-body'>" + item["model_name"] + "</td>";
        rows += "<td class='MuiTableCell-root MuiTableCell-body'>" + item["trainable_parameters"] + "</td>";
        rows += "<td class='MuiTableCell-root MuiTableCell-body'>" + Math.round(item["execution_time"], 2) + "</td>";
        rows += "<td class='MuiTableCell-root MuiTableCell-body'>" + Math.round(item["loss"], 3) + "</td>";
        rows += "<td class='MuiTableCell-root MuiTableCell-body'>" + Math.round(item["accuracy"] * 100.0, 2) + "</td>";
        rows += "<td class='MuiTableCell-root MuiTableCell-body'>" + Math.round(item["model_size"] / 1000000.00, 0) + "</td>";
        rows += "<td class='MuiTableCell-root MuiTableCell-body'>" + item["learning_rate"] + "</td>";
        rows += "<td class='MuiTableCell-root MuiTableCell-body'>" + item["batch_size"] + "</td>";
        rows += "<td class='MuiTableCell-root MuiTableCell-body'>" + item["epochs"] + "</td>";
        rows += "<td class='MuiTableCell-root MuiTableCell-body'>" + item["optimizer"] + "</td>";
        rows += "</tr>"
    });

    table_rows.innerHTML = rows;
}
```

- Call the `buildLeaderboardTable(...)` after we get the data from the API
- Add this line after this line `// Build the table`

```
buildLeaderboardTable(leaderboard);
```

### 🎉 Congratulations 🎉
Now we have completed:
* Reading data from a table in a **PostgreSQL** container. 
* Converted the data to list of dictionary objects in **Python** 
* Exposed the results as a REST API using **FastAPI**
* Called the API to get the leaderboard data
* Displayed the data in a HTML table