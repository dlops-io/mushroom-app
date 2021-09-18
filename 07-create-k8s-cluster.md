# Create Kubernetes Cluster Tutorial

## API's to enable in GCP for Project
Search for each of these in the GCP search bar and click enable to enable these API's
* Compute Engine API
* Service Usage API
* Cloud Resource Manager API
* Google Container Registry API
* Kubernetes Engine API

## Start Deployment Docker Container
-  `cd deployment`
- Run `sh docker-shell.sh` or `docker-shell.bat` for windows
- Check versions of tools
`gcloud --version`
`kubectl version`
`kubectl version --client`

- Check if make sure you are authenticated to GCP
- Run `gcloud auth list`

## Deploy to Kubernetes Cluster

### Create Cluster
```
gcloud container clusters create test-cluster --num-nodes 2 --zone us-east1-c
```

### Try some kubectl commands
```
kubectl get all
kubectl get all --all-namespaces
kubectl get pods --all-namespaces
```

```
kubectl get componentstatuses
kubectl get nodes
```


### Deploy the App
```
kubectl apply -f deploy-k8s-tic-tac-toe.yml
```

### Get the Loadbalancer external IP
```
kubectl get services
```


### Delete Cluster
```
gcloud container clusters delete test-cluster --zone us-east1-c
```