import os.path

BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(BASEDIR, 'data', 'cook.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    SECRET_KEY = os.urandom(20).hex()
    MAX_CONTENT_LENGTH = 524288
    UPLOAD_EXTENSIONS = ['.jpg', '.jpeg', '.JPG', '.JPEG', '.png', '.PNG']
    JWT_SECRET_KEY = os.urandom(20).hex()