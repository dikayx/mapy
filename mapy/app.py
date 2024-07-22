import logging
import os
import sys

from flask import Flask
from flask_wtf.csrf import CSRFProtect

from mapy import routes


def create_app():
    """
    Create application factory, as explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/.
    """
    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    # app.config.from_object(Config)
    # Config.init_app(app)

    csrf = CSRFProtect(app)

    register_blueprints(app)

    configure_logger(app)

    return app

def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(routes.blueprint)

def configure_logger(app):
    """Configure loggers."""
    handler = logging.StreamHandler(sys.stdout)
    if not app.logger.handlers:
        app.logger.addHandler(handler)