import os
import pytest
import bcrypt

from flask import url_for, session

from app import app as create_app

from dotenv import load_dotenv

load_dotenv()

@pytest.fixture
def app():
    app = create_app
    app.secret_key = os.environ.get('key')
    return app


def test_urls_when_user_not_in_session(client):
    card_id = []
    deck_id = []
    assert client.get(url_for('index')).status_code == 200
    assert client.get(url_for('register')).status_code == 200
    assert client.get(url_for('my_cards')).status_code == 302
    assert client.get(url_for('new_card')).status_code == 302
    assert client.get(url_for('edit_card', card_id=card_id)).status_code == 302
    assert client.get(url_for('remove_card', card_id=card_id)).status_code == 302
    assert client.get(url_for('my_cards')).status_code == 302
    assert client.get(url_for('my_decks')).status_code == 302
    assert client.get(url_for('deck_browse', deck_id=deck_id)).status_code == 302
    assert client.get(url_for('new_deck')).status_code == 302
    assert client.get(url_for('remove_deck', deck_id=deck_id)).status_code == 302
    assert client.get(url_for('deck_build', deck_id=deck_id)).status_code == 302
    assert client.get(url_for('add_card_to_deck', deck_id=deck_id, card_id=card_id)).status_code == 302
    assert client.get(url_for('remove_card_from_deck', deck_id=deck_id, card_id=card_id)).status_code == 302


def test_urls_when_user_in_session(client):
    card_id = []
    deck_id = []
    with client.session_transaction() as session:
        session['userinfo'] = {'username': 'testuser'}
    assert client.get(url_for('index')).status_code == 302
    assert client.get(url_for('register')).status_code == 302
    assert client.get(url_for('my_cards')).status_code == 200
    assert client.get(url_for('new_card')).status_code == 200
    assert client.get(url_for('edit_card', card_id=card_id)).status_code == 200
    assert client.get(url_for('remove_card', card_id=card_id)).status_code == 200
    assert client.get(url_for('my_cards')).status_code == 200
    assert client.get(url_for('my_decks')).status_code == 200
    assert client.get(url_for('deck_browse', deck_id=deck_id)).status_code == 200
    assert client.get(url_for('new_deck')).status_code == 200
    assert client.get(url_for('remove_deck', deck_id=deck_id)).status_code == 200
    assert client.get(url_for('deck_build', deck_id=deck_id)).status_code == 200
    assert client.get(url_for('add_card_to_deck', deck_id=deck_id, card_id=card_id)).status_code == 200
    assert client.get(url_for('remove_card_from_deck', deck_id=deck_id, card_id=card_id)).status_code == 200
