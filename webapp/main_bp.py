import monitor
import results
import trigger
import logging
from main import app
from main import config_app
from main import listener

app.register_blueprint(monitor.bp)
app.register_blueprint(results.bp)
app.register_blueprint(trigger.bp)

if __name__ == '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    
    app = config_app()
    app.run()
