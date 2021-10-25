# Mushroom App - Setup & Code Organization

In this tutorial we will continue to setup the three containers:
* api-service
* data-collector
* frontend-simple

The following container architecture is what we have implemented so far:

![Docker setup for Mushroom App](https://storage.googleapis.com/public_colab_images/docker/docker_containers_mushroom_app2.png)

## Setup Container with GCP Credentials
Next step is to enable `data-collector` and `api-service` container to have access to GCP. We want these two container to connect to GCS as shown:

![Docker setup for Mushroom App](https://storage.googleapis.com/public_colab_images/docker/docker_containers_mushroom_app3.png)

### Setup GCP Service Account
- This step has already been done since we want to connect the "common" model store you all published to in the Mushroom Classification competition. (The credentials file will be provided to you on Ed before this exercise)
- Here are the step to create an account just for reference:
- To setup a service account you will need to go to [GCP Console](https://console.cloud.google.com/home/dashboard), search for  "Service accounts" from the top search box. or go to: "IAM & Admins" > "Service accounts" from the top-left menu and create a new service account called "bucket-reader". For "Service account permissions" select "Cloud Storage" > "Storage Object Viewer". Then click done.
- This will create a service account
- On the right "Actions" column click the vertical ... and select "Create key". A prompt for Create private key for "bucket-reader" will appear select "JSON" and click create. This will download a Private key json file to your computer. Copy this json file into the **secrets** folder.


### Set GCP Credentials
- To setup GCP Credentials in a container we need to set the environment variable `GOOGLE_APPLICATION_CREDENTIALS` inside the container to the path of the secrets file from the previous step
- Update `docker-shell.sh` or `docker-shell.bat` in both `data-collector` and `api-service` to add the new environment variable

`docker-shell.sh`
```
export GCP_PROJECT="ac215-project"
export GCP_ZONE="us-central1-a"
export GOOGLE_APPLICATION_CREDENTIALS=/secrets/bucket-reader.json
```

and add set these environment variables when starting the docker container 

```
-e GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS \
-e GCP_PROJECT=$GCP_PROJECT \
-e GCP_ZONE=$GCP_ZONE \
```

`docker-shell.bat`
```
SET GCP_PROJECT="ac215-project"
SET GCP_ZONE="us-central1-a"
SET GOOGLE_APPLICATION_CREDENTIALS=/secrets/bucket-reader.json
```

and add set these environment variables when starting the docker container 

```
-e GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS ^
-e GCP_PROJECT=$GCP_PROJECT ^
-e GCP_ZONE=$GCP_ZONE ^
```

#### Test Reading from GCS Bucket
* Create a test python script `test_bucket_access.py` inside `data-collector` and add the following content to it:
```
import os
from google.cloud import storage


gcp_project = os.environ["GCP_PROJECT"]
bucket_name = "ac215-mushroom-app-models"
persistent_folder = "/persistent"


def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""

    storage_client = storage.Client(project=gcp_project)

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)


print(gcp_project)

download_file = "test-bucket-access.txt"
download_blob(bucket_name, download_file,
              os.path.join(persistent_folder, download_file))

```

* Run this script with `python test_bucket_access.py` and this should download a `test-bucket-access.txt` file
* Do the same for `api-service` to ensure your container has access to the GCS bucket