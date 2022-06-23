from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import DatabaseError

from src import db
from src.models import Feedback
from src.resources.iptracker import add_tracker
from src.schemas import FeedbackSchema


class FeedbackApi(Resource):
    feedback_schema = FeedbackSchema()

    @add_tracker
    def get(self):
        feedback = db.session.query(Feedback).all()
        feedback_data = self.feedback_schema.dump(feedback, many=True)
        return feedback_data, 200

    @add_tracker
    def post(self):
        data = request.json
        # check if theres user_id/name or recipe_id/name in request and update those
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

    @add_tracker
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
    def delete(self, _id=None):
        if _id is None:
            return {'message': 'Must specify id in the url to delete entry'}, 404
        feedback = db.session.query(Feedback).filter_by(id=_id).first()
        if not feedback:
            return {'message': 'The feedback entry does not yet exist'}, 404
        db.session.delete(feedback)
        db.session.commit()
        return {'message': "Feedback has been deleted"}, 204
