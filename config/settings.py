from dotenv import load_dotenv
import os 

load_dotenv()

class Config:
    MONOG_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/my_dnd_backend')
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')

settings = Config()
