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


def test_if_username_is_too_short(client):
    mongo = mongomock.MongoClient()
    db = mongo.testdb
    new_password = bcrypt.hashpw('testuser1'.encode('utf-8'),bcrypt.gensalt())
    new_username = 'tes'
    new_email = 'testuser1@test.com'
    users = db.users
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
        output = 'Username too short'
    assert output == 'Username too short'
    

def test_if_password_is_too_short(client):
    mongo = mongomock.MongoClient()
    db = mongo.testdb
    new_password = 'tes1'
    new_username = 'testuser1'
    new_email = 'testuser1@test.com'
    users = db.users
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
        output = 'password too short'
    assert output == 'password too short'
    
    
def test_get_category_id_for_rarity_and_types():
    def get_category_id(category_name, category):
        """ Comprehension function that returns id of each type or rarity card """
        if category == types:
            return [d['_id'] for d in types if d['type'] == category_name]
        elif category == rarity:
            return [d['_id'] for d in rarity if d['rarity'] == category_name]
    types = [{'_id': '1', 'type': 'land'}, {'_id': '2', 'type': 'creature'},
             {'_id': '3', 'type': 'artifact'}, {'_id': '4', 'type': 'enchantment'},
             {'_id': '5', 'type': 'planeswalker'}, {'_id': '6', 'type': 'instant'},
             {'_id': '7', 'type': 'sorcery'}]
    rarity = [{'_id': '11', 'rarity': 'land'}, {'_id': '12', 'rarity': 'common'},
              {'_id': '13', 'rarity': 'uncommon'}, {'_id': '14', 'rarity': 'rare'},
              {'_id': '15', 'rarity': 'mythic rare'}, {'_id': '16', 'rarity': 'timeshifted'},
              {'_id': '17', 'rarity': 'masterpiece'}]
    land_type = get_category_id('land', types)
    creature_type = get_category_id('creature', types)
    artifact_type = get_category_id('artifact', types)
    sorcery_type = get_category_id('sorcery', types)
    land = get_category_id('land', rarity)
    rare = get_category_id('rare', rarity)
    timeshifted = get_category_id('timeshifted', rarity)
    assert land_type == ['1']
    assert creature_type == ['2']
    assert artifact_type == ['3']
    assert sorcery_type == ['7']
    assert land == ['11']
    assert rare == ['14']
    assert timeshifted == ['16']
