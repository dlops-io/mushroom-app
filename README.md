# Create Kubernetes Cluster Tutorial

## API's to enable in GCP for Project
We have already done this in the deployment tutorial but in case you have not done that step. Search for each of these in the GCP search bar and click enable to enable these API's
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

### Create a Deployment Yaml file
* Add a file called `deploy-k8s-tic-tac-toe.yml` inside the deployment folder
* Add the following script:
```
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  selector:
    matchLabels:
      run: web
  template:
    metadata:
      labels:
        run: web
    spec:
      containers:
      - image: dlops/tic-tac-toe
        imagePullPolicy: IfNotPresent
        name: web
        ports:
        - containerPort: 8080
          protocol: TCP
---
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  ports:
  - port: 80
    protocol: TCP
    targetPort: 8080
  selector:
    run: web
  type: LoadBalancer
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