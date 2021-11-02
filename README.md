# Mushroom App - APIs & Frontend App


In this tutorial add on more functionality to the following containers:
* api-service
* frontend-simple

and we will add a new container
* frontend-react

The following container architecture is what we have implemented so far:

![Docker setup for Mushroom App](https://storage.googleapis.com/public_colab_images/docker/docker_containers_mushroom_app2.png)

## Create API for the leaderboard list [`api-service` Container]

In this section we will read the leaderboard.csv and return it to the API as a list of json objects

### Install pandas
```
pipenv install pandas
```

### Add a new route `/leaderboard`
- Add the following import
```
import pandas as pd
```

- In the `api-service` folder in `api/service.py` add the code for the new route
```
@app.get("/leaderboard")
def leaderboard_fetch():
    # Fetch leaderboard
    df = pd.read_csv("/persistent/experiments/leaderboard.csv")

    df["id"] = df.index
    df = df.fillna('')

    return df.to_dict('records')
```

Here are reading the `leaderboard.csv` using pandas and returning it as json object in the API call

- You can access this new route from the browser at 'http://localhost:9000/leaderboard'

### 🎉 What did we just do? 
* We read some data from a csv file in the persistent folder. 
* Converted the data to list of dictionary objects in **Python** 
* Exposed the results as a REST API using **FastAPI**


Next we will create a simple frontend page ot display the results.

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
            background-color: #A41034;
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

### Update HTML page to display data
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
        rows += "<td class='MuiTableCell-root MuiTableCell-body'>" + item["user"] + "</td>";
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
* We read some data from a csv file in the persistent folder. 
* Converted the data to list of dictionary objects in **Python** 
* Exposed the results as a REST API using **FastAPI**
* Called the API to get the leaderboard data
* Displayed the data in a HTML table

## Create a model serving API [`api-service` Container]

In this section we serve our best model from the leaderboard as an API

### Install Tensorflow Hub / Multipart
- Exit from `uvicorn_server`
- Run `pipenv install tensorflow_hub python-multipart`

### Add file `api/model.py`

`model.py`
```
import os
import json
import numpy as np
import tensorflow as tf
from tensorflow.python.keras import backend as K
from tensorflow.keras.models import Model
import tensorflow_hub as hub


AUTOTUNE = tf.data.experimental.AUTOTUNE
local_experiments_path = "/persistent/experiments"
best_model = None
best_model_id = None
prediction_model = None
data_details = None
image_width = 224
image_height = 224
num_channels = 3


def load_prediction_model():
    print("Loading Model...")
    global prediction_model, data_details

    best_model_path = os.path.join(
        local_experiments_path, best_model["user"], best_model["experiment"], best_model["model_name"]+".hdf5")

    print("best_model_path:", best_model_path)
    prediction_model = tf.keras.models.load_model(
        best_model_path, custom_objects={'KerasLayer': hub.KerasLayer})
    print(prediction_model.summary())

    data_details_path = os.path.join(
        local_experiments_path, best_model["user"], best_model["experiment"], "data_details.json")

    # Load data details
    with open(data_details_path, 'r') as json_file:
        data_details = json.load(json_file)


def check_model_change():
    global best_model, best_model_id
    best_model_json = os.path.join(local_experiments_path, "best_model.json")
    if os.path.exists(best_model_json):
        with open(best_model_json) as json_file:
            best_model = json.load(json_file)

        if best_model_id != best_model["experiment"]:
            load_prediction_model()
            best_model_id = best_model["experiment"]


def load_preprocess_image_from_path(image_path):
    print("Image", image_path)

    image_width = 224
    image_height = 224
    num_channels = 3

    # Prepare the data
    def load_image(path):
        image = tf.io.read_file(path)
        image = tf.image.decode_jpeg(image, channels=num_channels)
        image = tf.image.resize(image, [image_height, image_width])
        return image

    # Normalize pixels
    def normalize(image):
        image = image / 255
        return image

    test_data = tf.data.Dataset.from_tensor_slices(([image_path]))
    test_data = test_data.map(load_image, num_parallel_calls=AUTOTUNE)
    test_data = test_data.map(normalize, num_parallel_calls=AUTOTUNE)
    test_data = test_data.repeat(1).batch(1)

    return test_data


def make_prediction(image_path):
    check_model_change()

    # Load & preprocess
    test_data = load_preprocess_image_from_path(image_path)

    # Make prediction
    prediction = prediction_model.predict(test_data)
    idx = prediction.argmax(axis=1)[0]
    prediction_label = data_details["index2label"][str(idx)]

    if prediction_model.layers[-1].activation.__name__ != 'softmax':
        prediction = tf.nn.softmax(prediction).numpy()
        print(prediction)

    poisonous = False
    if prediction_label == "amanita":
        poisonous = True

    return {
        "input_image_shape": str(test_data.element_spec.shape),
        "prediction_shape": prediction.shape,
        "prediction_label": prediction_label,
        "prediction": prediction.tolist(),
        "accuracy": round(np.max(prediction)*100, 2),
        "poisonous": poisonous
    }

```

### Add two new routes in `service.py`
- Add the following imports to `service.py`
```
import os
from fastapi import File
from tempfile import TemporaryDirectory
from api import model
```

- Add the following routes to `service.py`
```
@app.get("/best_model")
async def get_best_model():
    model.check_model_change()
    if model.best_model is None:
        return {"message": 'No model available to serve'}
    else:
        return {
            "message": 'Current model being served:'+model.best_model["model_name"],
            "model_details": model.best_model
        }


@app.post("/predict")
async def predict(
        file: bytes = File(...)
):
    print("predict file:", len(file), type(file))

    # Save the image
    with TemporaryDirectory() as image_dir:
        image_path = os.path.join(image_dir, "test.png")
        with open(image_path, "wb") as output:
            output.write(file)

        # Make prediction
        prediction_results = model.make_prediction(image_path)

    return prediction_results
```

- Go to the page `http://localhost:9000/docs`
- What do you see?
- There should be an automatically generated API documentation for our APIs
- Test `/best_model`
- Test `/predict`

## Create a prediction page [`frontend-simple` Container]

In this section we will build a prediction page that allows upload of an image and view predictions

### Prediction page
- Add a file `predict.html` with the following content
```
<!DOCTYPE html>
<html>

<head>
    <title>🍄 Mushroom Identifier</title>
    <!-- Add reference to Google fonts -->
    <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">
    <!-- Google Material Design Styles -->
    <link href="https://unpkg.com/material-components-web@latest/dist/material-components-web.min.css" rel="stylesheet">
    <script src="https://unpkg.com/material-components-web@latest/dist/material-components-web.min.js"></script>
    <!-- Add javascript package axios for accessing APIs -->
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

        .dropzone {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            margin: 20px;
            border-width: 2px;
            border-radius: 2px;
            border-color: #cccccc;
            border-style: dashed;
            background-color: #fafafa;
            outline: none;
            transition: border .24s ease-in-out;
            cursor: pointer;
            background-image: url("https://storage.googleapis.com/public_colab_images/ai5/mushroom.svg");
            background-repeat: no-repeat;
            background-position: center;
        }

        .prediction {
            font-family: Roboto, sans-serif;
            font-size: 32px;
            font-weight: 900;
        }

        .mushroom_type {
            font-family: Roboto, sans-serif;
            font-size: 32px;
            font-weight: 900;
            color: #de2d26;
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
        <div class="container">
            <div class="mdc-card mdc-card--outlined" style="min-height: 400px;">
                <div class="dropzone" onclick="upload_file()">

                    <input type="file" id="input_file" accept="image/*" capture="camera" name="input_file" on
                        autocomplete="off" tabindex="-1" style="display: none;">
                    <div><img id="input_file_view" style="width:100%;" /></div>
                    <div style="color: #302f2f;">Click to take a picture or upload...</div>
                </div>
                <div style="padding:20px;">
                    <span class="prediction" id="prediction_label"></span>
                    <span class="mushroom_type" id="mushroom_type"></span>
                </div>
            </div>
        </div>
    </div>
    <!-- Content -->
</body>
<!-- Add Javascript -->
<script>
    // API URL
    axios.defaults.baseURL = 'http://localhost:9000/';

    // file input
    var input_file = document.getElementById("input_file");
    var prediction_label = document.getElementById("prediction_label");
    var prediction_accuracy = document.getElementById("prediction_accuracy");
    var mushroom_type = document.getElementById("mushroom_type");
    var input_file_view = document.getElementById('input_file_view');

    function upload_file() {
        // Clear
        prediction_label.innerHTML = "";
        input_file_view.src = null;

        input_file.click();
    }

    function input_file_onchange() {
        // Read the uploaded file and display it
        var file_to_upload = input_file.files[0];
        input_file_view.src = URL.createObjectURL(file_to_upload);
        prediction_label.innerHTML = "";

        // Post the image to the /predict API
        var formData = new FormData();
        formData.append("file", input_file.files[0]);
        axios.post('/predict', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        }).then(function (response) {
            var prediction_results = response.data;
            console.log(prediction_results);

            // Display the results
            prediction_label.innerHTML = prediction_results["prediction_label"] + " (" + prediction_results["accuracy"] + "%)";
            if (prediction_results["poisonous"]) {
                mushroom_type.innerHTML = "&nbsp;&nbsp;Poisonous";
            } else {
                mushroom_type.innerHTML = "";
            }

        });
    }

    // Attach an onchange event
    input_file.onchange = input_file_onchange;
</script>

</html>
```

- Go to the page `http://localhost:8080/predict.html`
- What do you see?
- Upload an image of a mushroom and see if you get results


## Frontend App using React

### Download the folder `frontent-react`
- From the [repo](https://github.com/dlops-io/mushroom-app/tree/05-apis-frontend)
- Download and unzip `frontent-react` inside your `mushroom-app` folder 
- cd into `frontent-react`
- Run `sh docker-shell.sh` or `docker-shell.bat` 
- Wait for docker shell to start up
- Run `yarn install`, This will ensure all your node packages for React are installed
- Run `yarn start` to start your React App

- Go to the page `http://localhost:3000`
- What do you see?
- Test out the prediction page (Home)
- Test the leaderboard page
- Test the current model page


## 🎉 Congratulations 🎉
Now we have completed:
* Reading data from a csv file in the persistent folder. 
* Converted the data to list of dictionary objects in **Python** 
* Exposed the results as a REST API using **FastAPI**
* Called the API to get the leaderboard data
* Displayed the data in a HTML table
* Exposed our best model as a API, **Model serving**
* Build a predict page for users to upload an image and view predictions
* Rebuilt all the HTML/Javascript into a frontend framework **React**