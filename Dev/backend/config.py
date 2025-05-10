import os
from datetime import timedelta

class Config:
    # Configuración básica
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-123'
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # Configuración de correo
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Configuración de CORS
    CORS_HEADERS = 'Content-Type'
    
    # Configuración de la base de datos (archivos JSON)
    USERS_FILE = 'users.json'
    FORUM_FILE = 'forum.json'
    
    # Configuración de la aplicación
    SECRET_KEY = 'tu_clave_secreta_muy_segura'  # Cambiar en producción
    
    # Configuración de correo electrónico
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'ejemplo@gmail.com'
    MAIL_PASSWORD = 'ejemplo123'
    MAIL_DEFAULT_SENDER = 'ejemplo@gmail.com'
    MAIL_USE_SSL = False
    MAIL_ASCII_ATTACHMENTS = False
    MAIL_DEFAULT_CHARSET = 'utf-8'
    
    # Configuración de sesión para desarrollo local
    SESSION_COOKIE_SECURE = False  # True solo en producción con HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'None'  # Permitir cookies cross-origin para desarrollo 