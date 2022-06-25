import datetime
import os
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


def send_mail(_name, _email):
    print('Sending mail...')
    message = Message(
        subject='You have been registered',
        recipients=[_email],
        sender=os.environ.get('MAIL_USERNAME'),
        body=f'Hello, {_name}! You have been registered.'
    )
    mail.send(message)
    print('Email sent successfully...')


class RegisterApi(Resource):
    user_schema = UserSchema()

    @add_tracker
    def post(self):
        data = request.json
        email = data.get('email', '')
        name = data.get('name', '')
        for key, val in data.items():
            if not key == 'password':
                data[key] = val.lower()
        try:
            user = self.user_schema.load(data)
        except ValidationError as error:
            return {'message': str(error)}, 400
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {'message': 'User exists already'}, 409
        else:
            print('about to send mail')
            send_mail(name, email)
            print('email send')
        return {'message': 'User has been created'}, 201


class LoginApi(Resource):

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
                "exp": datetime.datetime.now() + datetime.timedelta(hours=2)
            }, app.config.get('SECRET_KEY'), algorithm="HS256"
        )
        return {"token": token}, 200


def jwt_protected(func):
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