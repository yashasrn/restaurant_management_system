import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    )
    
    # Optional: Mail settings
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'