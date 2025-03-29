import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-segura-123')
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.getenv('CSRF_SECRET_KEY', 'csrf-key-segura-456')
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:1234@localhost:3306/CookieKing'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Configuración de email (considera usar variables de entorno)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'cortezgonzalezjuandiego3@gmail.com'
    MAIL_PASSWORD = 'lqog yyak mslx shtt'
    MAIL_DEFAULT_SENDER = 'cortezgonzalezjuandiego3@gmail.com'

config = {
    'development': DevelopmentConfig
}