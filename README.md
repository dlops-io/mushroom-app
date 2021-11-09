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

### Create folders and give permissions
* `sudo mkdir persistent-folder`
* `sudo mkdir secrets`
* `sudo mkdir -p conf/nginx`
* `sudo chmod 0777 persistent-folder`
* `sudo chmod 0777 secrets`
* `sudo chmod -R 0777 conf`

```
sudo mkdir persistent-folder
sudo mkdir secrets
sudo mkdir -p conf/nginx
sudo chmod 0777 persistent-folder
sudo chmod 0777 secrets
sudo chmod -R 0777 conf
```

### Add secrets file
* Create a file `bucket-reader.json` inside `secrets` folder with the secrets json provided
* You can create a file using the echo command:
```
echo '<___Provided Json Key___>' > secrets/bucket-reader.json
```


### Create Docker network
```
sudo docker network create mushroom-app
```

### Run api-service
Run the container using the following command
```
sudo docker run -d --name api-service \
--mount type=bind,source="$(pwd)/persistent-folder/",target=/persistent \
--mount type=bind,source="$(pwd)/secrets/",target=/secrets \
-p 9000:9000 \
-e GOOGLE_APPLICATION_CREDENTIALS=/secrets/bucket-reader.json \
-e GCP_PROJECT=ac215-project \
-e GCP_ZONE=us-central1-a --network mushroom-app dlops/mushroom-app-api-service
```

If you want to run in interactive mode like we id in development:
```
sudo docker run --rm -ti --name api-service --mount type=bind,source="$(pwd)/persistent-folder/",target=/persistent --mount type=bind,source="$(pwd)/secrets/",target=/secrets -p 9000:9000 -e GOOGLE_APPLICATION_CREDENTIALS=/secrets/bucket-reader.json -e GCP_PROJECT=ac215-project -e GCP_ZONE=us-central1-a -e DEV=1 --network mushroom-app dlops/mushroom-app-api-service
```

### Run frontend
Run the container using the following command
```
sudo docker run -d --name frontend -p 3000:80 --network mushroom-app dlops/mushroom-app-frontend
```

### Add NGINX config file
* Download file `nginx.conf`
```
echo 'user  nginx;
error_log  /var/log/nginx/error.log warn;
pid        /var/run/nginx.pid;
events {
    worker_connections  1024;
}
http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';
    access_log  /var/log/nginx/access.log  main;
    sendfile        on;
    tcp_nopush     on;
    keepalive_timeout  65;
	types_hash_max_size 2048;
	server_tokens off;
    gzip  on;
	gzip_disable "msie6";

	ssl_protocols TLSv1 TLSv1.1 TLSv1.2; # Dropping SSLv3, ref: POODLE
    ssl_prefer_server_ciphers on;

	server {
		listen 80;

		server_name localhost;

		error_page   500 502 503 504  /50x.html;
		location = /50x.html {
			root   /usr/share/nginx/html;
		}
		# API
		location /api {
			rewrite ^/api/(.*)$ /$1 break;
			proxy_pass http://api-service:9000;
			proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
			proxy_set_header X-Forwarded-Proto $scheme;
			proxy_set_header X-Real-IP $remote_addr;
			proxy_set_header Host $http_host;
			proxy_redirect off;
			proxy_buffering off;
		}

		# Frontend
		location / {
			rewrite ^/(.*)$ /$1 break;
			proxy_pass http://frontend;
			proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
			proxy_set_header X-Forwarded-Proto $scheme;
			proxy_set_header X-Real-IP $remote_addr;
			proxy_set_header Host $http_host;
			proxy_redirect off;
			proxy_buffering off;
		}
	}
}
' > conf/nginx/nginx.conf
```

### Run NGINX Web Server
Run the container using the following command
```
sudo docker run -d --name nginx -v $(pwd)/conf/nginx/nginx.conf:/etc/nginx/nginx.conf -p 80:80 --network mushroom-app nginx:stable
```

You can access the deployed API using `http://<Your VM IP Address>/`
