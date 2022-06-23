import os

from flask import request
from flask_restful import Resource
from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash

from src import db, mail
from src.models import User
from src.resources.iptracker import add_tracker
from src.schemas import UserSchema
from flask_mail import Message


def send_mail(_name, _email):
    print('Sending mail...')
    message = Message(
        subject='You have been registered',
        recipients=[_email],
        sender='olesliusarenko@gmail.com',
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
            return "", 401, {"WWW-Authenticate": "Basic realm='Authentication required'"}
        return {"token": "you have been authenticated"}, 200
