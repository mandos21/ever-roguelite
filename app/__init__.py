from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from mongoengine import connect
from config.settings import settings

from app.controllers.auth_controller import auth_bp
from app.controllers.user_controller import user_bp
from app.controllers.room_controller import room_bp
from app.controllers.roll_controller import roll_bp
from app.controllers.encounter_controller import encounter_bp
from app.controllers.rolltable_controller import rolltable_bp
from app.controllers.item_controller import item_bp
from app.utils.json_provider import CustomJSONProvider

socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config.from_object(settings)
    app.json = CustomJSONProvider(app)
    
    socketio.init_app(app)


    connect(host=settings.MONGO_URI, uuidRepresentation='standard')
    
    app.register_blueprint(auth_bp, url_prefix='/auth') 
    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(rolltable_bp, url_prefix='/rolltables')
    app.register_blueprint(room_bp, url_prefix='/rooms')
    app.register_blueprint(encounter_bp, url_prefix='/encounters')
    app.register_blueprint(roll_bp, url_prefix='/rolls')
    app.register_blueprint(item_bp, url_prefix='/items')

    return app


app = create_app()
