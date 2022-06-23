from flask import request
from flask_restful import Resource

from src.resources.authentication import jwt_protected


class Smoke(Resource):
    @jwt_protected
    def get(self):
        print(request.headers.get('Authorization'))
        return {'message': 'All good here'}, 200
    