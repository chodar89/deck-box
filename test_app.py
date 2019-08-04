import pytest
import os
from app import app as create_app
from flask import url_for


@pytest.fixture
def app():
    app = create_app
    return app
    

def test_urls(client):
    assert client.get(url_for('index')).status_code == 200
    assert client.get(url_for('register')).status_code == 200


def test_redirect_when_user_is_not_loged(client):
    assert client.get(url_for('my_cards')).status_code == 302
    assert client.get(url_for('new_card')).status_code == 302

    