import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-12345'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///oscm.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
