import logging

from flask import Flask, jsonify
from flask_socketio import SocketIO
from mongoengine import connect

from app.controllers.auth_controller import auth_bp
from app.controllers.encounter_controller import encounter_bp
from app.controllers.item_controller import item_bp
from app.controllers.roll_controller import roll_bp
from app.controllers.rolltable_controller import rolltable_bp
from app.controllers.room_controller import room_bp
from app.controllers.user_controller import user_bp
from app.utils.json_provider import CustomJSONProvider
from config.settings import settings

socketio = SocketIO()
logging.basicConfig(level=logging.INFO)


def create_app():
    flask_app = Flask(__name__)
    flask_app.config.from_object(settings)
    flask_app.json = CustomJSONProvider(flask_app)

    socketio.init_app(flask_app)

    connect(host=settings.MONGO_URI, uuidRepresentation='standard')

    flask_app.register_blueprint(auth_bp, url_prefix='/auth')
    flask_app.register_blueprint(user_bp, url_prefix='/users')
    flask_app.register_blueprint(rolltable_bp, url_prefix='/rolltables')
    flask_app.register_blueprint(room_bp, url_prefix='/rooms')
    flask_app.register_blueprint(encounter_bp, url_prefix='/encounters')
    flask_app.register_blueprint(roll_bp, url_prefix='/rolls')
    flask_app.register_blueprint(item_bp, url_prefix='/items')

    @flask_app.errorhandler(Exception)
    def handle_exception(e):
        logging.error(f"An error occurred: {e}")
        response = {
            "error": "Internal Server Error",
            "message": str(e)
        }
        return jsonify(response), 500

    return flask_app


app = create_app()
