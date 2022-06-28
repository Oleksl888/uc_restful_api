import json

import pytest
from src import app

# Creating a test client for application
app.testing = True
client = app.test_client()


# Fixture that will apply endpoints in params to the test cases in get requests
@pytest.fixture(scope='function', params=[
    '/recipes',
    '/ingredients',
    '/feedback',
    '/users',
    '/tracker',
    '/',
    '/register',
    '/login'
])
def setup_get(request):
    endpoints = request.param
    return endpoints


@pytest.fixture(scope='function', params=[
    '/recipes',
    '/ingredients',
    '/feedback',
    '/users',
    '/tracker',
    '/',
    '/register',
    '/login'
])
def setup_post(request):
    endpoints = request.param
    return endpoints


# Fixture that will apply endpoints in params to the test cases in post requests
def test_endpoints_with_get(setup_get):
    resp = client.post(setup_get)
    # print(resp.status_code)
    # print(resp.content_type)
    # print(resp.json)
    assert resp.status_code == 200
    assert resp.status_code == 302
    assert resp.status_code == 405
    assert resp.status_code == 401


def test_endpoints_with_post(setup_post):
    resp = client.post(setup_post)
    # print(resp.status_code)
    # print(resp.content_type)
    # print(resp.json)
    assert resp.status_code == 200


def test_register_with_post():
    resp = client.post('/register',
                       data=json.dumps(
                           dict(
                               name='alexa',
                               email='alex@mail.com',
                               password='12345678')
                       ),
                       content_type='application/json'
                       )
    print(resp.status_code)
    print(resp.content_type)
    print(resp.json)
    assert resp.status_code == 201


def test_login_with_post():
    resp = client.post('/login',
                       data=json.dumps(
                           dict(
                               name='alexa',
                               password='12345678')
                       ),
                       content_type='application/json'
                       )
    print(resp.status_code)
    print(resp.content_type)
    print(resp.json)
    assert resp.status_code == 200
