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


@app.before_request
def before_request():
    """
    Check if user is not in session, and redirect user
    to register page if URL is endpoint is diferent than,
    login, register or index
    """
    if 'userinfo' not in session and request.endpoint not in (
            'index', 'register', 'login', 'static'):
        return redirect(url_for('register'))


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
    elif 'userinfo' not in session:
        return dict(user_name=None)

@app.errorhandler(404)
@app.errorhandler(401)
@app.errorhandler(500)
def not_found_error(error):
    """Render error page"""
    return render_template('error.html')


@app.route('/')
@app.route('/index', endpoint='index')
def index():
    """ Render index template, if user logged go to decks.html """
    if 'userinfo' in session:
        return redirect(url_for('my_decks'))
    elif 'userinfo' not in session:
        return render_template('index.html', sign_in='Sign In')


@app.route('/cards', methods=["POST", "GET"])
def my_cards():
    """
    Shows collection of all user cards plus pagination,
    Request number of cards to display per page from form.
    If user dont pick any, take number from database
    """
    search = False
    q = request.args.get('q')
    if q:
        search = True
    page = request.args.get(get_page_parameter(), type=int, default=1)
    user_name = session['userinfo'].get("username")
    user = mongo.db.users.find_one({"username": user_name})
    user_id = ObjectId(session['userinfo'].get("id"))
    if request.method == "POST":
        # If method is POST take number of cards to display from form
        change_per_page = request.form.get('change_per_page')
        mongo.db.users.update({'username': user_name},
                              {'$set': {'user_per_page':change_per_page}},
                              multi=False)
        return redirect(url_for('my_cards'))
    if user['user_per_page'] is None:
        # Prevents error if number is None and set it to 20,
        # for user that created accounts before this feature
        per_page = 20
    else:
        per_page = int(user['user_per_page'])
    user_cards = mongo.db.cards.find({'user_id': user_id})
    if user_cards is None:
        count_user_cards = 0
    else:
        count_user_cards = user_cards.count()
    card_output = []
    try:
        cards = mongo.db.cards.find(
            {'user_id': user_id}).sort('_id', pymongo.DESCENDING).skip(
                (page - 1) * per_page).limit(per_page)
        for card in cards:
            card_output.append(card)
    except:
        flash('you do not have any cards in your collection yet', 'error')
    pagination = Pagination(page=page, per_page=per_page, total=count_user_cards,
                            search=search, record_name='card_output')
    return render_template('cards.html', card_output=card_output,
                           pagination=pagination, per_page=per_page)


@app.route('/cards/new', methods=['POST', 'GET'])
def new_card():
    """
    Render addcard page and take values from collection to form\
    when method is == to GET, when method is == POST
    insert card to database
    """
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
        for color in colors_form:
            colors_id.append(ObjectId(color))
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


@app.route('/cards/<card_id>/edit', methods=["POST", "GET"])
def edit_card(card_id):
    """
    If method is GET than render form and takes values for card
    if method is POST takes values from form and update them
    in database
    """
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
        for color in colors_form:
            colors_id.append(ObjectId(color))
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
def my_decks():
    """ This is the home page after login, dispays all users decks """
    user_id = ObjectId(session['userinfo'].get("id"))
    decks = mongo.db.decks.find({'user_id': user_id})
    return render_template('decks.html', decks=decks)


@app.route('/decks/<deck_id>')
def deck_browse(deck_id):
    """
    Get all types and rarities collection and retrive id's.
    Than check each card in deck and count types and rarietes for
    later display.
    """
    cards = []
    color_name = []
    types = list(mongo.db.card_types.find())
    def get_category_id(category_name, category):
        """ Comprehension function that returns id of each type or rarity card """
        if category == types:
            return [d['_id'] for d in types if d['type'] == category_name]
        elif category == rarity:
            return [d['_id'] for d in rarity if d['rarity'] == category_name]
    land_type = get_category_id('land', types)
    creature_type = get_category_id('creature', types)
    artifact_type = get_category_id('artifact', types)
    enchantment_type = get_category_id('enchantment', types)
    planeswalker_type = get_category_id('planeswalker', types)
    instant_type = get_category_id('instant', types)
    sorcery_type = get_category_id('sorcery', types)
    rarity = list(mongo.db.rarity.find())
    land = get_category_id('land', rarity)
    common = get_category_id('common', rarity)
    uncommon = get_category_id('uncommon', rarity)
    rare = get_category_id('rare', rarity)
    mythic = get_category_id('mythic rare', rarity)
    timeshifted = get_category_id('timeshifted', rarity)
    masterpiece = get_category_id('masterpiece', rarity)
    #  Check colors of deck that user browse
    colors = list(mongo.db.colors.find())
    deck = mongo.db.decks.find_one({'_id': ObjectId(deck_id)})
    deck_color_id = deck.get('color')
    for color in deck_color_id:
        color_inf = [d['color'] for d in colors if d['_id'] == color]
        color_name.append(color_inf)
    deck_cards = deck["cards"]
    count_cards = len(deck_cards)
    #  Find each card by id and check what type card it is and append it to array
    if deck_cards != None:
        # Loop that check if card is in deck, if it is
        # don't append, add amount to card.
        card_type_and_rarity = []
        for card in deck_cards:
            find_card = mongo.db.cards.find({'_id': ObjectId(card)})
            same_card = np.array(deck_cards)
            same_card_count = (same_card == card).sum()
            for each_card in find_card:
                each_card["amount"] = same_card_count
                card_type_and_rarity.append([each_card["type"]])
                card_type_and_rarity.append([each_card["rarity"]])
                if each_card not in cards:
                    cards.append(each_card)
        class LandsRarities:
            """
            Hold var for types and rarity count and pass
            to javascript and html by jinja
            """
            count_lands = 0
            count_creatures = 0
            count_artifacts = 0
            count_enchantments = 0
            count_planeswalkers = 0
            count_instants = 0
            count_sorceries = 0
            rarity_land = 0
            rarity_common = 0
            rarity_uncommon = 0
            rarity_rare = 0
            rarity_mythic = 0
            rarity_timeshifted = 0
            rarity_masterpiece = 0
        def deck_cards_type_and_rarity(type_or_rarity):
            """Check each card from deck and count its rarity and type"""
            for each in type_or_rarity:
                if each == land_type:
                    LandsRarities.count_lands += 1
                elif each == creature_type:
                    LandsRarities.count_creatures += 1
                elif each == artifact_type:
                    LandsRarities.count_artifacts += 1
                elif each == enchantment_type:
                    LandsRarities.count_enchantments += 1
                elif each == planeswalker_type:
                    LandsRarities.count_planeswalkers += 1
                elif each == instant_type:
                    LandsRarities.count_instants += 1
                elif each == sorcery_type:
                    LandsRarities.count_sorceries += 1
                elif each == land:
                    LandsRarities.rarity_land += 1
                elif each == common:
                    LandsRarities.rarity_common += 1
                elif each == uncommon:
                    LandsRarities.rarity_uncommon += 1
                elif each == rare:
                    LandsRarities.rarity_rare += 1
                elif each == mythic:
                    LandsRarities.rarity_mythic += 1
                elif each == timeshifted:
                    LandsRarities.rarity_timeshifted += 1
                elif each == masterpiece:
                    LandsRarities.rarity_masterpiece += 1
        deck_cards_type_and_rarity(card_type_and_rarity)
    return render_template('deckbrowse.html', LandsRarities=LandsRarities, deck=deck,
                           count_cards=count_cards, color_name=color_name, cards=cards)


@app.route('/deck/new', methods=['POST', 'GET'])
def new_deck():
    """ If method is POST insert deck to database else render new deck form """
    if request.method == 'POST':
        colors_id = []
        colors_form = request.form.getlist('color')
        for color in colors_form:
            colors = ObjectId(color)
            colors_id.append(colors)
        decks = mongo.db.decks
        user_id = ObjectId(session['userinfo'].get("id"))
        decks.insert_one({
            'deck_name': request.form.get('deck_name'),
            'color': colors_id,
            'user_id': user_id,
            'cards': []
        })
        return redirect(url_for('my_decks'))
    if request.method == 'GET':
        colors = mongo.db.colors.find()
        return render_template('new_deck.html', colors=colors, sign_out='Sign Out')


@app.route('/decks/remove/<deck_id>')
def remove_deck(deck_id):
    """ Delete deck """
    deck = mongo.db.decks.find_one({'_id': ObjectId(deck_id)})
    flash(f"Deck {deck.get('deck_name')} removed from your collection", "alert")
    mongo.db.decks.remove({'_id': ObjectId(deck_id)})
    return redirect(url_for('my_decks'))


@app.route('/decks/deck_build/<deck_id>')
def deck_build(deck_id):
    """ Redirect page where user can add cards to specific deck """
    deck = mongo.db.decks.find_one({'_id': ObjectId(deck_id)})
    user_id = ObjectId(session['userinfo'].get("id"))
    cards = mongo.db.cards.find({'user_id': user_id})
    return render_template('deckbuild.html', deck=deck, cards=cards)


@app.route('/decks/deck_build/<deck_id>/<card_id>', methods=['POST'])
def add_card_to_deck(deck_id, card_id):
    """ Add card to deck """
    current_deck = mongo.db.decks.find_one({'_id': ObjectId(deck_id)})
    deck_id = current_deck.get('_id')
    deck_name = current_deck.get('deck_name')
    card = mongo.db.cards.find_one({'_id': ObjectId(card_id)})
    card_name = card.get('card_name')
    cards_amount = request.form.get('one_four_cards')
    #  Loop takes card amount from form and push cards to deck
    for i in range(0, int(cards_amount)):
        mongo.db.decks.update({'_id': ObjectId(deck_id)},
                              {'$push': {'cards':card_id}})
    flash(f"Card {card_name} added to {deck_name} deck", "alert")
    return redirect(url_for('deck_build', deck_id=deck_id))


@app.route('/decks/deck_build/<deck_id>/<card_id>')
def remove_card_from_deck(deck_id, card_id):
    """ Remove card from deck """
    current_deck = mongo.db.decks.find_one({'_id': ObjectId(deck_id)})
    deck_id = current_deck.get('_id')
    deck_name = current_deck.get('deck_name')
    card = mongo.db.cards.find_one({'_id': ObjectId(card_id)})
    card_name = card.get('card_name')
    mongo.db.decks.update({'_id': ObjectId(deck_id)},
                          {'$pull': {'cards':card_id}})
    flash(f"Card {card_name} removed from {deck_name} deck", "alert")
    return redirect(url_for('deck_browse', deck_id=deck_id, card_id=card_id))


@app.route('/register', methods=['POST', 'GET'], endpoint='register')
def register():
    """ Render register page and post registration form to mongo database """
    if 'userinfo' in session:
        return redirect(url_for('my_decks'))
    else:
        if request.method == 'POST':
            users = mongo.db.users
            new_username = request.form['username']
            new_password = request.form['password']
            new_email = request.form.get('email')
            existing_user = users.find_one({'username' : new_username.lower()})
            existing_email = users.find_one({'email': new_email.lower()})
            # First checks if username and emial exists in
            # database if not post form if yes find user in database hold in session
            # and redirect user to my_decks page
            if existing_user is None and existing_email is None:
                if len(new_username) < 4:
                    flash('Username too short', 'exists')
                elif len(new_password) < 6:
                    flash('password too short', 'exists')
                else:
                    hash_password = bcrypt.hashpw(
                        request.form['password'].encode('utf-8'), bcrypt.gensalt())
                    users.insert_one({'username':new_username.lower(), 'password' : hash_password,
                                  'email': new_email.lower(), 'avatar': request.form['avatar'],
                                  'user_per_page': 10})
                    user = users.find_one({'username': new_username.lower()})
                    session['userinfo'] = {'username': user.get('username'),
                                           'id': str(user.get('_id')),
                                           'email': user.get('email'), 'avatar': user.get('avatar')}
                    flash('Thank you for creating an account', 'alert')
                return redirect(url_for('my_decks'))
            else:
                flash('Username or email already exists', 'exists')
        return render_template('register.html')


@app.route('/login', methods=['POST'], endpoint='login')
def login():
    """ Login form, encode and checks data in form with database that exists if not flash allert """
    users = mongo.db.users
    log_username = request.form['log_username']
    user = users.find_one({'username': log_username.lower()})
    if user:
        if bcrypt.hashpw(request.form['log_password'].encode('utf-8'),
                         user['password']) == user['password']:
            session['userinfo'] = {'username': user.get('username'),
                                   'id': str(user.get('_id')),
                                   'email': user.get('email'), 'avatar': user.get('avatar')}
            flash(f"Welcome back {session['userinfo'].get('username')}", "welcome")
            return redirect(url_for('my_decks'))
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
