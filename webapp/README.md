# Running the Web App

We use gunicorn to serve the flask web app. The list of dependencies for the web app is in `webapp/requirements.txt`. After cloning, use `pip install -r requirements.txt` in the `webapp/` directory to install these dependencies.

## Configuration

There are a couple security measures to protect our database and cookie storage server.

### Redis

We use redis to store cookies so we have login and authentication features. For the app to connect to the redis server properly, you need to add the server address and our redis secret key to your environment variables. I've put the secret key inside `/home/ychen/secrets/secret_key.txt` on `blpc0`. Set environment variable `SECRET_KEY` to the file's contents.

e.g.:
```bash
export SECRET_KEY=$(ssh blpc0 "cat /home/ychen/secrets/secret_key.txt")
```

The IP is somewhat more complex. the redis server is configured so that only GCP internal machines can access it. I set up a ssh forwarding server so you can access it on an outside machine. The port forwarding command is shown below:

```bash
gcloud beta compute ssh --zone "us-central1-a" "bl-scale-redis-forwarder" --project "breakthrough-listen-sandbox" -- -N -L 6379:10.191.222.19:6379
```

You will need to have done `gcloud auth login` to run this successfully.
After that, set environment variable `SESSION_REDIS` to `redis://127.0.0.1:6379` by running:

```bash
export SESSION_REDIS=redis://127.0.0.1:6379
```

After that, your redis connection will be set up and cookies will be working when you run on local.

### Firebase

Our firebase database is only accessible with our unique API key and a specific GCP service account key. The two keys are also stored inside `/home/ychen/secrets/` on `blpc0` as `firebase-apiKey.txt` and `bl_scale_key.json`.

For the API key, you should set environment variable `FIREBASE_API_KEY` to its contents, e.g:

```bash
export FIREBASE_API_KEY=$(ssh blpc0 "cat /home/ychen/secrets/firebase-apiKey.txt")
```

For the service account key, you will need to download it to a secure location on your machine, and set environment variable `GOOGLE_APPLICATION_CREDENTIALS` to the key's **path**. For example, download it to `/secrets`, and set `GOOGLE_APPLICATION_CREDENTIALS` to `/secrets/bl_scale_key.json`. e.g.:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/secrets/bl_scale_key.json
```

## Running with gunicorn

After configuring the related environment variables, you can run the app with:

```bash
gunicorn3 -b :5000 --log-level=debug "main:config_app()"
```
