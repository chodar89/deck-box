import os
import bcrypt
import numpy as np

from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_pymongo import PyMongo, pymongo
from flask_paginate import Pagination, get_page_parameter
from bson.objectid import ObjectId
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['MONGO_DBNAME'] = os.environ.get('MONGO_DBNAME')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')

mongo = PyMongo(app)

@app.context_processor
def user_context():
    """ Launched username before render templates """
    if 'userinfo' in session:
        user_name = session['userinfo'].get("username")
        user_email = session['userinfo'].get("email")
        sign_out = 'Sign Out'
        user_avatar = session['userinfo'].get("avatar")
        return dict(user_name=user_name.upper(), user_email=user_email,
                    sign_out=sign_out, user_avatar=user_avatar)
    else:
        return dict(user_name=None)

@app.route('/')
@app.route('/index')
def index():
    if 'userinfo' in session:
        return redirect(url_for('decks'))
    else:
        return render_template('index.html', sign_in='Sign In')

@app.route('/cards', methods=["POST", "GET"])
def my_cards():
    """
    Shows collection of all user cards plus pagination,
    Request number of cards to display per page from form.
    If user dont pick any, take number from database
    """
    if 'userinfo' in session:
        search = False
        q = request.args.get('q')
        if q:
            search = True
        page = request.args.get(get_page_parameter(), type=int, default=1)
        user_name = session['userinfo'].get("username")
        user = mongo.db.users.find_one({"username": user_name})
        user_id = ObjectId(session['userinfo'].get("id"))
        change_per_page = request.form.get('change_per_page')
        """ If user dont pick any, take number from database """
        if change_per_page != None:
            mongo.db.users.update({'username': user_name},
                                  {'$set': {'user_per_page':change_per_page}},
                                  multi=False)
            return redirect(url_for('cards'))
        if user['user_per_page'] == None:
            """ Prevents error if number is None and sert it to 20 """
            per_page = 20
        else:
            per_page = int(user['user_per_page'])
        user_pp = user['user_per_page']
        try:
            """ Try to find cards and count, if user dont have any gives 0 """
            user_cards = mongo.db.cards.find({'user_id': user_id})
            count_user_cards = user_cards.count()
        except:
            count_user_cards = 0
        card_output = []
        try:
            cards = mongo.db.cards.find(
                {'user_id': user_id}).sort('_id', pymongo.DESCENDING).skip((page - 1) * per_page).limit(per_page)
            for i in cards:
                card_output.append(i)
        except:
            flash('you do not have any cards in your collection yet', 'error')
        pagination = Pagination(page=page, per_page=per_page, total=count_user_cards,
                                search=search, record_name='card_output')
        return render_template('cards.html', card_output=card_output,
                               pagination=pagination, per_page=per_page)
    else:
        return redirect(url_for('register'))

@app.route('/cards/new_card', methods=['POST', 'GET'])
def new_card():
    """ 
    Render addcard page and take values from collection to form\
    when method is == to GET, when method is == POST
    insert card to database 
    """
    if 'userinfo' in session:
        if request.method == 'GET':
            colors = mongo.db.colors.find()
            rarity = mongo.db.rarity.find()
            expansion = mongo.db.expansion_set.find()
            card_types = mongo.db.card_types.find()
            rating = mongo.db.rating.find()
            return render_template('new_card.html', **locals())
        if request.method == 'POST':
            colors_id = []
            cards = mongo.db.cards
            colors_form = request.form.getlist('color')
            for i in colors_form:
                colors = ObjectId(i)
                colors_id.append(colors)
            rarity_form = request.form.get('rarity')
            expansion_form = request.form.get('set')
            type_form = request.form.get('type')
            user_id = ObjectId(session['userinfo'].get("id"))
            cards.insert_one({
                'card_name': request.form.get('card_name'),
                'color': colors_id,
                'rarity': ObjectId(rarity_form),
                'type': ObjectId(type_form),
                'set': ObjectId(expansion_form),
                'mana_cost': request.form.get('mana_cost'),
                'strength': request.form.get('strength'),
                'toughness': request.form.get('toughness'),
                'ruling': request.form.get('ruling'),
                'flavor_text': request.form.get('flavor_text'),
                'artist': request.form.get('artist'),
                'rating': request.form.get('rating'),
                'card_url': request.form.get('card_url'),
                'user_id': user_id
            })
            flash(f"Card {request.form.get('card_name')} added to your collection", "alert")
            return redirect(url_for('new_card'))
    else:
        return redirect(url_for('register'))

@app.route('/cards/<card_id>/edit_card', methods=["POST", "GET"])
def edit_card(card_id):
    """
    If method is GET than render form and takes values for card
    if method is POST takes values from form and update them
    in database
    """
    if 'userinfo' in session:
        if request.method == 'GET':
            card = mongo.db.cards.find_one({"_id": ObjectId(card_id)})
            colors = mongo.db.colors.find()
            rarity = mongo.db.rarity.find()
            expansion = mongo.db.expansion_set.find()
            card_types = mongo.db.card_types.find()
            rating = mongo.db.rating.find()
            card_color_id = card.get('color')
            return render_template('editcard.html', card=card, colors=colors,
                                   rarity=rarity, expansion=expansion, card_types=card_types,
                                   rating=rating, card_color_id=card_color_id)
        if request.method == 'POST':
            colors_id = []
            cards = mongo.db.cards
            colors_form = request.form.getlist('color')
            for i in colors_form:
                colors = ObjectId(i)
                colors_id.append(colors)
            rarity_form = request.form.get('rarity')
            expansion_form = request.form.get('set')
            type_form = request.form.get('type')
            user_id = ObjectId(session['userinfo'].get("id"))
            cards.update({"_id": ObjectId(card_id)}, {
                'card_name': request.form.get('card_name'),
                'color': colors_id,
                'rarity': ObjectId(rarity_form),
                'type': ObjectId(type_form),
                'set': ObjectId(expansion_form),
                'mana_cost': request.form.get('mana_cost'),
                'strength': request.form.get('strength'),
                'toughness': request.form.get('toughness'),
                'ruling': request.form.get('ruling'),
                'flavor_text': request.form.get('flavor_text'),
                'artist': request.form.get('artist'),
                'rating': request.form.get('rating'),
                'card_url': request.form.get('card_url'),
                'user_id': user_id})
            return redirect(url_for('my_cards'))
    else:
        return redirect(url_for('register'))

@app.route('/cards/<card_id>')
def remove_card(card_id):
    """ Removes document, card that user picked """
    user_id = ObjectId(session['userinfo'].get("id"))
    mongo.db.decks.update({'user_id': user_id},
                          {'$pull': {'cards':card_id}},
                          multi=True)
    card = mongo.db.cards.find_one({'_id': ObjectId(card_id)})
    flash(f"Card {card.get('card_name')} removed from your collection", "alert")
    mongo.db.cards.remove({'_id': ObjectId(card_id)})
    return redirect(url_for('my_cards'))

@app.route('/decks')
def decks():
    """ This is the home page after login, dispays all users decks """
    if 'userinfo' in session:
        user_id = ObjectId(session['userinfo'].get("id"))
        decks = mongo.db.decks.find({'user_id': user_id})
        return render_template('decks.html', decks=decks)
    else:
        return redirect(url_for('register'))

@app.route('/decks/<deck_id>')
def deck_browse(deck_id):
    if 'userinfo' in session:
        """
        Get all types and rarities collection and retrive id's.
        Than check each card in deck and count types and rarietes for
        later display.
        """
        cards = []
        count_lands = 0
        count_creatures = 0
        count_artifacts = 0
        count_enchantments = 0
        count_planeswalkers = 0
        count_instants = 0
        count_sorceries = 0
        color_name = []
        rarity_land = 0
        rarity_common = 0
        rarity_uncommon = 0
        rarity_rare = 0
        rarity_mythic = 0
        rarity_timeshifted = 0
        rarity_masterpiece = 0
        types = list(mongo.db.card_types.find())
        def type_id(type_name):
            """ Comprehension function that returns id of each type card """
            return [d['_id'] for d in types if d['type'] == type_name]
        land_type = type_id('land')
        creature_type = type_id('creature')
        artifact_type = type_id('artifact')
        enchantment_type = type_id('enchantment')
        planeswalker_type = type_id('planeswalker')
        instant_type = type_id('instant')
        sorcery_type = type_id('sorcery')
        rarity = list(mongo.db.rarity.find())
        def rarity_id(rarity_name):
            """ Comprehension function that returns id of each rarity card """
            return [d['_id'] for d in rarity if d['rarity'] == rarity_name]
        land = rarity_id('land')
        common = rarity_id('common')
        uncommon = rarity_id('uncommon')
        rare = rarity_id('rare')
        mythic = rarity_id('mythic rare')
        timeshifted = rarity_id('timeshifted')
        masterpiece = rarity_id('masterpiece')
        """ Check colors of deck that user browse """
        colors = list(mongo.db.colors.find())
        deck = mongo.db.decks.find_one({'_id': ObjectId(deck_id)})
        deck_color_id = deck.get('color')
        for color in deck_color_id:
            color_inf = [d['color'] for d in colors if d['_id'] == color]
            color_name.append(color_inf)
        """ Takes cards id from deck if empty throws None """
        try:
            deck_cards = deck["cards"]
        except:
            deck_cards = []
        count_cards = len(deck_cards)
        """ Find each card by id and check what type card it is and append it to array """
        if deck_cards != None:
            """ 
            Loop that check if card is in deck, if it is
            don't append, add amount to card.
            """
            for i in deck_cards:
                find_card = mongo.db.cards.find({'_id': ObjectId(i)})
                same_card = np.array(deck_cards)
                same_card_count = (same_card == i).sum()
                for each_card in find_card:
                    each_card["amount"] = same_card_count
                    if each_card not in cards:
                        cards.append(each_card)
            for card in deck_cards:
                card_information = mongo.db.cards.find_one({'_id': ObjectId(card)})
                card_type = [card_information["type"]]
                if card_type == land_type:
                    count_lands += 1
                elif card_type == creature_type:
                    count_creatures += 1
                elif card_type == artifact_type:
                    count_artifacts += 1
                elif card_type == enchantment_type:
                    count_enchantments += 1
                elif card_type == planeswalker_type:
                    count_planeswalkers += 1
                elif card_type == instant_type:
                    count_instants += 1
                elif card_type == sorcery_type:
                    count_sorceries += 1
            for card in deck_cards:
                card_information = mongo.db.cards.find_one({'_id': ObjectId(card)})
                card_rarity = [card_information["rarity"]]
                if card_rarity == land:
                    rarity_land += 1
                elif card_rarity == common:
                    rarity_common += 1
                elif card_rarity == uncommon:
                    rarity_uncommon += 1
                elif card_rarity == rare:
                    rarity_rare += 1
                elif card_rarity == mythic:
                    rarity_mythic += 1
                elif card_rarity == timeshifted:
                    rarity_timeshifted += 1
                elif card_rarity == masterpiece:
                    rarity_masterpiece += 1
        return render_template('deckbrowse.html', **locals())
    else: 
        return redirect(url_for('register'))

@app.route('/deck/new_deck', methods=['POST', 'GET'])
def new_deck():
    """ If method is POST insert deck to database else render new deck form """
    if 'userinfo' in session:
        if request.method == 'POST':
            """ Insert deck name to database """
            colors_id = []
            colors_form = request.form.getlist('color')
            for i in colors_form:
                colors = ObjectId(i)
                colors_id.append(colors)
            decks = mongo.db.decks
            user_id = ObjectId(session['userinfo'].get("id"))
            decks.insert_one({
                'deck_name': request.form.get('deck_name'),
                'color': colors_id,
                'user_id': user_id,
            })
            return redirect(url_for('decks'))
        if request.method == 'GET':
            colors = mongo.db.colors.find()
            return render_template('new_deck.html', colors=colors, sign_out='Sign Out')
    else:
        return redirect(url_for('register'))

@app.route('/decks/remove/<deck_id>')
def remove_deck(deck_id):
    """ Delete deck """
    deck = mongo.db.decks.find_one({'_id': ObjectId(deck_id)})
    flash(f"Deck {deck.get('deck_name')} removed from your collection", "alert")
    mongo.db.decks.remove({'_id': ObjectId(deck_id)})
    return redirect(url_for('decks'))

@app.route('/decks/deck_build/<deck_id>')
def deck_build(deck_id):
    """ Redirect page where user can add cards to specific deck """
    if 'userinfo' in session:
        deck = mongo.db.decks.find_one({'_id': ObjectId(deck_id)})
        user_id = ObjectId(session['userinfo'].get("id"))
        cards = mongo.db.cards.find({'user_id': user_id})
        return render_template('deckbuild.html', deck=deck, cards=cards)
    else:
        return redirect(url_for('register'))

@app.route('/decks/deck_build/<deck_id>/<card_id>', methods=['POST'])
def add_card_to_deck(deck_id, card_id):
    """ Add card to deck """
    if 'userinfo' in session:
        current_deck = mongo.db.decks.find_one({'_id': ObjectId(deck_id)})
        deck_id = current_deck.get('_id')
        deck_name = current_deck.get('deck_name')
        card = mongo.db.cards.find_one({'_id': ObjectId(card_id)})
        card_name = card.get('card_name')
        cards_amount = request.form.get('one_four_cards')
        """ Loop takes card amount from form and push cards to deck """
        for i in range(0, int(cards_amount)):
            deck = mongo.db.decks.update({'_id': ObjectId(deck_id)},
                                         {'$push': {'cards':card_id}})
        flash(f"Card {card_name} added to {deck_name} deck", "alert")
        return redirect(url_for('deck_build', deck_id=deck_id))
    else:
        return redirect(url_for('register'))

@app.route('/decks/deck_build/<deck_id>/<card_id>')
def remove_card_from_deck(deck_id, card_id):
    """ Remove card from deck """
    current_deck = mongo.db.decks.find_one({'_id': ObjectId(deck_id)})
    deck_id = current_deck.get('_id')
    deck_name = current_deck.get('deck_name')
    card = mongo.db.cards.find_one({'_id': ObjectId(card_id)})
    card_name = card.get('card_name')
    deck = mongo.db.decks.update({'_id': ObjectId(deck_id)},
                                 {'$pull': {'cards':card_id}})
    flash(f"Card {card_name} removed from {deck_name} deck", "alert")
    return redirect(url_for('deck_browse', deck_id=deck_id, card_id=card_id))

@app.route('/register', methods=['POST', 'GET'])
def register():
    """ Render register page and post registration form to mongo database """
    if 'userinfo' in session:
        return redirect(url_for('decks'))
    else:
        if request.method == 'POST':
            users = mongo.db.users
            new_username = request.form['username']
            new_password = request.form['password']
            email = request.form.get('email')
            existing_user = users.find_one({'username' : new_username.lower()})
            existing_email = users.find_one({'email': email.lower()})
            """
            First checks if username and emial exists in
            database if not post form if yes flash allert
            """
            if existing_user is None and existing_email is None:
                if len(new_username) < 4:
                    flash('Username to short', 'exists')
                elif len(new_password) < 6:
                    flash('password to short', 'exists')
                else:
                    hash_password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
                    users.insert({'username':new_username.lower(), 'password' : hash_password, 'email': email.lower(), 
                                  'avatar': request.form['avatar'], 'user_per_page': 10})
                    flash('Thank you for creating an account', 'exists')
                return redirect(url_for('register'))
            else: flash('Username or email already exists', 'exists')
        return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    """ Login form, encode and checks data in form with database that exists if not flash allert """
    users = mongo.db.users
    log_username = request.form['log_username']
    username = users.find_one({'username': log_username.lower()})
    if username:
        if bcrypt.hashpw(request.form['log_password'].encode('utf-8'), username['password']) == username['password']:
            session['userinfo'] = {'username': username.get('username'), 'id': str(username.get('_id')), 
                                   'email': username.get('email'), 'avatar': username.get('avatar')}
            flash(f"Welcome back {session['userinfo'].get('username')}", "welcome")
            return redirect(url_for('decks'))
    flash("Incorrect password or username", "error")
    return redirect(url_for('register'))

@app.route('/logout')
def logout():
    """ Simply logout session function """
    session.pop('userinfo')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.secret_key = os.environ.get('key')
    app.run(host=os.environ.get("IP", "0.0.0.0"),
            port=int(os.environ.get("PORT", "5000")),
            debug=os.environ.get('debug'))
