from flask import redirect
from flask_restful import Resource


class Index(Resource):
    """
    Doesn't do anything but redirect to make a homepage look pretty
    """
    def get(self):
        return redirect('/swagger')
    