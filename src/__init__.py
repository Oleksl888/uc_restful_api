from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from config import Config
from flask_migrate import Migrate
from flask_mail import Mail
from flask_swagger_ui import get_swaggerui_blueprint


app = Flask(__name__)  # Create flask app
app.config.from_object(Config)  # Import config
api = Api(app)  # Create api object
db = SQLAlchemy(app)  # Create database
migrate = Migrate(app, db)  # Set up for database migrations (it's like VCS for database)
ma = Marshmallow(app)  # Set up for database schemas
mail = Mail(app)  # Set up for sending emails from application


# Set up for Swagger UI
SWAGGER_URL = '/swagger'
API_URL = '/static/openapi.yaml'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
            'app_name': 'Ultimate CookBook UI',
            'validatorUrl': None
        }
)

app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)


# Importing routes and models to avoid circular import exception
from src import routes, models
