from flask import Flask
from flask_session import Session
from flask import session


sess = Session()

app = Flask(__name__, instance_relative_config=False)
app.config.from_object('config.Config')

def config_app():

    sess.init_app(app)

    with app.app_context():
        return app

@app.route('/')
def index():
    if "count" in session:
        session["count"]+=1
    else:
        session["count"]=1
    return str(session["count"])
