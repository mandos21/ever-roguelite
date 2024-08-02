from flask import Flask
from mongoengine import connect
from config.settings import settings


def create_app():
    app = Flask(__name__)
    app.config.from_object(settings)


    connect(host=settings.MONGO_URI)

    
    @app.route('/status')
    def status():
        return {'status': 'alive'}, 200


    return app
