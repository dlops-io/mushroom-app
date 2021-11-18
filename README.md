# Deploy Mushroom App to K8s Cluster

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

## Build and Push Docker Containers to GCR
**This step is only required if you have NOT already done this**
```
ansible-playbook deploy-docker-images.yml -i inventory.yml
```

# Deploy to Kubernetes Cluster
We will use ansible to create and deploy the mushroom app into a Kubernetes Cluster

### Create a Deployment Yaml file (Ansible Playbook)
* Add a file called `deploy-k8s-cluster.yml` inside the deployment folder
* Add the following script:
```
---
- name: "Create Kubernetes Cluster and deploy multiple containers"
  hosts: localhost
  gather_facts: false

  vars:
    cluster_name: "mushroom-app-cluster"
    machine_type: "n1-standard-1"
    machine_disk_size: 30
    initial_node_count: 2

  tasks:
  - name: "Create a GKE cluster"
    google.cloud.gcp_container_cluster:
      name: "{{cluster_name}}"
      initial_node_count: "{{ initial_node_count }}"
      location: "{{ gcp_zone }}"
      project: "{{ gcp_project }}"
      release_channel:
        channel: "UNSPECIFIED"
      ip_allocation_policy:
        use_ip_aliases: "yes"
      auth_kind: "{{ gcp_auth_kind }}"
      service_account_file: "{{ gcp_service_account_file }}"
      state: "{{ cluster_state }}"
    register: cluster
  
  - name: "Create a Node Pool"
    google.cloud.gcp_container_node_pool:
      name: default-pool
      initial_node_count: "{{ initial_node_count }}"
      cluster: "{{ cluster }}"
      location: "{{ gcp_zone }}"
      project: "{{ gcp_project }}"
      config:
        machine_type: "{{ machine_type }}"
        image_type: "COS"
        disk_size_gb: "{{ machine_disk_size }}"
        oauth_scopes:
          - "https://www.googleapis.com/auth/devstorage.read_only"
          - "https://www.googleapis.com/auth/logging.write"
          - "https://www.googleapis.com/auth/monitoring"
          - "https://www.googleapis.com/auth/servicecontrol"
          - "https://www.googleapis.com/auth/service.management.readonly"
          - "https://www.googleapis.com/auth/trace.append"
      autoscaling:
        enabled: "yes"
        min_node_count: "1"
        max_node_count: "{{ initial_node_count }}"
      management:
        auto_repair: "yes"
        auto_upgrade: "yes"
      auth_kind: "{{ gcp_auth_kind }}"
      service_account_file: "{{ gcp_service_account_file }}"
      state: "{{ cluster_state }}"
  
  - name: "Connect to cluster (update kubeconfig)"
    shell: "gcloud container clusters get-credentials {{ cluster.name }} --zone {{ gcp_zone }} --project {{ gcp_project }}"
    when: cluster_state == "present"

  - name: "Create Namespace"
    k8s:
      name: "{{cluster_name}}-namespace"
      api_version: v1
      kind: Namespace
      state: present
    when: cluster_state == "present"

  - name: "Add nginx-ingress helm repo"
    community.kubernetes.helm_repository:
      name: nginx-stable
      repo_url: https://helm.nginx.com/stable
    when: cluster_state == "present"

  - name: "Install nginx-ingress"
    community.kubernetes.helm:
      name: nginx-ingress
      namespace: "{{cluster_name}}-namespace"
      chart_ref: nginx-stable/nginx-ingress
      state: present
    when: cluster_state == "present"

  - name: "Copy docker tag file"
    copy:
      src: .docker-tag
      dest: .docker-tag
      mode: 0644
    when: cluster_state == "present"

  - name: "Get docker tag"
    shell: "cat .docker-tag"
    register: tag
    when: cluster_state == "present"

  - name: "Print tag"
    debug:
      var: tag
    when: cluster_state == "present"

  - name: Create secrets directory
    file:
      path: "/srv/secrets"
      state: "directory"
      mode: 0755
    when: cluster_state == "present"
  
  - name: Create persistent directory
    file:
      path: "/srv/persistent"
      state: "directory"
      mode: 0777
    when: cluster_state == "present"

  - name: Copy bucket reader key file
    copy:
      src: ../secrets/bucket-reader.json
      dest: "/srv/secrets/bucket-reader.json"
      mode: 0644
    when: cluster_state == "present"

  - name: "Create Persistent Volume Claim"
    k8s:
      state: present
      definition:
        apiVersion: v1
        kind: PersistentVolumeClaim
        metadata:
          name: persistent-pvc
          namespace: "{{cluster_name}}-namespace"
        spec:
          accessModes:
            - ReadWriteOnce
          resources:
            requests:
              storage: 5Gi
    when: cluster_state == "present"
  
  - name: Importing credentials as a Secret
    shell: |
      #!/bin/bash
      kubectl create secret generic bucket-reader-key --from-file=bucket-reader.json=../secrets/bucket-reader.json --namespace="{{cluster_name}}-namespace"
    when: cluster_state == "present"
  
  - name: "Create Deployment for Frontend"
    k8s:
      state: present
      definition:
        apiVersion: v1
        kind: Deployment
        metadata:
          name: frontend
          namespace: "{{cluster_name}}-namespace"
        spec:
          selector:
            matchLabels:
              run: frontend
          template:
            metadata:
              labels:
                run: frontend
            spec:
              containers:
              - image: "gcr.io/{{ gcp_project }}/mushroom-app-frontend-react:{{ tag.stdout}}"
                imagePullPolicy: IfNotPresent
                name: frontend
                ports:
                - containerPort: 80
                  protocol: TCP
    when: cluster_state == "present"

  - name: "Create Deployment for API Service"
    k8s:
      state: present
      definition:
        apiVersion: v1
        kind: Deployment
        metadata:
          name: api
          namespace: "{{cluster_name}}-namespace"
        spec:
          selector:
            matchLabels:
              run: api
          template:
            metadata:
              labels:
                run: api
            spec:
              volumes:
                - name: persistent-vol
                  emptyDir: {}
                  # persistentVolumeClaim:
                  #   claimName: persistent-pvc
                - name: google-cloud-key
                  secret:
                    secretName: bucket-reader-key
              containers:
              - image: gcr.io/{{ gcp_project }}/mushroom-app-api-service:{{ tag.stdout}}
                imagePullPolicy: IfNotPresent
                name: api
                ports:
                - containerPort: 9000
                  protocol: TCP
                volumeMounts:
                  - name: persistent-vol
                    mountPath: /persistent
                    #readOnly: false
                  - name: google-cloud-key
                    mountPath: /secrets
                env:
                  - name: GOOGLE_APPLICATION_CREDENTIALS
                    value: /secrets/bucket-reader.json
                  - name: GCP_PROJECT
                    value: ac215-project
                  - name: GCP_ZONE
                    value: us-central1-a
    when: cluster_state == "present"

  - name: "Create Service for Frontend"
    k8s:
      state: present
      definition:
        apiVersion: v1
        kind: Service
        metadata:
          name: frontend
          namespace: "{{cluster_name}}-namespace"
        spec:
          ports:
          - port: 80
            protocol: TCP
            targetPort: 80
          selector:
            run: frontend
          type: NodePort
    when: cluster_state == "present"

  - name: "Create Service for API Service"
    k8s:
      state: present
      definition:
        apiVersion: v1
        kind: Service
        metadata:
          name: api
          namespace: "{{cluster_name}}-namespace"
        spec:
          ports:
          - port: 9000
            protocol: TCP
            targetPort: 9000
          selector:
            run: api
          type: NodePort
    when: cluster_state == "present"

  - name: Wait for Ingress Nginx to get ready
    shell: |
      #!/bin/bash
      kubectl get service nginx-ingress-nginx-ingress --namespace="{{cluster_name}}-namespace" -ojson | jq -r '.status.loadBalancer.ingress[].ip'
    register: nginx_ingress
    delay: 10
    retries: 20
    until: nginx_ingress.stderr == ""
    when: cluster_state == "present"

  - name: Set Nginx Ingress IP
    set_fact:
      nginx_ingress_ip: "{{nginx_ingress.stdout}}"
    when: cluster_state == "present"

  - name: Debug Ingress Nginx IP Address
    debug:
      msg: "Ingress Nginx IP Address: {{ nginx_ingress_ip }}"
    when: cluster_state == "present"

  - name: Debug vars
    debug:
      var: nginx_ingress_ip
      verbosity: 0
    when: cluster_state == "present"

  - name: "Create Ingress Controller"
    k8s:
      state: present
      definition:
        apiVersion: networking.k8s.io/v1
        kind: Ingress
        metadata:
          name: ingress-resource
          namespace: "{{cluster_name}}-namespace"
          annotations:
            kubernetes.io/ingress.class: "nginx"
            nginx.ingress.kubernetes.io/ssl-redirect: "false"
            nginx.org/rewrites: "serviceName=frontend rewrite=/;serviceName=api rewrite=/"
        spec:
          rules:
          - host: "{{ nginx_ingress_ip }}.sslip.io" # Host requires a domain and not just an IP
            http:
              paths:
              - path: /
                pathType: Prefix
                backend:
                  service:
                    name: frontend
                    port:
                      number: 80
              - path: /api/
                pathType: Prefix
                backend:
                  service:
                    name: api
                    port:
                      number: 9000
    when: cluster_state == "present"
```

### Create & Deploy Cluster
```
ansible-playbook deploy-k8s-cluster.yml -i inventory.yml --extra-vars cluster_state=present
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

### If you want to shell into a container in a Pod
```
kubectl get pods --namespace=mushroom-app-cluster-namespace
kubectl get pod api-5d4878c545-47754 --namespace=mushroom-app-cluster-namespace
kubectl exec --stdin --tty api-5d4878c545-47754 --namespace=mushroom-app-cluster-namespace  -- /bin/bash
```

### View the App
* Copy the `nginx_ingress_ip` from the terminal from the create cluster command
* Go to `http://<YOUR INGRESS IP>.sslip.io`

### Delete Cluster
```
ansible-playbook deploy-k8s-cluster.yml -i inventory.yml --extra-vars cluster_state=absent
```