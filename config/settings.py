from dotenv import load_dotenv
import os 

load_dotenv()

class Config:
    MONGO_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/my_dnd_backend')
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    SECRET_KEY = os.getenv('SECRET_KET', 'shhh-top-secret')

settings = Config()
