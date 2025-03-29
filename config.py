import os
from sqlalchemy import create_engine

import urllib

class Config:
    SECRET_KEY = "1234567890"
    SESSION_COOKIE_SECURE = False

class DevelopmentConfig(Config):  
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:sergio@localhost:3306/CookieKing'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

config = {
    'development': DevelopmentConfig
}