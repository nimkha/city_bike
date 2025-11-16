from flask import Flask
from flasgger import Swagger
import logging


def configure_logging():
    """Using logging module to decouple logging from Flask app"""

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    """This is to avoid duplicates on reload in dev server"""
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def create_app():
    """
    Build and configure the Flask application.
    """
    app = Flask(__name__)
    logger = configure_logging()
    app.logger.handlers = logger.handlers
    app.logger.setLevel(logger.level)
    Swagger(app, template={
        "info": {
            "title": "City Bikes",
            "description": "REST API for City Bike information.",
            "version": "1.0.0"
        }
    })

    """Import the routes after the app object exists so they register on it. """
    from .api import api_bp
    app.register_blueprint(api_bp)

    return app
