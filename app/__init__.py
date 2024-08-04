from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from mongoengine import connect
from config.settings import settings

from app.controllers.auth_controller import auth_bp
from app.controllers.user_controller import user_bp

socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config.from_object(settings)
    
    socketio.init_app(app)


    connect(host=settings.MONGO_URI)
    
    app.register_blueprint(auth_bp, url_prefix='/auth') 
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(rolltable_bp, url_prefix='/rolltable')
    app.register_blueprint(rooms_bp, url_prefix='/room')
    app.register_blueprint(encounters_bp, url_prefix='/encounter')
    app.register_blueprint(rolls_bp, url_prefix='/roll')

    return app
