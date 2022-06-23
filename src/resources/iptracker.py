import requests
from src import db
from src.models import Tracker
from flask import request


def ip_tracker():
    """This part is intentionally added for Heroku"""
    response = request.headers.get('X-Forwarded-For', None)
    print('This is the real clients ip address --------', response)
    return response
    # response = requests.get('https://api64.ipify.org?format=json').json()
    # result = response.get("ip", None)
    # return result


def geo_request():
    ip_address = ip_tracker()
    if ip_address:
        url = 'http://ipwho.is/'
        request = requests.get(url + ip_address)
        return request.json()
    return False


def add_tracker(func):

    def get_geo_data(self, *args, **kwargs):
        json_response = geo_request()
        if not json_response:
            tracker = Tracker(ipaddress='Unknown', city='Unknown', country='Unknown')
            db.session.add(tracker)
            db.session.commit()
            print('Could not track user location')
        else:
            ipaddress = json_response.get('ip', 'Unknown')
            city = json_response.get('city', 'Unknown')
            country = json_response.get('country', 'Unknown')
            tracker = Tracker(ipaddress=ipaddress, city=city, country=country)
            db.session.add(tracker)
            db.session.commit()
            print('Tracker added...')
        return func(self, *args, **kwargs)

    return get_geo_data

