import logging

from flask import Flask, jsonify
from flask_socketio import SocketIO
from mongoengine import connect
from werkzeug.exceptions import HTTPException

from app.utils.json_provider import CustomJSONProvider
from app.views.auth import auth_bp
from app.views.encounter import encounter_bp
from app.views.item import item_bp
from app.views.roll import roll_bp
from app.views.rolltable import rolltable_bp
from app.views.room import room_bp
from app.views.session import session_bp
from app.views.user import user_bp
from config.settings import settings

socketio = SocketIO()
logging.basicConfig(level=logging.INFO)


def create_app():
    from app.views import socket

    flask_app = Flask(__name__)
    flask_app.config.from_object(settings)
    flask_app.json = CustomJSONProvider(flask_app)

    socketio.init_app(flask_app)

    connect(host=settings.MONGO_URI, uuidRepresentation="standard")

    flask_app.register_blueprint(session_bp, url_prefix="/session")

    flask_app.register_blueprint(auth_bp, url_prefix="/auth")
    flask_app.register_blueprint(user_bp, url_prefix="/users")
    flask_app.register_blueprint(rolltable_bp, url_prefix="/rolltables")
    flask_app.register_blueprint(room_bp, url_prefix="/rooms")
    flask_app.register_blueprint(encounter_bp, url_prefix="/encounters")
    flask_app.register_blueprint(roll_bp, url_prefix="/rolls")
    flask_app.register_blueprint(item_bp, url_prefix="/items")

    @flask_app.errorhandler(HTTPException)
    def handle_http_exception(e):
        logging.warning(f"HTTP error occurred: {e}")
        response = {"error": e.name, "message": e.description}
        return jsonify(response), e.code

    @flask_app.errorhandler(Exception)
    def handle_exception(e):
        logging.error(f"An error occurred: {e}")
        response = {"error": "Internal Server Error", "message": str(e)}
        return jsonify(response), 500

    @flask_app.errorhandler(404)
    def handle_404_error(e):
        response = {
            "error": "Not Found",
            "message": "The requested resource could not be found",
        }
        return jsonify(response), 404

    @flask_app.errorhandler(400)
    def handle_400_error(e):
        response = {
            "error": "Bad Request",
            "message": "The request could not be understood or was missing required parameters",
        }
        return jsonify(response), 400

    return flask_app


app = create_app()
