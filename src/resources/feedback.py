from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import DatabaseError

from src import db
from src.models import Feedback, User, Recipe
from src.resources.authentication import jwt_protected
from src.resources.iptracker import add_tracker
from src.schemas import FeedbackSchema


class FeedbackApi(Resource):
    feedback_schema = FeedbackSchema()

    @add_tracker
    def get(self):
        #add filter_by unregistered users
        feedback = db.session.query(Feedback).all()
        feedback_data = self.feedback_schema.dump(feedback, many=True)
        return feedback_data, 200

    @add_tracker
    @jwt_protected
    def post(self):
        data = request.json
        # check if theres user_id/name or recipe_id/name in request and update those
        #add regitered user tab
        user_id = data.get('user_uuid', None)
        recipe_id = data.get('recipe_id', None)
        if not user_id and not recipe_id:
            try:
                feedback = self.feedback_schema.load(data, session=db.session)
            except ValidationError:
                return {'message': 'Incorrect data entered'}, 400
            except (KeyError, TypeError, ValueError, AttributeError, DatabaseError):
                print('Wrong data. Database error, cleaning up remaining files...')
                db.session.rollback()
                db.session.close()
            else:
                db.session.add(feedback)
                db.session.commit()
            return {'message': "Feedback has been added"}, 201
        feedback_name = data.get('name', '')
        feedback_msg = data.get('message', '')
        if len(feedback_name) < 1 or len(feedback_msg) < 1:
            return {'message': 'Incorrect data entered: Mandatory fields cannot be empty'}, 400
        feedback = Feedback(feedback_name, feedback_msg)
        if user_id and recipe_id:
            try:
                user = db.session.query(User).filter_by(uuid=user_id).first()
                user.feedback.append(feedback)
                recipe = db.session.query(Recipe).filter_by(id=recipe_id).first()
                recipe.feedback.append(feedback)
                db.session.commit()
            except AttributeError:
                return {'message': "Wrong user or recipe data"}, 201
            return {'message': "Feedback has been added with user and recipe"}, 201
        elif recipe_id:
            recipe = db.session.query(Recipe).filter_by(id=recipe_id).first()
            recipe.feedback.append(feedback)
            db.session.commit()
            return {'message': "Feedback has been added with recipe"}, 201
        elif user_id:
            user = db.session.query(User).filter_by(uuid=user_id).first()
            user.feedback.append(feedback)
            db.session.commit()
            return {'message': "Feedback has been added with user"}, 201

    #put and patch methods will change only message but will not alter message ownership to recipe and user
    @add_tracker
    @jwt_protected
    def put(self, _id=None):
        if _id is None:
            return {'message': 'Must specify id in the url to make changes'}, 404
        data = request.json
        feedback = db.session.query(Feedback).filter_by(id=_id).first()
        if feedback:
            try:
                feedback = self.feedback_schema.load(data, instance=feedback, session=db.session)
            except ValidationError:
                return {'message': 'Incorrect data entered'}, 400
            except (KeyError, TypeError, ValueError, AttributeError, DatabaseError):
                print('Wrong data. Database error, cleaning up remaining files...')
                db.session.rollback()
                db.session.close()
            else:
                db.session.add(feedback)
                db.session.commit()
            return {'message': "Feedback has been Updated"}, 201
        else:
            return {'message': 'The feedback entry does not yet exist'}, 404

    @add_tracker
    @jwt_protected

    def patch(self, _id=None):
        if _id is None:
            return {'message': 'Must specify id in the url to make changes'}, 404
        data = request.json
        feedback = db.session.query(Feedback).filter_by(id=_id).first()
        if feedback:
            try:
                feedback = self.feedback_schema.load(data, instance=feedback, session=db.session, partial=True)
            except ValidationError:
                return {'message': 'Incorrect data entered'}, 400
            except (KeyError, TypeError, ValueError, AttributeError, DatabaseError):
                print('Wrong data. Database error, cleaning up remaining files...')
                db.session.rollback()
                db.session.close()
            else:
                db.session.add(feedback)
                db.session.commit()
            return {'message': "Feedback has been Updated"}, 201
        else:
            return {'message': 'The feedback entry does not yet exist'}, 404

    @add_tracker
    @jwt_protected

    def delete(self, _id=None):
        if _id is None:
            return {'message': 'Must specify id in the url to delete entry'}, 404
        feedback = db.session.query(Feedback).filter_by(id=_id).first()
        if not feedback:
            return {'message': 'The feedback entry does not yet exist'}, 404
        db.session.delete(feedback)
        db.session.commit()
        return {'message': "Feedback has been deleted"}, 204
