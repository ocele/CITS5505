# config.py
import os
from dotenv import load_dotenv

# getting the base directory of the project
basedir = os.path.abspath(os.path.dirname(__file__))
# loading environment variables from .env file
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # getting the secret key from environment variables
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # getting the database URI from environment variables
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
