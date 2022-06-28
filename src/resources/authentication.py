import datetime
from functools import wraps

import jwt
from flask import request
from flask_restful import Resource
from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash

from src import db, mail, app
from src.models import User
from src.resources.iptracker import add_tracker
from src.schemas import UserSchema
from flask_mail import Message


def normalize_data(data_from_json):
    """
    Checks name string for having alphabetic characters only
    and sets all strings to lower case before adding them to db.
    If required fields are empty Validation Error is raised
    """
    if not data_from_json.get('name') or not data_from_json.get('name').isalpha():
        raise ValidationError
    if not data_from_json.get('email') or not data_from_json.get('password'):
        raise ValidationError
    if len(data_from_json.get('password')) < 8:
        raise ValidationError
    for key, val in data_from_json.items():
        if not key == 'password':
            data_from_json[key] = val.lower()


def send_mail(_name, _email):
    """
    Must configure settings for email service. Config file must contain these mandatory fields:
    MAIL_SERVER
    MAIL_USERNAME
    MAIL_PASSWORD
    MAIL_PORT
    MAIL_USE_TLS
    Username and password must be taken from environment variables for security purposes
    """
    print('Sending mail...')
    message = Message(
        subject='You have been registered',
        recipients=[_email],
        sender=app.config.get('MAIL_USERNAME'),
        body=f'Hello, {_name}! You have been registered.'
    )
    mail.send(message)
    print('Email sent successfully...')


class RegisterApi(Resource):
    """
    Register User endpoint that does not require authentication.
    Basic user priveleges will be set with this endpoint.
    """
    user_schema = UserSchema()

    @add_tracker
    def post(self):
        """
        The normalize_data function will raise validation error if name has incorrect format.
        """
        data = request.json
        try:
            normalize_data(data)
            user = self.user_schema.load(data)
        except (ValidationError, TypeError):
            return {'message': '''Incorrect data entered:\n
                                  Name must be only alphabetic characters.\n
                                  Must be valid email address.\n
                                  Password must contain at least 8 symbols\n'''}, 400
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {'message': 'User exists already'}, 409
        else:
            name = data.get('name')
            email = data.get('email')
            print('about to send mail')
            send_mail(name, email)
            print('email send')
        return {'message': 'User has been created'}, 201


class LoginApi(Resource):
    """
    Upon successful login a jwt token is issued with expiration for 2 hours.
    JWT token contains user id and its authorization level.
    """

    @add_tracker
    def post(self):
        data = request.json
        name = data.get('name', '').lower()
        password = data.get('password', '')
        user = db.session.query(User).filter_by(name=name).first()
        if not user or not check_password_hash(user.password, password):
            return {"message": "Wrong username or password"}, 401
        token = jwt.encode(
            {
                "user_id": user.uuid,
                "is_admin": user.is_admin,
                "exp": datetime.datetime.now() + datetime.timedelta(hours=6)
            }, app.config.get('SECRET_KEY'), algorithm="HS256"
        )
        return {"token": token}, 200


def jwt_protected(func):
    """
    Makes a decorator for endpoints that will require basic user authentication.
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            print(request.headers.get('Authorization'))
            token = request.headers.get('Authorization', None).split()[1]
        except (IndexError, ValueError, KeyError, AttributeError):
            return {"message": "Authentication required"}, 401
        print('this is a token', token)
        try:
            uuid = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")['user_id']
        except (KeyError, ValueError, jwt.ExpiredSignatureError, jwt.InvalidSignatureError):
            return {"message": "Authentication required"}, 401
        user = db.session.query(User).filter_by(uuid=uuid).first()
        if not user:
            return {"message": "Authentication required"}, 401
        else:
            return func(self, *args, **kwargs)

    return wrapper


def admin_required(func):
    """
    Makes a decorator for endpoints that will require admin user authentication.
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            print(request.headers.get('Authorization'))
            token = request.headers.get('Authorization', None).split()[1]
        except (IndexError, ValueError, KeyError, AttributeError):
            return {"message": "Authentication required"}, 401
        print('this is a token', token)
        try:
            token_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
            if token_data['user_id'] and not token_data['is_admin']:
                return {"message": "Not Authorized do make changes"}, 403
            uuid = token_data['user_id']
        except (KeyError, ValueError, jwt.ExpiredSignatureError, jwt.InvalidSignatureError):
            return {"message": "Authentication required"}, 401
        user = db.session.query(User).filter_by(uuid=uuid).first()
        if not user:
            return {"message": "Authentication required"}, 401
        else:
            return func(self, *args, **kwargs)

    return wrapper
