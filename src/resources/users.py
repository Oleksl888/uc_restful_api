from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, DatabaseError
from src.resources.authentication import send_mail, admin_required
from src import db
from src.models import User
from src.resources.iptracker import add_tracker
from src.schemas import UserSchema


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


class UsersApi(Resource):
    user_schema = UserSchema()
    @add_tracker
    @admin_required
    def get(self, uuid=None):
        if uuid is None:
            users = db.session.query(User).all()
            users_data = self.user_schema.dump(users, many=True)
            return users_data, 200
        user = db.session.query(User).filter_by(uuid=uuid).first()
        if not user:
            return {'message': 'User not found'}, 404
        user_data = self.user_schema.dump(user)
        return user_data, 200

    @admin_required
    def post(self):
        data = request.json
        try:
            normalize_data(data)
            user = self.user_schema.load(data, session=db.session)
        except (ValidationError, TypeError):
            return {'message': '''Incorrect data entered:\n
                                  Name must be only alphabetic characters.\n
                                  Must be valid email address.\n
                                  Password must contain at least 8 symbols\n'''}, 400
        except (KeyError, TypeError, ValueError, AttributeError, DatabaseError):
            print('Wrong data. Database error, cleaning up remaining files...')
            db.session.rollback()
            db.session.close()
        else:
            try:
                db.session.add(user)
                db.session.commit()
            except IntegrityError:
                return {'message': 'The user already exists'}, 409
            email = data.get('email', '')
            name = data.get('name', '')
            send_mail(name, email)
            return {'message': 'User has been added'}, 201

    @admin_required
    def put(self, uuid=None):
        data = request.json
        if uuid is None:
            return {'message': 'Must specify user uuid in the url to make changes'}, 404
        user = db.session.query(User).filter_by(uuid=uuid).first()
        if user:
            try:
                normalize_data(data)
                user = self.user_schema.load(data, instance=user, session=db.session)
            except (ValidationError, TypeError):
                return {'message': '''Incorrect data entered:\n
                                      Name must be only alphabetic characters.\n
                                      Must be valid email address.\n
                                      Password must contain at least 8 symbols\n'''}, 400
            except (KeyError, TypeError, ValueError, AttributeError, DatabaseError):
                print('Wrong data. Database error, cleaning up remaining files...')
                db.session.rollback()
                db.session.close()
            else:
                try:
                    db.session.add(user)
                    db.session.commit()
                except IntegrityError:
                    return {'message': 'The user already exists'}, 409
                return {'message': 'User has been updated'}, 201
        else:
            return {'message': 'The user does not yet exist'}, 404

    @admin_required
    def patch(self, uuid=None):
        data = request.json
        if uuid is None:
            return {'message': 'Must specify user uuid in the url to make changes'}, 404
        user = db.session.query(User).filter_by(uuid=uuid).first()
        if user:
            try:  # Validating and normalizing data - made separate for patch method
                if data.get('name') and not data.get('name').isalpha():
                    raise ValidationError
                if data.get('password') and len(data.get('password')) < 8:
                    raise ValidationError
                for key, val in data.items():
                    if not key == 'password':
                        data[key] = val.lower()
                user = self.user_schema.load(data, instance=user, session=db.session, partial=True)
            except (ValidationError, TypeError):
                return {'message': '''Incorrect data entered:\n
                                          Name must be only alphabetic characters.\n
                                          Must be valid email address.\n
                                          Password must contain at least 8 symbols\n'''}, 400
            except (KeyError, TypeError, ValueError, AttributeError, DatabaseError):
                print('Wrong data. Database error, cleaning up remaining files...')
                db.session.rollback()
                db.session.close()
            else:
                try:
                    db.session.add(user)
                    db.session.commit()
                except IntegrityError:
                    return {'message': 'The user already exists'}, 409
                return {'message': 'User has been updated'}, 201
        else:
            return {'message': 'The user does not yet exist'}, 404

    @admin_required
    def delete(self, uuid=None):
        if uuid is None:
            return {'message': 'Must specify user id in the url to delete'}, 404
        user = db.session.query(User).filter_by(uuid=uuid).first()
        if not user:
            return {'message': 'The user does not yet exist'}, 404
        db.session.delete(user)
        db.session.commit()
        return {'message': 'The user has been deleted'}, 204
