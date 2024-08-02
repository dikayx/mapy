import logging
import os
import sys

from flask import Flask
from flask_wtf.csrf import CSRFProtect

from mapy import routes
from mapy.cleanup import schedule_tempfile_cleanup
from mapy.context_processors import register_context_processors


def create_app():
    """
    Create application factory, as explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/.
    """
    app = Flask(__name__)
    app.secret_key = os.urandom(24)

    csrf = CSRFProtect(app)

    register_blueprints(app)

    register_context_processors(app)

    configure_logger(app)

    schedule_tempfile_cleanup()

    return app


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(routes.blueprint)


def configure_logger(app):
    """Configure loggers."""
    handler = logging.StreamHandler(sys.stdout)
    if not app.logger.handlers:
        app.logger.addHandler(handler)
