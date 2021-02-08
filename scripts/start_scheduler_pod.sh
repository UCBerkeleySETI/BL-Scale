gcloud auth activate-service-account --key-file=/var/run/secret/cloud.google.com/bl-scale_key.json
gcloud container clusters get-credentials bl-scale-cluster --zone us-central1-c --project breakthrough-listen-sandbox
python3 server/scheduler.py
