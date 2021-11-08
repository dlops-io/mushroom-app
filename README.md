# Mushroom App - Deployment to GCP (Manual)


In this tutorial we will deploy the Mushroom App to GCP. For this we will create a VM instance in GCP and deploy the following container on the VM:
* api-service
* frontend-react


## Ensure you have all your container build and works locally
### api-service
* Go to `http://localhost:9000/docs` and make sure you can see the API Docs
### frontend-react
* Go to `http://localhost:3000/` and make sure you can see the prediction page

## Push Docker Images to Docker Hub
* Sign up in Docker Hub and create an [Access Token](https://hub.docker.com/settings/security)
* Open a new terminal
* Login to the Hub: `docker login -u <USER NAME> -p <ACCESS TOKEN>`

### Tag & Push api-service
* Tag the Docker Image: `docker tag mushroom-app-api-service <USER NAME>/mushroom-app-api-service`
* Push to Docker Hub: `docker push <USER NAME>/mushroom-app-api-service`

### Build, Tag & Push frontend-react
* Inside the folder`frontend-react` 
* Run `docker build -t mushroom-app-frontend -f Dockerfile .`
* Tag the Docker Image: `docker tag mushroom-app-frontend <USER NAME>/mushroom-app-frontend`
* Push to Docker Hub: `docker push <USER NAME>/mushroom-app-frontend`


## Running Docker Containers on VM

### Install Docker on VM
* Create a VM Instance from [GCP](https://console.cloud.google.com/compute/instances)
* SSH into your newly created instance
Install Docker on the newly created instance by running
* `curl -fsSL https://get.docker.com -o get-docker.sh`
* `sudo sh get-docker.sh`
Check version of installed Docker
* `sudo docker --version`

### Create folder and give permissions
* `sudo mkdir persistent-folder`
* `sudo mkdir secrets`
* `sudo chmod 0755 conf -r`
* `sudo chmod 0777 persistent-folder`
* `sudo chmod 0755 secrets`
* `sudo chmod -R 0755 conf`

### Add secrets file
* Create a file `bucket-reader.json` inside `secrets` folder with the secrets json provided

### Create firewall rules
* Go to `VPC Networks` in GCP and select `Firewall`
* Create a new Firewall rule with the following values:
    - Name: fast-api-rule
    - Target Tags: fast-api-rule
    - Source IP4 range: 0.0.0.0/0
    - Specified protocols and ports: tcp:9000
    - Click Save
* In your VM instance
    - Edit the instance
    - Add the network tags: `fast-api-rule`, `http-server`, `https-server`

### Run api-service
Run the container using the following command
```
sudo docker run -d --name mushroom-app-api-service \
--mount type=bind,source="$(pwd)/persistent-folder/",target=/persistent \
--mount type=bind,source="$(pwd)/secrets/",target=/secrets \
-p 9000:9000 \
-e GOOGLE_APPLICATION_CREDENTIALS=/secrets/bucket-reader.json \
-e GCP_PROJECT=ac215-project \
-e GCP_ZONE=us-central1-a dlops/mushroom-app-api-service
```

If you want to run in interactive mode like we id in development:
```
sudo docker run --rm -ti --name api-service --mount type=bind,source="$(pwd)/persistent-folder/",target=/persistent --mount type=bind,source="$(pwd)/secrets/",target=/secrets -p 9000:9000 -e GOOGLE_APPLICATION_CREDENTIALS=/secrets/bucket-reader.json -e GCP_PROJECT=ac215-project -e GCP_ZONE=us-central1-a -e DEV=1 dlops/mushroom-app-api-service
```

You can access the deployed API using `http://<Your VM IP Address>:9000/docs`

### Run frontend
Run the container using the following command
```
sudo docker run -d --name frontend -p 3000:80 dlops/mushroom-app-frontend
```

You can access the deployed API using `http://<Your VM IP Address>/`

### Add NGINX config file
* Download file `nginx.conf`
```
sudo curl -o conf/nginx/nginx.conf https://github.com/dlops-io/mushroom-app/releases/download/v1.2/nginx.conf
```

### Run NGINX Web Server
Run the app using the following command
```
sudo docker run -d --name nginx -v /conf/nginx/nginx.conf:/etc/nginx/nginx.conf  -p 80:80 nginx:stable
```