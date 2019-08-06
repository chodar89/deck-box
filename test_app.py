import os
import pytest
import mongomock
import bcrypt

from flask import url_for

from app import login, logout, deck_browse
from app import app as create_app



@pytest.fixture
def app():
    app = create_app
    return app



def test_register_the_same_user_should_refuse(client):
    mongo = mongomock.MongoClient()
    db = mongo.testdb
    new_password = bcrypt.hashpw('testuser1'.encode('utf-8'),bcrypt.gensalt())
    new_username = 'testuser1'
    new_email = 'testuser1@test.com'
    users = db.users
    users.insert_one({'username': new_username,
                     'password': new_password,
                     'email': new_email})
    existing_user = users.find_one({'username' : new_username.lower()})
    existing_email = users.find_one({'email': new_email.lower()})
    if existing_user is None and existing_email is None:
        if len(new_username) < 4:
            output = 'Username too short'
        elif len(new_password) < 6:
            output = 'password too short'
        else:
            users.insert({'username':new_username.lower(), 'password' : new_password,
                          'email': new_email.lower()})
            output = 'Thank you for creating an account'
    else:
        output = 'Username or email already exists'
    assert output == 'Username or email already exists'
