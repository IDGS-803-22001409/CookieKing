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

    MAIL_SERVER = 'smtp.gmail.com'  # Cambia por tu servidor SMTP
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'cortezgonzalezjuandiego3@gmail.com'
    MAIL_PASSWORD = 'lqog yyak mslx shtt '
    MAIL_DEFAULT_SENDER = 'cortezgonzalezjuandiego3@gmail.com'

config = {
    'development': DevelopmentConfig
}