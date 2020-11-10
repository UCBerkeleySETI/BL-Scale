echo "Authenticating GCloud"
ls /var/run/secret/cloud.google.com/
gcloud auth activate-service-account --key-file=/var/run/secret/cloud.google.com/bl-scale_key.json
gcloud container clusters get-credentials bl-scale-cluster --zone us-central1-c --project breakthrough-listen-sandbox
echo "Auth Finished, Starting Server"
python3 server/monitor.py
