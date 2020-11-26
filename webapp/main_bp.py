import monitor
import results
import trigger
from main import app
from main import config_app

app.register_blueprint(monitor.bp)
app.register_blueprint(results.bp)
app.register_blueprint(trigger.bp)

if __name__ == '__main__':
    app = config_app()
    app.run()