# BL@Scale

Cloud-based platform for scaling algorithms to process petabytes of Breakthrough Listen data.

## Deployment

`cd` into the repo and run

```
export FLASK_APP=webapp
flask init-db
```

This will set up and initialize the app. After that, running 

```
flask run
```

will deploy the app on your localhost
