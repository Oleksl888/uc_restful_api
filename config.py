import os.path

BASEDIR = os.path.abspath(os.path.dirname(__file__))


# In case of Heroku deployment - fixing postgres dialect issue
uri = os.getenv("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)


class Config:
    # Setting database to postgres and if not available using sqlite3
    SQLALCHEMY_DATABASE_URI = uri or 'sqlite:///' + os.path.join(BASEDIR, 'data', 'cook.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')  # Must set username in environment variable
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')  # Must set password in environment variable
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME', '')
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    SECRET_KEY = os.urandom(20).hex()  # Generating random secret key for CSRF encryption and JWT tokens
    MAX_CONTENT_LENGTH = 524288  # Sets a limit for uploaded content in bytes
    UPLOAD_EXTENSIONS = ['.jpg', '.jpeg', '.JPG', '.JPEG', '.png', '.PNG']  # Sets extensions accepted for upload

