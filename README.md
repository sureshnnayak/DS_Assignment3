# DistributedSystems

# Programming Assignment 3
**Goal** : Implement NTP protocol on both server and client

**Contributors**: @SwaminathanSriram @SureshNayak

## Interfaces Implemented
- NTP Client
  - UDP connections are established
  - NTP data format 
- NTP Server

## Current State of the System
- NTP server works   
- NTP Client works

## How to run Server
- Docker
```python
docker compose up
```
- GCP
  - Create Image
  ```python
  gcloud builds submit --tag gcr.io/{Project_ID}/ntp_server
  ```
  - Create Kubernetes Cluster
  - Configure kubectl to access the cluster
  ```python
  gcloud container clusters get-credentials {CLUSTER_NAME} --zone {ZONE} --project {Project_ID}
  ```
  - Deploy kube scripts
  ```
  kubectl apply -f deployment
  ```
  - Configure Firewall
  ```
  gcloud compute firewall-rules create {FIREWALL_NAME} --allow udp:{PORT}
  ```

## How to run client
```python3
NTP_SERVER="localhost" NTP_PORT=1234 python3 ntp_client/ntp_client.py | tee ntp_client/logs/localhost_client.output
```

## How to plot graph
```
SERVER="Local_NTP_Server" python3 ntp_client/plot.py
```

## Where to view logs and graphs ?
- Graphs : ntp_client/graphs
- Output : ntp_client/logs