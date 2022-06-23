from flask_restful import Resource


class Smoke(Resource):
    def get(self):
        return {'message': 'All good here'}, 200
    