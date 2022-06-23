from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, DatabaseError
from src.resources.authentication import send_mail
from src import db
from src.models import User
from src.resources.iptracker import add_tracker
from src.schemas import UserSchema

#must solve case sensitivity issue
class UsersApi(Resource):
    user_schema = UserSchema()

    @add_tracker
    def get(self, _id=None):
        if _id is None:
            users = db.session.query(User).all()
            users_data = self.user_schema.dump(users, many=True)
            return users_data, 200
        user = db.session.query(User).filter_by(id=_id).first()
        if not user:
            return {'message': 'User not found'}, 404
        user_data = self.user_schema.dump(user)
        return user_data, 200

    def post(self):
        data = request.json
        # check if feedback is in the request, create appropriate objects and add them to db
        # or check if there is a session, take a user id from there and update it from feedback route

        email = data.get('email', '')
        name = data.get('name', '')
        try:
            user = self.user_schema.load(data, session=db.session)
        except ValidationError:
            return {'message': 'Incorrect data entered'}, 400
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
            send_mail(name, email)
            return {'message': 'User has been added'}, 201

    def put(self, uuid=None):
        data = request.json
        if uuid is None:
            return {'message': 'Must specify user uuid in the url to make changes'}, 404
        user = db.session.query(User).filter_by(uuid=uuid).first()
        if user:
            try:
                user = self.user_schema.load(data, instance=user, session=db.session)
            except ValidationError:
                return {'message': 'Incorrect data entered'}, 400
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

    def patch(self, uuid=None):
        data = request.json
        if uuid is None:
            return {'message': 'Must specify user uuid in the url to make changes'}, 404
        user = db.session.query(User).filter_by(uuid=uuid).first()
        if user:
            try:
                user = self.user_schema.load(data, instance=user, session=db.session, partial=True)
            except ValidationError:
                return {'message': 'Incorrect data entered'}, 400
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

    def delete(self, uuid=None):
        if uuid is None:
            return {'message': 'Must specify user id in the url to delete'}, 404
        user = db.session.query(User).filter_by(uuid=uuid).first()
        if not user:
            return {'message': 'The user does not yet exist'}, 404
        db.session.delete(user)
        db.session.commit()
        return {'message': 'The user has been deleted'}, 204
